# Lexical Delta Memory Design

Use this reference when iterating fixed-state associative attention whose addressing or values are tied to token identity.

## Terminology contract

Do not call deterministic token hashes, token IDs, n-gram fingerprints, hidden-state projections, or zero-initialized token modulation tables “semantic.” Report the actual mechanism: lexical address, contextual address, hidden-value write, lexical-value write, collision normalization, induction, or exact-token retrieval. A learned projection is not automatically semantic.

## Diagnostic sequence

1. Inspect the actual recurrence and value source. A mechanism can use lexical addresses while still writing `value_proj(hidden_states)`; that is not lexical-value memory.
2. Read learned controls from the target checkpoint. High write + near-one decay + collapsed output gate suggests noisy additive accumulation.
3. Replace additive updates with residual Delta writes:
   `prediction = key @ state`; `error = value - prediction`; `state = decay * state + write_rate * outer(key, error)`.
4. Keep recurrent state FP32 initially. Test bounded repeated writes, association replacement, causal prefix invariance, and full-vs-incremental equivalence.
5. Vectorize exactly before promotion. For a chunk, solve the causal lower-triangular error system rather than using a Python token loop. Benchmark forward **and backward**; forward-only timing can hide a 10x training slowdown.
6. Sweep chunk sizes at the target batch/sequence/rank. Larger chunks may be faster until triangular-solve cost overtakes launch overhead.
7. Smoke the compiled target-width model. A tiny 3,052-step proxy can rank variants incorrectly at 98M/100M tokens.

## Read/write ablations that preserve fixed state

Change one axis at a time:

- **Stable hidden-value Delta:** lexical/contextual address, hidden activation value. This isolates recurrence stability.
- **Collision-normalized Delta:** preserve the full matrix and add a fixed-size diagonal write-load vector. Precondition read/write codes by causal per-dimension load. This targets interference without partitioning capacity and is a plausible low-cost target-width candidate even when the miniature gain is small.
- **Lexical-value Delta:** replace `value_proj(hidden)` with a deterministic token-value fingerprint distinct from the address fingerprint. Treat this as a diagnostic only: an excellent miniature result can reverse sharply at target width because exact token identity discards useful contextual payload.
- **Lexical token forge:** forge the **read/write lexical components**, but retain `value_proj(hidden)` unless target-width evidence supports exact-token values. Keep the existing contextual address component so the forge is a strict extension of Stable Delta. A forge that deletes contextual routing is a different, weaker baseline.
- **Compressed shared lexical modulation:** when the model already owns a tied `token_scale[token_id]` table, reuse it instead of adding another vocabulary table. A factorized `object_rank -> bottleneck -> state_rank` path (for example `16 -> 4 -> 128`) individualizes lexical routing with hundreds of parameters. Zero-initialized shared token modulation must make the forge exactly reproduce Stable Delta at initialization. Assert table object identity and deduplicated parameter count.

For forge tests, separate the contracts:

1. deterministic lexical forge codes depend only on `token_id`;
2. final read/write addresses may also include the retained contextual projection;
3. values remain hidden-state-dependent;
4. full and incremental outputs match;
5. with forge diagonals at identity and shared token modulation at zero, outputs exactly match Stable Delta after copying common weights.

A proxy for a compressed shared forge must instantiate the actual lexical-object MLP and tie its token table. A generic SwiGLU proxy does not exercise the proposed mechanism and must not be used as its promotion gate. Use a paired control with the same lexical MLP, tied table, seed, stream, schedule, and parameter budget; the only difference should be the compressed forge. Match the forge to that lexical control rather than to a smaller generic-SwiGLU target, because a vocabulary-sized tied table can make global parameter matching impossible or misleading.

For a compressed forge, report both quality and cost: absolute held-out-loss delta against its paired lexical control, deduplicated parameter delta, and stabilized throughput delta. A large paired miniature gain is a valid reason for a target-width smoke, not final evidence: prior exact-lexical variants produced strong 3,052-step gains and reversed at 98M/100M-token scale. Require a compiled full-model smoke before the target-token run and treat the target-scale held-out CSV as authoritative.

If the shared bottleneck helps, do **not** jump directly to independent token-specific read and write heads. Associative lookup requires query/read and write keys to remain in a compatible coordinate system. Preserve one shared forged address center. Independent R/W deltas can erase the gain, and even a zero-gated antisymmetric direction can underperform the common-address forge after training; a no-op initialization does not guarantee the extra branch will remain harmless. Treat R/W directionality as disproven for the tested setup unless new evidence motivates it.

If testing a neural RWV forge next, keep `read` and `write` on the common V3 address and change only the value axis. Never replace the contextual value outright. Produce a bounded lexical modulation of `value_proj(hidden)` behind its own zero-initialized gate:

`value = value_proj(hidden) * (1 + tanh(value_gate) * tanh(value_delta))`

Use the same compressed token bottleneck for the common address and value modulation, preserve/copy the common V3 projection weights where possible, and verify gate-closed full/incremental equivalence before a paired V3-vs-value-modulated proxy. The exact-token-value target-scale failure shows that lexical identity alone is insufficient payload.

## Negative findings worth preserving

- Multi-order lexical hashes can reduce per-channel capacity and throughput; do not assume more n-gram orders improve LM loss.
- Fixed value-column timescale partitions can win a full-length miniature proxy yet lose at target width. Distinct learned decays prove use, not superiority.
- Exact lexical-value writes can beat Stable Delta and GQA in a miniature 3,052-step proxy while losing badly at 98M/100M-token scale. Interpret this as evidence that contextual hidden payload is necessary, not that lexical addressing itself failed.
- A pure token-only read/write forge can lose because it removed the baseline's contextual routing. A corrected forge that preserves contextual routing may yield only a sub-noise proxy gain; do not pay for target-scale promotion unless the gain clears the predefined gate.
- A compressed forge tied to an existing rank-16 token table can show a large paired miniature gain yet only a marginal target-scale improvement. Preserve the mechanism as a candidate, but treat the target-width result as authoritative and do not describe the proxy delta as transferred.
- Independent token-specific R/W heads can underperform the shared forge because they create incompatible per-token read and write dictionaries. A shared-center, zero-gated antisymmetric R/W correction can also degrade a matched proxy, showing that gradual coupling alone does not make directionality useful. Prefer a common forged address and test value modulation as a separate axis; more expressive is not automatically more addressable.
- Per-batch loss spikes that occur at the same steps and amplitudes in GQA are data difficulty, not recurrent instability. Compare exact matched steps and post-spike recovery before redesigning attention.
- A final progress-bar loss is usually the current train batch. Read finite `eval_loss` rows from raw metrics for claims.

## Occurrence-address extensions

Before adding another contextual path, inspect the current address equation. Stable lexical Delta already includes a dense `address_proj(hidden)` context term; adding a second context signature without removing or explicitly gating the first confounds the ablation.

A compact occurrence-address experiment should use one explicit equation:

`address_t = lexical_forge(token_t) + small_context_signature(h_t) + position_signature(t)`

Recommended structural contract:

- replace the dense context projection with a factorized path such as `hidden -> 8 -> state_rank` rather than stacking both;
- use one shared occurrence term for read and write so their coordinate systems remain compatible;
- generate the absolute-position signature deterministically and place it behind a zero-initialized gate;
- add only a fixed-size absolute-position counter to recurrent state, and verify chunked full-forward equals token-by-token incremental execution across chunk boundaries;
- keep `value_proj(hidden)` unchanged;
- compensate removed dense parameters in the matched backbone and verify the realized full-model count.

Position identity is not automatically helpful: making repeated token occurrences too distinct can weaken long-range lexical lookup. Treat the gate and target-scale held-out loss as evidence, not the architectural story.

## Composition is an ablation, not arithmetic

Do not assume two independently positive mechanisms compose. Collision normalization and a compressed lexical forge can target apparently different defects, show a large paired miniature gain when combined, and still fail to improve over collision normalization alone at target scale. Test the combination as its own matched condition and preserve the stronger single mechanism when the target-width delta is null.

After repeated proxy/target reversals within one architecture family, retire the miniature proxy as a promotion gate for that family. It may still check learnability and mechanics, but architecture decisions should move to bounded target-width runs. Do not keep launching increasingly elaborate miniature variants because each clears a proxy threshold that has already lost predictive validity.

## Promotion gate

Promote only after: structural tests -> matched diagnostic appropriate to the architecture family -> target-width compiled smoke -> target-token run. Once proxy/target reversals are observed, treat the proxy as learnability evidence only; target-scale held-out loss is authoritative. After several reversals, skip proxy-based promotion claims entirely and use a bounded target-width discriminator.

Keep raw CSV/JSON and hashes for every negative run. A post-success `PyGILState_Release` during PyArrow/Hugging Face teardown does not invalidate a run if metrics/checkpoint were already saved and the final metrics row is complete.