# Shared+routed residual framing and live baseline ordering

Session lesson from Complexity-ML token-routed MLP ablations.

## Scientific framing

When a routed lexical branch only wins after adding a shared dense path, do not frame the result as “routing replaces dense MLPs.” The defensible claim is:

> A frequency-balanced routed lexical branch can improve a shared dense MLP backbone when used as a residual specialization path.

Use ablations to separate the roles:

- `dense_residual`: dense baseline; run early so live comparisons have an anchor.
- `zipf_shared`: shared dense path + Zipf-routed lexical residual.
- `zipf_no_shared`: tests whether routing alone suffices.
- `shared_only`: tests whether extra/shared dense capacity alone explains the gain.
- `random/modulo/round_robin_shared`: tests whether the routing table quality matters once the shared path is present.

Interpretation pattern from the B200 100M suite: `zipf_shared > dense_residual > modulo_shared > round_robin_shared > random_shared > zipf_no_shared` on best validation. Phrase this as “lexical token identity is a meaningful routing object when paired with a shared dense backbone and frequency-aware partitioning.” Do not reduce it to “shared always wins” or “routing replaces dense.”

Avoid overclaims:

- Do not say “routing replaces dense” if the winning model is shared-plus-routed.
- Do not cite short local/MPS smokes as final evidence; use them for debugging and schedule/gate sanity.
- Report matched-token quality separately from wall-clock/FLOP efficiency when routed variants are slower.
- If a reviewer asks for matched wall-clock, answer the narrower claim explicitly: matched wall-clock is a training-efficiency metric; matched tokens is the quality/sample-efficiency evidence. Report throughput, admit dense is faster if true, and do not claim training wall-clock efficiency unless measured.
- Separate training throughput from deployment/inference relevance. Training is often a one-time cost, while inference is recurring; a slower training implementation can still be operationally interesting if the model is smaller, serving-friendly, and high-throughput at inference. Do not claim inference wins without a same-setup dense baseline; phrase it as serving compatibility/high-throughput sanity unless the comparison exists.

## Launcher ordering for paid/live sweeps

For expensive sweeps where the user wants to watch progress, run the dense baseline first (or immediately after an already-running current run) so every subsequent variant can be interpreted live.

Recommended order for shared+routed ablations:

1. `dense_residual`
2. `zipf_shared`
3. `zipf_no_shared`
4. `modulo_shared`
5. `random_shared`
6. `round_robin_shared`
7. `shared_only`

If a sweep was accidentally started with a non-baseline first, either:

- let the current run finish if it is nearly complete, then kill/reorder before the next run starts; or
- stop immediately if the current run is early and paid compute would be wasted.

When reordering a live remote sweep, use a watcher that waits for the current run’s `metrics.csv` to complete, kills the next run/driver immediately, cleans partial metrics for the killed run, and relaunches the remaining variants with the baseline next.
