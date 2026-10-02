# Attention-free LLM architecture validation

Use this checklist when replacing Transformer attention with convolutional or recurrent sequence mixers while preserving causal-LM behavior and deployment viability.

## Architectural contract

- Define the model as a causal sequence function, not merely “Transformer minus QKV.”
- State separately: local mixer, persistent state, shared channel path, lexical conditioning, conditional residual, and LM head.
- Keep QKV/Transformer implementations as matched controls unless deletion is explicitly requested.
- Verify the target model instantiates zero `q_proj`, `k_proj`, and `v_proj` parameter tensors.

## Training validation

1. Write a strict causality test: changing future tokens must not change prefix outputs.
2. Match total parameters before comparing loss or throughput.
3. Compare same tokenizer, data stream, seed, batch, sequence length, optimizer, schedule, and token budget.
4. Run a short throughput gate before the full diagnostic.
5. Verify backward reaches every new controller/state parameter.
6. Test higher-order scan/compile primitives under the actual device, dtype, and autocast context. A primitive working in a tiny FP32 probe does not establish production-training compatibility.
7. Prefer a tensorized closed form for diagonal recurrences when it is numerically safe; keep persistent state in FP32 if long-horizon accumulation matters.

## Inference contract

- Separate parallel prefill from `[B, 1, D]` decode.
- Allocate fixed-size per-layer state; do not grow or concatenate an unbounded history.
- Test full-sequence logits against token-by-token cached logits with explicit tolerances.
- Under inference/no-grad, update state in place and assert cache pointers remain stable.
- Measure state elements and bytes per sequence.
- Benchmark cached decode against full-prefix recomputation using the real vocabulary projection.

## CUDA Graph claim ladder

Use precise labels:

1. **Graph-friendly by design**: static shapes/control flow, no `.item()`, no data-dependent Python routing.
2. **Pointer-stable decode**: preallocated state updated in place.
3. **Capture-tested**: real `torch.cuda.CUDAGraph` capture succeeds on the target CUDA stack.
4. **Replay-verified**: repeated graph replays match eager logits and state updates.
5. **Deployment-validated**: measured prefill/decode latency and memory at target batch/context buckets.

Never jump from step 1 or 2 to “CUDA Graph compatible.” CUDA Graph requires real capture and replay evidence on CUDA.

## Interpreting local versus persistent memory

A persistent state cannot show unique value when the local mixer’s receptive field already covers the entire training sequence. Evaluate it at contexts longer than the local receptive field. Keep the simpler local model canonical until the persistent-state variant wins on an experiment where long memory is actually needed.

## Reporting

Report implemented behavior, measured results, and remaining deployment assumptions separately. Small single-seed runs are architecture diagnostics, not general superiority claims.
