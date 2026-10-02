# W/R/V, Flash-style execution, and minimum-attention studies

Use this note when a fixed-state W/R/V architecture is near an attention control in throughput but remains behind in language-model quality.

## Keep three concepts separate

1. **W/R/V recurrence**: write address W, read address R, contextual value V, fixed recurrent state, no softmax over prior positions.
2. **Flash-style execution**: IO-aware tiling, SRAM-resident chunks, fused forward/backward, and no materialized sequence-square intermediates. This is an implementation strategy and need not imply Q/K/V.
3. **Stock FlashAttention operation**: causal `softmax(R W^T)V` when R/W/V are passed through the API's `q`/`k`/`v` slots. This is attention, even when architecture-facing names remain W/R/V.

Never infer (3) from a request for (2). Ask only if the intended semantics remain genuinely ambiguous; otherwise preserve the stated W/R/V equations.

## Performance diagnosis

- Compare against the actual named control, not merely the nearest internal predecessor.
- Match runtime, compilation policy, sequence length, batch, loss backend, and evaluation cadence.
- Count causal scans, not only projection matmuls. Parallel projections plus one recurrent scan per route can still be much slower than one scan.
- A single rectangular state can combine common and routed address subspaces while retaining contextual V columns and one scan.
- Separate compile warm-up and evaluation/recompilation stalls from steady-state intervals.

## When quality, not throughput, is the blocker

If W/R/V throughput is already close to the full-attention control, another kernel rewrite does not by itself address a measured loss gap. Prefer a threshold experiment:

- 0 attention layers: canonical conv + WVR + lexical model.
- 1 lexical W/R/V attention layer at a pre-registered non-WVR position.
- 2 lexical W/R/V attention layers only if one layer misses the full-budget gate.
- Full GQA/attention: matched control.

Preserve WVR invocation points while inserting attention elsewhere, or state explicitly that WVR was removed. Match total parameters by adjusting a declared width, not by adding uncounted residual branches.

## Lexical W/R/V attention contract

A project-specific attention layer may use:

- `W = normalize(lexical_address(token) + gamma * contextual_write(h))`
- `R = normalize(read_projection(h))`
- `V = value_projection(h)`
- causal retrieval `softmax(R W^T / sqrt(d)) V`

In code, keep names such as `write_addresses`, `read_addresses`, and `values`. Third-party kernels may require arguments named `q`, `k`, and `v`; those are adapter details, not permission to rename the architecture or add generic Q/K projections.

## Run discipline

- Short pilots eliminate OOM, NaN, dead gates, and unacceptable throughput.
- If short proxies previously failed to rank full-budget models, never promote a proxy winner; run the smallest pre-registered full-budget arm.
- Stop paid runs immediately when they violate an explicit gate or instantiate the wrong architecture.
- Before killing by process pattern, avoid patterns that match the SSH shell command itself; identify the service/PID first and verify GPU memory afterward.
