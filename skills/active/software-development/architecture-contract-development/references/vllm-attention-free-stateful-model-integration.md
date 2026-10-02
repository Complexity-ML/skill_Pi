# vLLM Attention-Free Stateful Model Integration

Use this checklist when adding a decoder-only vLLM model whose sequence mixer owns fixed-size per-request state rather than an attention KV cache.

## Architecture contract

- Make the top-level causal LM inherit `HasInnerState`, `IsAttentionFree`, and `SupportsPP` when applicable.
- Keep forbidden transformer surfaces absent from both implementation and checkpoint-facing names: no QKV projections, RoPE, or `Attention` construction.
- Reuse the existing stateful mixer and domain MLP rather than recreating either inside the model file.
- Preserve canonical checkpoint module names (`model.embed_tokens`, `model.layers.N.input_layernorm`, `self_attn`, `post_attention_layernorm`, `mlp`, final norm, and `lm_head`).

## vLLM interfaces

- Follow Mamba-family top-level contracts for `scheduler_config`, `model_config`, `make_empty_intermediate_tensors`, CUDA-graph input delegation, state dtype, and state shape.
- Use `VocabParallelEmbedding`, `ParallelLMHead`, and `LogitsProcessor` where compatible. If an inner layer is explicitly TP=1, reject larger TP at model construction rather than exposing partially parallelized embeddings.
- For tied embeddings, tie the parallel LM head to the input embedding and map checkpoint `lm_head.weight` to the canonical embedding parameter during loading.
- State shape returned by the model must exactly match the state tuple exposed by every mixer layer, including dimension order.

## Pipeline-parallel token routing

Token-conditioned MLPs need token IDs on every PP rank. `IntermediateTensors` transport commonly allocates homogeneous 2-D buffers shaped like hidden states. If no dedicated integer side channel exists:

1. Allocate a PP field for routing IDs with the same 2-D shape/dtype as hidden states.
2. Pack each token ID across columns before returning intermediate tensors.
3. Recover one column and cast to `long` on the receiving stage.
4. Test this packing contract explicitly; do not assume `input_ids` is supplied to non-first PP ranks.

This is transport compatibility, not model routing logic; keep it localized to the model wrapper.

## Exact weight loading

- Build both `named_parameters()` and `named_buffers()` maps: deterministic routing tables may be persistent buffers present in checkpoints.
- Normalize only documented outer-prefix and tied-embedding cases.
- Load every other key by exact dictionary lookup so architectural drift fails closed rather than logging and skipping unknown projections.
- Respect `is_pp_missing_parameter` before lookup.
- Use each parameter's custom `weight_loader` when present; copy persistent buffers directly.
- Do not add projection packing/remapping when the checkpoint already uses exact canonical names.

## Focused verification

When full model imports require unavailable native/runtime dependencies, a focused AST/source contract test can still guard:

- required interfaces and required mixer/MLP construction;
- absence of QKV/RoPE/Attention surfaces;
- checkpoint-facing attribute names;
- fail-closed exact lookup in `load_weights`.

Also run syntax compilation and whitespace checks. Clearly distinguish these contract checks from full runtime model tests; do not imply end-to-end vLLM execution occurred.