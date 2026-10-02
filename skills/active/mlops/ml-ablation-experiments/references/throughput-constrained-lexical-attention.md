# Throughput-Constrained Lexical Attention Ablations

Use this protocol when a lexical residual must beat a strong GQA baseline without making large-scale training materially slower.

## Decision criteria

Treat quality, throughput, and parameter budget as simultaneous promotion gates.

- Compare paired runs with the same dataset, tokenizer, seed, batch, sequence length, optimizer, token budget, and attention backend.
- Measure stabilized target-shape training throughput, not warmup or a primitive-only microbenchmark.
- Extrapolate slowdown to the proposed scale before replication. A single-digit percentage regression can represent thousands of GPU-days at fleet scale.
- A quality winner with unacceptable throughput is a diagnostic, not a deployable winner. Stop replicating it and compress the exact winning mechanism.
- Use early/full-budget losses only as rejection evidence when dynamics reverse. Promote only on full-budget held-out loss.

## Baseline-preserving construction

Prefer a strong dense GQA substrate plus a zero-effect lexical residual:

- Keep Q/K/V GQA semantics and the fused SDPA/FlashAttention path.
- Keep V contextual unless a separate value-path ablation is explicitly intended.
- Require exact numerical equivalence to GQA when the lexical source or gate is zero.
- Verify finite backward, nonzero gradients into the gate/object path, causality, full-vs-cache equivalence, and a real target-device smoke.

If an augmented lexical score widens Q/K and wins quality but loses throughput, try to project the learned lexical object into the existing K (or Q/K) head coordinates instead of widening the head. This preserves head dimension and can retain FlashAttention throughput with only a small projection. Avoid compensating a tiny attention parameter increase by shrinking a sensitive dense MLP before proving the lexical mechanism; the compensation itself can erase the gain. Report unmatched and strictly matched controls separately.

## Ablation sequence

1. **Fresh paired baseline** on the same hardware/runtime.
2. **Minimal learned lexical residual** with GQA-equivalent initialization.
3. **Gate initialization** at two small values; do not sweep many values before a full-budget signal exists.
4. **Compress a slow quality winner** by inspecting learned gates and limiting the residual to useful layers/heads. Prefer top-1/top-2 layers before broad depth sweeps when fleet-scale throughput matters.
5. **Norm-preserving residual**: compare `K + residual` with QK renormalization after injection if late degradation suggests norm drift.
6. **Frequency-aware control** only after a uniform learned residual is viable.
7. Replicate seeds only after a candidate meets both loss and throughput thresholds.

## Zipf controls

Never treat tokenizer ID order as token frequency.

- Build counts with the exact tokenizer and frozen training corpus/shard.
- Exclude held-out/evaluation documents from the counts.
- For multi-trillion-token training, do not require a separate exhaustive scan: accumulate counters during tokenization/data preparation, or freeze a representative 1–10B-token sample. Verify rank/bucket stability across increasing sample sizes (for example 100M, 1B, 10B) before accepting the approximation.
- For dataset mixtures, combine corpus counts using the actual training sampling probabilities rather than raw corpus sizes.
- Prefer logarithmic/rank buckets when exact tail counts are unstable; the mechanism needs stable frequency classes, not perfect counts for every rare token.
- Archive counts plus corpus/tokenizer metadata and checksum provenance.
- Apply frequency weights only to the intended lexical residual, not silently to the shared MLP/object path.
- RMS-match the weight vector so ordered and control conditions have comparable average amplitude.
- Compare at minimum:
  - uniform weights;
  - ordered Zipf weights;
  - a deterministic permutation of the exact same weights.
- The permuted condition must preserve the sorted histogram exactly. If ordered and permuted perform equally, frequency ordering is not the cause.
- Consider reversed Zipf only as a causal control when ordered-vs-permuted is ambiguous.

A useful bounded rank weighting is

`w(r) = max(floor, (r / V) ** alpha)`, followed by RMS normalization,

where rank 1 is most frequent. Tune `alpha`/`floor` only after the ordered-vs-permuted test; otherwise the sweep confounds frequency ordering with generic amplitude regularization.

## Failure patterns

- **Deterministic token hashes** can improve early loss and degrade late loss; call them identity hashes, not semantics.
- **Raw lexical vectors added directly to normalized K** can distort key geometry. Prefer a learned low-rank projection and test renormalization.
- **All-layer widening** can produce a small loss win with an unacceptable throughput penalty. Do not replicate before compressing.
- **Early crossing** is not a win. Some lexical variants lead before the midpoint and lose by the final evaluation.
- **Historical throughput comparisons** are insufficient. Pair throughput on the same hardware, commit, runtime, and workload.

## Evidence to retain

A one-seed full-budget win remains architecture-search evidence. If another paired seed reverses the result, summarize paired deltas and continue ablation rather than advertising the best seed. Require the planned multi-seed result before promotion.

For one-shot streaming frequency counters, define completion by a fully written artifact with validated metadata/checksum. Some data readers can leave helper workers alive after the output is flushed; ensure the CLI exits after a successful close so a supervisor does not report a completed count as still running.

For every promoted or rejected full-budget condition, mirror lightweight artifacts immediately:

- `metrics.csv`;
- realized `run_config.json`;
- model/config commit;
- parameter count;
- stabilized throughput and peak memory;
- final gate values by layer/head when relevant;
- corpus/tokenizer/count-table provenance for Zipf experiments.
