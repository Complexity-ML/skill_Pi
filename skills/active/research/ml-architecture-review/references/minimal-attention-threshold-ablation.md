# Minimal-attention threshold ablations

Use this protocol when an attention-free recurrent/conv model is close to an attention control but still lacks instance-selective retrieval.

## Source-first identification

Before naming the fastest or best model, read the actual paper table and raw CSVs. Never infer which row produced a remembered throughput number. Record separately:

- best held-out loss;
- fastest attention-free throughput;
- dense-attention control throughput;
- exact parameter/token/optimizer schedule.

Historical absolute throughput and a new runtime smoke are not directly comparable. Measure candidate and canonical control back-to-back in the same environment, then report relative overhead. Preserve the archived number only as historical evidence.

## Restore, then vary one thing

1. Stop rejected paid-GPU jobs immediately and verify VRAM is released.
2. Restore the exact canonical baseline that is closest to the quality control—not a worktree containing several selectable experimental memories.
3. Remove or disconnect rejected routed/augmented variants and their CLI/config/tests before benchmarking.
4. Re-run focused correctness tests and a short matched throughput control.
5. Add exactly one attention layer or branch; keep data, token budget, optimizer, seed, parameter count, and evaluation cadence matched.
6. A short proxy is a catastrophe/stability screen only. It must not rank candidates when prior proxies failed to transfer.
7. Run the full budget for 0 attention, 1 layer, 2 layers, and dense-attention control until the smallest layer count that closes the quality gap is identified.

## Mechanism versus execution kernel

Do not conflate FlashAttention with QKV semantics. FlashAttention is an execution kernel for a causal softmax contraction. A lexical Write/Read/Value mechanism may pass read addresses, write addresses, and contextual values through API arguments named `q`, `k`, and `v`; those API labels do not redefine the architecture. In code and prose, preserve W/R/V names and state explicitly when the operation is mathematically attention.

Conversely, a flash-style Delta/WVR kernel preserves recurrent WVR equations and is not attention merely because it uses SRAM tiling. Verify whether a third-party Delta kernel reads before or after the current write; causal indexing changes are architecture changes.

## Lexical W/R/V attention candidate

A minimal lexical attention layer can use:

- `W`: deterministic lexical address plus a gated contextual correction;
- `R`: contextual read address;
- `V`: contextual value `W_v h`;
- causal softmax over `R W^T`, executed by SDPA/FlashAttention;
- cache `(W,V)` for incremental decoding.

Tests must assert strict causality, full/incremental equivalence, no accidental `q_proj`/`k_proj` architecture symbols, and correct cache shape.

## Interpretation

If one or two attention layers close the loss gap, report the minimal-attention threshold rather than claiming attention-free parity. This is often more defensible than burying a targeted negative result or turning dense attention into the main substrate with the novel mechanism merely as a residual.
