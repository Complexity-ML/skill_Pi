# Throughput-Preserving Lexical GQA Ablations

Use this pattern when the target is to beat a strong GQA baseline while preserving large-scale training economics.

## Promotion contract

Treat quality, throughput, and parameter budget as joint gates:

- Define the required held-out loss delta before exploration (for example, `-0.03` to `-0.05`, not merely `< 0`).
- Measure stabilized same-GPU training throughput at the target batch and sequence length.
- Convert slowdown into end-to-end cost: `new_days = baseline_days * baseline_tok_s / candidate_tok_s`; report extra calendar days and GPU-days.
- Reject a slow quality winner when its gain does not justify deployment cost. A small loss win with an 8–9% slowdown is not a scalable winner.
- Use full-budget loss for promotion. Early gains can reverse around the middle of training, and mid-run losses can recover late.

## Evidence-driven ladder

1. **Preserve GQA exactly at initialization.** Keep contextual Q/K/V as the main path. Initialize lexical objects to zero or use a zero gate, and verify numerical equivalence at identical baseline weights.
2. **Avoid arbitrary token hashes.** Fixed sinusoidal token-ID codes can help early and degrade late. Prefer learned lexical objects and name the mechanism lexical rather than semantic.
3. **Do not pay for wider attention heads unless necessary.** Concatenating lexical Q/K dimensions can preserve FlashAttention compatibility but still increase score compute materially.
4. **Prefer in-dimension residuals.** A low-rank learned lexical object can be projected into the existing K dimensions:
   `K' = K_gqa + g_k A_k(L(token))`.
   This keeps head width, causal cache shape, and fused SDPA/FlashAttention unchanged. A rank-16 to two 48-dim KV-head projection adds only about 15k parameters in a 10-layer 100M model.
5. **If K-only wins but misses the target delta, test one mechanism at a time:**
   - projected lexical Q+K residuals in the existing dimensions;
   - Q/K renormalization after residual injection;
   - per-head/per-layer gates with sparsity pressure;
   - token-frequency-conditioned amplitude to suppress common syntax tokens.
   Keep V contextual unless lexical V is an explicit axis.
6. **Compress known winners before inventing a new family.** Inspect final per-layer/head gates, then test top-1/top-2 active layers if an all-layer mechanism wins quality but is slow. Do not assume lower layers are best; use checkpoint gates.
7. **Do not shrink the dense MLP casually to match tiny attention additions.** A small attention branch can require a surprisingly damaging MLP-width reduction. Report both strict parameter-matched and intact-backbone controls; promote only with the deployment contract stated explicitly.

## Clean comparison matrix

For each candidate, preserve dataset revision/hash, tokenizer, seed, batch, sequence, steps, optimizer, eval cadence, and backend. Record:

- final finite held-out loss from `metrics.csv`;
- stabilized median/representative tok/s;
- realized parameter count;
- final gate values by layer/head;
- exact commit and realized `run_config.json`.

Run seed 42 architecture selection first. Replicate seeds 43–44 only after the candidate reaches the predefined loss target and throughput threshold. Pair fresh baselines on the same hardware/runtime where possible.

## Operational pattern on paid dual-GPU hosts

- Run one condition per GPU under a durable supervisor.
- Stop structurally redundant candidates once a decisive target-width discriminator fails, but let close or previously reversing candidates reach full budget.
- Mirror metrics/configs immediately after completion; checkpoints are needed only for gate inspection or downstream evaluation.
- Keep the baseline running when replacing only the failed candidate on the other GPU, so paid capacity continues producing useful paired evidence.
