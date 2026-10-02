# Stable fixed-state associative attention: diagnosis and repair

Use this reference when a fixed-state associative/fast-weight context branch has synthetic retrieval capacity but contributes little to target-scale language loss.

## Diagnose before adding capacity

Inspect the learned effective controls from a completed checkpoint:

- `write_rate = sigmoid(write_logit)`
- `decay = sigmoid(decay_logit)`
- learned context output scale/gate
- learned lexical/contextual address mix

A characteristic unstable additive-memory pattern is:

- write rate near one;
- decay near one (long persistence);
- address mix grows, proving the address path trains;
- output gate collapses toward zero.

Interpret this as the backbone suppressing a noisy accumulated memory, not automatically as insufficient context capacity. Estimate the rough persistence horizon as `1 / (1 - decay)`, but validate norms empirically over the target sequence length.

The additive update

`M_t = decay * M_(t-1) + beta * k_t v_t^T`

can repeatedly accumulate colliding/similar keys. More fusion layers or a larger receptive field do not repair this recurrence.

## Stable Delta update

Use residual error writes:

`prediction_t = k_t^T M_(t-1)`

`error_t = v_t - prediction_t`

`M_t = decay * M_(t-1) + beta * k_t error_t^T`

This makes repeated correct associations converge instead of grow and permits replacement of old values. Keep the recurrent matrix in FP32 initially; cast only the projected output back to the model dtype. The state remains fixed-size.

## Structural tests before training

Write these tests before benchmarking:

1. Repeating one key/value for 8k writes keeps state norm finite and near the target scale.
2. Repeating a new value for the same key replaces the old association.
3. Full-sequence and one-token incremental outputs and final states agree.
4. Future perturbations cannot alter prefix outputs.
5. The recurrent state is FP32 and fixed-size.
6. Gradients reach address/value/output projections.

Do not promote based only on recall/induction if those capabilities were already known. Order evidence by the user's actual failure criterion (usually held-out LM loss).

## Exact chunkwise vectorization

A Python token loop may have fast forward but a catastrophically slow backward because autograd builds one node chain per token. Vectorize each chunk exactly.

For a chunk with write keys `K`, values `V`, initial state `S0`, scalar `beta`, and `lambda=decay`, define the strict-lower decay matrix:

`D[i,j] = lambda ** (i-j-1)` for `i > j`, else zero.

The error system is lower triangular:

`A = I + beta * (K K^T) * D`

`rhs = beta * (V - lambda**positions * K S0)`

`E = solve_triangular(A, rhs, upper=False, unitriangular=True)`

For aligned causal queries `Q`, reads are:

`Y = lambda**positions * Q S0 + ((Q K^T) * D) E`

and the final state is:

`S_next = lambda**L * S0 + K^T (lambda**reverse_positions * E)`

Process long sequences as several exact chunks, carrying `S_next` between chunks. Assert numerical equivalence to the sequential reference before measuring speed.

## Chunk-size selection

Do not assume smaller chunks are faster. Triangular solve has quadratic work, but launch and autograd overhead can dominate. Sweep chunk sizes with:

- forward and backward;
- the target batch, sequence, hidden size, rank, and precision;
- peak memory;
- full-model compiled smoke after the primitive benchmark.

A primitive-only speed win is not sufficient. The final gate is stabilized full-model throughput under the same compilation protocol as GQA.

## Diagnose loss spikes without hand-waving

Do not automatically blame recurrent attention for noisy per-batch loss, and do not dismiss spikes as “just noise” without a matched check.

1. Align the candidate and GQA/baseline metrics by **exact optimizer step** on the same deterministic data stream.
2. For each candidate spike, compute deviation from a recent rolling median and the 10/20/30-step recovery.
3. If spikes occur at the same steps with nearly identical amplitudes in GQA, classify them as hard-batch/data effects rather than recurrence instability.
4. Suspect the attention only when candidate-only spikes coincide with exploding state norm, non-finite gradients, persistent post-spike degradation, or BF16/FP32 divergence.
5. Add architecture-aware telemetry for state norm, read RMS, write rate, decay, and update/error norm; generic MLP gate logs cannot diagnose attention.

Keep names explicit in live reporting: `context_output_gate` belongs to attention, while `object_gate` and `micro_gate` belong to lexical MLP residuals. Never imply that removing the former removed the latter. If the user asks whether gates remain, answer this distinction first.

## Multi-timescale extension after scalar Delta

If scalar Stable Delta improves target-scale loss but still trails GQA, inspect whether one global decay is forcing every value channel onto the same temporal horizon. A minimal extension is to split only the **value columns** of the same `rank x rank` state into groups with separate learned decay/write scalars. This preserves the address, total state size, fixed-state contract, and Delta rule.

Recommended sequence:

1. Initialize several bounded horizons (for example decays near `0.95`, `0.99`, `0.997`, `0.9995`) rather than four copies of the same scalar.
2. Keep one shared key/address space and partition columns, not separate small key matrices; splitting rank into hashed lexical n-gram heads can lose capacity and add compute.
3. Vectorize timescales by folding the group axis into the batch axis and perform one batched triangular solve. Extend the exact scan to accept per-batch decay/write vectors, and assert full/incremental equivalence before and after batching.
4. Benchmark the compiled target-width model. Four Python solve calls can erase the proxy throughput win even when each group is mathematically sound.
5. Treat a long miniature proxy as a discriminator only, not proof: target-scale runs have previously reversed proxy rankings.

Do not describe deterministic token hashes, n-gram fingerprints, or hidden-state addresses as "semantic" without direct evidence. Use precise terms such as lexical identity, contextual address, learned address, transition retrieval, or exact/approximate collision behavior. A learned projection is not automatically a semantic representation. If the user rejects semantic framing, correct the terminology immediately and redesign in terms of measurable lexical read/write behavior rather than merely renaming the same unsupported claim.

## What target-scale reversals teach

A multi-timescale value-column Delta can win a 3,052-step miniature proxy yet lose to scalar Stable Delta at 98M parameters and 100M tokens. Treat that as evidence that fixed column partitioning can reduce final capacity even when learned decays remain clearly separated. Preserve the negative result; do not keep launching adjacent full-budget variants from the same proxy signal.

When evaluating such extensions:

- Compare finite held-out `eval_loss`, never the final progress-bar train loss.
- Report target-scale throughput separately from proxy throughput.
- Inspect effective learned decays/write rates to verify that the extension was actually used.
- If the full result loses, revert the architecture baseline to scalar Stable Delta rather than stacking the failed extension with another mechanism.

## Collision normalization without partitioning capacity

A lower-risk anti-interference extension preserves the complete `rank x rank` Delta matrix and adds a fixed diagonal load vector. Track exponentially decayed squared key load per address dimension, then precondition causal write keys and queries before the ordinary Delta scan. Required invariants:

1. Load is non-negative, fixed-size, and caller-owned.
2. Full-sequence and incremental outputs/states match, including the load vector.
3. The load update is causal and chunk-boundary invariant.
4. The matrix capacity is not split into hashed heads or timescale blocks.
5. Target-width compiled throughput is measured before a full run.

A marginal proxy gain is not enough after known proxy reversals; require bounded target-width evidence and preserve scalar Stable Delta as the control.

## Audit lexical read/write semantics precisely

Inspect the actual memory value path. A lexical address paired with `value_proj(hidden_states)` stores a dense activation, not token identity. Likewise, a zero-initialized rank-16 token modulation table is not automatically a standalone lexical object or semantic embedding.

For a strict lexical-value ablation, write a deterministic token-identity code (or a clearly defined tied lexical object) under the previous lexical/contextual address, then project the retrieved code back to hidden space. State the comparison exactly:

- hidden-value Delta: address → projected activation;
- lexical-value Delta: address → deterministic token code.

Do not call either path semantic. Verify parameter matching, exact previous-key/current-value alignment, full/incremental equivalence, fixed state, and matched LM loss before promotion.

## Promotion discipline

- Tiny language proxies are learnability diagnostics, not reliable target-scale promotion gates once one has produced a false positive.
- Never retrain an already-losing checkpoint merely to avoid transferring it; iterate the architecture instead unless exact reproduction is explicitly required.
- Keep standalone experimental code separate from the production mixer. Integrate only after structural tests and matched evidence.
- A progress-bar `loss` is usually current train-batch loss. Read finite `eval_loss` rows from raw CSV for decisions.
- A teardown abort after final JSON/CSV/checkpoint writes does not invalidate the run; verify artifacts and final step. Also check for orphaned GPU processes from completed streaming jobs and terminate only confirmed stale PIDs.
