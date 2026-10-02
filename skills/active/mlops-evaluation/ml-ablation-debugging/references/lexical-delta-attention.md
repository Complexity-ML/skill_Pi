# Stable lexical Delta attention: diagnostics and iteration protocol

## Scope

Use this reference when a fixed-state lexical associative attention learns a very small output gate, loses to GQA at long horizon, or shows suspected loss spikes.

## Diagnose before adding capacity

For additive memory

\[
M_t=\lambda M_{t-1}+\beta k_t v_t^\top,
\]

inspect checkpoint-effective values, not only initial config:

- `write_rate = sigmoid(write_logit)`
- `decay = sigmoid(decay_logit)`
- effective horizon `1 / (1 - decay)`
- output gate/mix
- state and read norms

High write, near-unit decay, and a tiny learned output gate indicate superposition/interference: the model is suppressing a noisy memory.

## Bounded Delta correction

Use residual writes:

\[
\hat v_t=k_t^\top M_{t-1},\qquad
M_t=\lambda M_{t-1}+\beta k_t(v_t-\hat v_t)^\top.
\]

Required invariants before language training:

1. repeated identical writes remain bounded over at least 8k updates;
2. replacing a value converges to the new association;
3. full-sequence and incremental outputs/states agree;
4. recurrence state remains FP32 under BF16 model execution;
5. causal behavior and fixed state shape are tested.

## Exact chunk vectorization

Do not keep a tokenwise autograd loop. For a chunk with keys `K`, values `V`, initial state `S0`, scalar write `beta`, and decay `lambda`, solve the causal lower-triangular error system.

For positions `i > j`:

\[
A_{ij}=\beta\,\lambda^{i-j-1}k_i^\top k_j,\qquad A_{ii}=1.
\]

Right-hand side:

\[
B_i=\beta\left(v_i-\lambda^i k_i^\top S_0\right).
\]

Then `E = solve_triangular(A, B)` gives exact residual writes. Reads and final state are reconstructed with the same causal decay powers. Test vectorized vs sequential recurrence numerically before benchmarking.

Sweep chunk sizes on the production shape, backward included. Small chunks may be slower because launch overhead dominates; one observed H100 shape favored 512 over 16/32/64/128/256/1024. Never persist that number as universal—re-sweep for batch, sequence, rank, dtype, and hardware.

## Do not invent semantics

A learned projection of lexical or hidden representations is not evidence of semantic addressing. Describe only what is implemented and measured. If the intended mechanism is lexical, keep the mechanism and claims lexical.

A defensible extension is deterministic multi-order lexical addressing:

- order 1 token context;
- order 2 bigram context;
- order 4 and order 8 lexical fingerprints;
- independent bounded Delta memories;
- fixed total state;
- no claim of semantic similarity.

Use deterministic causal token-ID fingerprints and test full/incremental equivalence, including carried token history.

## Diagnose training-loss spikes correctly

A spike in batch train loss is not automatically an attention failure. Compare candidate and baseline at the exact same data steps:

- spike step alignment;
- amplitude above the previous rolling median;
- recovery after 10/20/30 steps;
- held-out curve;
- state norms and finite checks.

Near-identical spikes at the same steps in GQA and the candidate identify difficult batches, not candidate-specific instability. A true attention issue should add unmatched spikes, non-recovery, exploding state/read norms, non-finite gradients, or BF16/FP32 divergence.

## Empirical interpretation and rejected branches

A bounded Delta update can fix a real stability defect without closing the entire quality gap. One production-scale pattern was:

- additive memory: high write + near-unit decay + tiny output gate;
- Stable Delta: lower learned write, near-unit decay, no output gate, much larger contextual mix;
- Stable Delta improved every associative predecessor but still lost to matched GQA.

Interpret this as evidence that stability was one defect, not proof that addressing or temporal organization is now optimal.

Do not assume deterministic multi-order lexical fingerprints will help merely because they are honest lexical mechanisms. A rank-split `1/2/4/8` design can lose both quality and throughput: each channel receives less capacity, and multiple Delta solves add overhead. Reject it at proxy scale when it loses to both GQA and single-state Stable Delta; do not promote it to a production run.

**Multi-timescale Stable Delta is diagnostic, not a default upgrade.** A clean implementation can:

- retain the same address and full state matrix;
- partition value columns, not key/address capacity;
- learn one bounded decay and write rate per value group;
- initialize groups across short-to-long horizons;
- preserve full/incremental equivalence and exact chunked recurrence.

Avoid four serialized triangular solves. Reshape value groups into the batch dimension, repeat keys/queries, pass per-batch decay/write tensors to one triangular solve, then restore the original column layout. Verify this batched formulation against incremental recurrence before measuring it; this recovered most of the observed production-shape throughput penalty.

Do not promote the design solely because a full-length miniature proxy wins. In one matched production run, four groups learned distinct, sensible horizons (roughly 22, 45, 89, and 1816 tokens) but still finished behind the single-timescale Stable Delta. The fixed value-channel partition was therefore a mild capacity constraint despite successful temporal specialization. Preserve the result as an ablation and return to the unpartitioned matrix for subsequent interference/read-write experiments.

## Preserve capacity while reducing collisions

After bounded Delta and failed rank/channel partitioning, prefer an anti-interference change that keeps the full matrix intact. A useful pattern is a fixed-size diagonal address-load state:

\[
d_t=\lambda d_{t-1}+\beta k_t^2.
\]

Before each read/write, scale each address dimension by the inverse square root of its causal accumulated load, then renormalize the address. This is diagonal collision preconditioning, not semantic retrieval and not a learned gate.

Implementation requirements:

- compute `d_before` causally for every position in the chunk;
- carry only one rank-sized FP32 load vector in addition to the matrix and prior address;
- precondition both write keys and read queries from the same causal load;
- verify full/incremental equality and non-negative finite load;
- generalize cache plumbing when the context state gains a third tensor;
- benchmark production-shape backward, not only the standalone forward.

This can produce a small but real full-scale gain without partitioning rank. In one matched production run, diagonal collision normalization improved held-out loss from `4.898880` to `4.895427` while preserving roughly matched throughput, becoming the best associative candidate in that suite but still trailing GQA `4.820476`. Treat such a marginal proxy gain honestly: it authorizes a matched full run only after throughput smoke, not a claim of superiority.

## Test lexical values separately from hidden-state values

A lexical address does not imply that the stored value is lexical. Inspect the write path: many associative implementations use `value_proj(hidden_states)`, so they store dense model activations under lexical/contextual addresses.

A clean lexical read/write ablation replaces hidden-state values with a deterministic token-identity code:

\[
a(token_{t-1}) \rightarrow c(token_t),
\]

where address code `a` and value code `c` are distinct deterministic fingerprints. Do not call either code semantic. Recommended controls:

- remove the now-unused hidden `value_proj` before parameter matching;
- precompute non-persistent token-code tables when vocabulary size is known;
- retain an on-the-fly deterministic fallback for incremental or standalone use;
- test that different token IDs produce different codes;
- require full/incremental equality before the language proxy;
- compare this pure lexical-value branch directly against the same Delta rule storing projected hidden activations.

Do not silently reuse a token-modulation table as an “object embedding.” A zero-initialized low-rank `token_scale` that modulates a hidden projection is not a standalone token representation; trace its forward semantics before tying it into attention.

A miniature proxy can strongly overrate pure lexical values. One observed deterministic token-value branch beat GQA and Stable Delta on a 3052-step miniature proxy, then regressed to `4.963167` at production scale—worse than the hidden-value Stable Delta (`4.898880`), collision-normalized Delta (`4.895427`), and even the additive candidate (`4.921405`). The durable lesson is architectural: lexical addresses may be useful, but the stored payload still needs the contextualized hidden activation. Do not promote pure token-code values from proxy evidence.

## Lexical read/write forge without semantic claims

When investigating learned lexical routing, forge only the lexical portion of read/write addresses and retain `value_proj(hidden_states)` as the payload. A minimal forge learns global diagonal transforms:

\[
r_t=\operatorname{normalize}(d_r\odot a(token_t)+m\,c_t),\qquad
w_t=\operatorname{normalize}(d_w\odot a(token_t)+m\,c_t),
\]

where `a(token)` is a deterministic lexical fingerprint and `c_t` is the existing contextual activation used by the baseline. Do not call `c_t` semantic unless separately measured.

Required forge protocol:

1. read/write lexical codes depend only on `token_id`;
2. contextual routing and hidden-state values remain exactly those of Stable Delta;
3. initialize `d_r=d_w=1`, so the complete candidate is bit-for-bit equivalent to Stable Delta before training;
4. test full/incremental equality after read/write paths diverge;
5. add only the forge parameters to the iso-parameter calculation;
6. reject any V1 that removes a useful baseline path instead of extending it.

A concrete failure demonstrated why neutral equivalence matters: a token-only forge that removed contextual routing reached `6.7604` on the miniature proxy, behind Stable Delta `6.74745`. That result did not test whether forged lexical read/write helps Stable Delta; it tested a confounded deletion. The corrected V2 must preserve contextual routing and differ only through learned lexical read/write geometry.

## Scale discipline

Synthetic recall and miniature FineWeb proxies are mechanistic screens only. Even a 3052-step miniature proxy can rank candidates differently from a 100M-token production model. After a candidate passes invariants and throughput smoke, only the matched production held-out curve decides superiority.

Always distinguish final-batch train loss in a progress bar from held-out eval loss in `metrics.csv`.

For metric logging, convert autograd tensors with `float(loss.detach())` or `loss.detach().item()`, never `float(loss)`. If a PyArrow/Hugging Face finalizer aborts only after a non-empty JSON/CSV and checkpoint have been written, verify and hash those artifacts before classifying the training run as failed.