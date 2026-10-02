# Native causal-choice evaluation: TR-Hash / PIQA pattern

Use this pattern when a custom causal LM must be evaluated through its production/native inference engine rather than its training framework.

## Protocol checklist

1. Resolve the exact model artifact. For Hugging Face, inspect repository metadata first, pin the immutable commit SHA, and download only the canonical config, weights, tokenizer metadata, and model card needed for evaluation.
2. Hash the downloaded weights and benchmark archive. Record byte size and source paths.
3. Inspect tokenizer special tokens and IDs before scoring. A reserved token's existence is not authorization to inject it.
4. For raw base/refinement PIQA, encode goals and both continuations with `add_special_tokens=False`; do not apply a chat template, prepend BOS/begin, or silently fall back to BOS for empty contexts. Fail closed if a context is empty or any reserved special ID occurs.
5. Score both answer choices by causal continuation log-likelihood. Report:
   - raw accuracy from summed continuation log-likelihood;
   - normalized accuracy from mean continuation log-likelihood per continuation token;
   - correct counts, total examples, total choices, and total continuation tokens.
6. Run the complete validation split for a final score. PIQA validation has 1,838 examples and 3,676 choices; tiny subsets are functional/performance smokes only.
7. Save a machine-readable artifact with the exact first encoding and a small prediction sample so token-boundary errors remain auditable.

## TR-Hash-i64 loader adaptation

A Hugging Face config may be canonical for training/Transformers but need compatibility fields for the inference loader. Preserve the downloaded config and create a separate temporary engine directory containing symlinks to the canonical weight/tokenizer plus an adapted config.

For the 100M TR-Hash layout observed in September 2026:

- omit explicit `head_dim` from the engine copy when the config class exposes it as a derived read-only property;
- map `shared_intermediate_size` to the loader's `intermediate_size` alias;
- map `num_experts_per_tok` to `top_k`;
- preserve all topology and routing values unchanged.

Document these as loader compatibility adaptations, not changes to the model's canonical architecture.

## Native engine scoring shape

Instantiate the real engine and use its paged state/KV contract. A practical PIQA scorer can:

- prefill each goal through the engine model with the engine-owned paged cache;
- select only last-context logits when the model supports `logits_indices`;
- teacher-force continuation tokens through `decode_step` while accumulating target log-probabilities;
- free each sequence's cache blocks after the batch.

This is a native-engine evaluation even though scoring requires explicit teacher-forcing control instead of ordinary free generation.

### Repeated synchronous generation pitfall

In the TR-Hash-i64 revision observed (`ec1f96c7e0828f2188030f5eb2423d3e15ab18ce`), `generate()` returned while the finished request remained visible until the next engine step. With `max_batch_size=1`, immediately adding a second request could raise `No KV cache slots available`. Advancing one cleanup `step()` after consuming each finished result was verified to release the slot. Re-check current engine behavior before applying this workaround because the engine may later fix finalization internally.

## Interpreting speed

Full PIQA does not produce one token per question. It scores every token in both candidate continuations. Therefore always report examples, choices, continuation-token count, elapsed time, and continuation tokens/s. On Apple MPS, eager paged decode can take several minutes even for a 100M model; CUDA/CUDA Graph results are a different backend and require a matched rerun before claiming a speedup.

Do not take GPUs from a live DDP training run for convenience. Inspect active processes and accelerator utilization first; evaluate locally or on separate capacity when training is active.
