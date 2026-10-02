# Complexity causal-convolution → vLLM adaptation

## Source locations

- Complexity model: `~/Dev/complexity-framework`
- vLLM fork: `~/Dev/vllm-cuda_graph`
- Historical QKV backend (reference only): `vllm/model_executor/models/pacific_i64.py`
- Fixed-state scheduler references: `vllm/v1/worker/mamba_utils.py`, `vllm/v1/attention/backends/mamba_attn.py`, and `vllm/model_executor/layers/mamba/`

## Canonical contract

The canonical model is not Mamba. It is a width-384, ten-layer stack of explicit depthwise causal dilated convolutions plus lexical objects and deterministic micro-experts. Dilations are `[1,2,4,8,16,32,64,128,1,2]`, kernel size 4, receptive field 775, and there are no QKV projections, attention softmax, selective scan, attention matrix, or growing KV cache.

Checkpoint formula for each mixer is exactly:

```text
mixed = depthwise_causal_conv(x)
y = o_proj(silu(gate_proj(mixed)) * up_proj(mixed))
```

Do not place `up_proj` before the convolution. A self-consistent full/decode test can miss that error; always compare against the reference framework or real checkpoint.

Lexical MLP formula:

```text
shared = shared_down(silu(shared_gate(x)) * shared_up(x))
object = object_down(silu(object_up(x)) * (1 + token_scale[token]))
micro = deterministic top-1 token-indexed narrow expert residual
```

Preserve checkpoint parameter names and require strict loading.

## Ring-state design

For direct circular storage that includes the current sample, the minimum ring length is:

```text
1 + (kernel_size - 1) * dilation
```

Thus the maximum layer needs 385 entries at dilation 128. Alternatively, a 384-entry past-only ring is valid only if all historical reads occur before the current write and the current contribution is handled separately. Never write current into a 384 ring before reading offset 384: it aliases and destroys the oldest needed sample.

Use a uniform maximum shape for all layers because current vLLM `MambaSpec` grouping requires equal state specs. Derive write/read slots from absolute device positions; never maintain Python cursors.

Padding rows require an explicit safe reserved state slot or a masked custom kernel. Merely clamping `PAD_SLOT_ID=-1` to a real slot can collide with an active request under CUDA Graph batching.

## vLLM integration

Create a distinct architecture, e.g. `PacificDilatedConvForCausalLM`, and a backend named `dilated_conv`. Reuse `MambaSpec` and `BaseMambaAttentionMetadataBuilder` only as generic fixed-inner-state scheduler plumbing; do not label the model itself Mamba.

Initial scope:

- TP=1;
- prefix cache mode `none` or carefully tested `align`;
- no speculative decoding;
- decode CUDA Graph first;
- prefill may start with a correct eager sequential implementation, then move to a Triton kernel.

Required tests:

1. framework full-forward vs new full-forward;
2. framework full-forward vs incremental decode beyond dilation-128 wraparound;
3. real checkpoint MLP and mixer exactness;
4. mixed state-slot ordering;
5. reset/reuse and no request leakage;
6. padding-state non-mutation;
7. scheduler state copy/migration;
8. eager vs CUDA Graph replay with different slots;
9. OpenAI API generation.

## Checkpoint and tokenizer packaging

Strip optimizer/scheduler state before transfer. Save `config.json` plus `model.safetensors`; record SHA-256 locally and remotely before deleting or stopping the GPU instance.

An unknown Transformers `model_type` may fail before vLLM resolves the custom `architectures` entry. A known HF config class can be used strictly as a configuration container while retaining `architectures: [PacificDilatedConvForCausalLM]` and all custom fields.

`o200k_base` can be converted with `transformers.integrations.tiktoken.convert_tiktoken_to_fast`. Validate exact token IDs against tiktoken on multilingual text, code, and emoji. `PreTrainedTokenizerFast.vocab_size` may omit reserved-ID gaps even though the model head remains 200,019.

## Build and cost discipline

The release `v0.2.0` wheel (`cp312`, Linux x86_64) is a binary reference, not editable source. Use a source checkout and `VLLM_USE_PRECOMPILED=1` editable install to iterate against existing CUDA extensions; rebuild the final wheel on H100 only after Python/model equivalence passes.

On paid accelerators, parallelize remote environment setup/export with local coding. Archive compact inference artifacts and metrics early, checksum them, and explicitly tell the user when the instance can stop. Do not keep H100 idle during local-only work.

Never claim CUDA Graph compatibility until real H100 capture and repeated replay pass with stable pointers and matching outputs.
