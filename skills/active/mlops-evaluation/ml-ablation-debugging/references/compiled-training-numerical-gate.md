# Compiled-training numerical gate for paid ML runs

Use this procedure before any long compiled ablation, especially when parameters or intermediate representations are tied across layers.

## Mandatory preflight

Run the real batch shape, precision, loss backend, optimizer, and compilation mode for at least **three optimizer updates**. One update is insufficient: graph-reuse failures often first appear on update two.

Abort immediately if any of these becomes non-finite:

1. loss before backward;
2. gradient of the model output (`retain_grad`);
3. any parameter gradient before `optimizer.step()`;
4. any parameter after `optimizer.step()`;
5. architecture gates or telemetry scalars.

Never complete a throughput smoke after NaNs appear, and never report throughput from that run.

## Differential localization

Change one variable at a time:

- eager vs compiled;
- compile mode;
- custom kernels on/off;
- real shape vs reduced shape;
- `lr=0` frozen update vs a real optimizer update;
- feature module vs nearest dense control;
- tied/shared parameters vs independent parameters.

At each update, log the first non-finite boundary. This distinguishes a bad forward, bad loss gradient, compiled backward corruption, and optimizer corruption.

## Shared/tied-state matrix

If tied state is implicated, test separately:

- one module registered under several owners;
- one registered parameter consumed repeatedly;
- one lookup result reused across layers;
- cloned per-layer consumers;
- independent parameters initialized identically.

Do not call the root cause proven until the nearest dense control and independent-state control remain finite.

## Rule of three

After three mathematically equivalent sharing rewrites fail, stop patch stacking. Preserve the scientific semantics, use the known-finite execution path for urgent runs, and isolate compiler interaction in a dedicated minimal reproducer.

## Recovering throughput on the known-finite path

When eager is the only numerically valid path, do not assume the whole compiler gain is lost. Compare the experimental arm structurally with the fast control and remove exact overheads before redesigning the architecture:

- Hoist deterministic, layer-invariant work out of the layer loop. If ten layers compute the same token-derived address tensor, compute it once per model forward and pass it to every layer. Add an equality test between precomputed and local paths.
- Fuse parallel input projections into one concatenated `F.linear`, then split outputs, while retaining separate parameters and checkpoint keys. This matches common fused Q/K/V or K/Q/V patterns without changing model semantics.
- Check for materialized repeats, redundant dtype conversions, masks, normalizations, and launch-heavy small GEMMs.
- Re-run both candidate and baseline on the same final commit. A control measured before shared-path refactoring is not a valid throughput comparator.
- Report median throughput after warm-up over repeated windows; keep maxima and last-point rates diagnostic only.

Require bitwise or tolerance-tested semantic equivalence before treating a speed rewrite as the same ablation. If the optimized arm remains slower, state the measured quality/throughput trade-off rather than using an invalid compiled run as the speed reference.

## Paid GPU discipline

- Put a fail-fast non-finite guard in the training loop.
- Start the baseline first.
- Verify the first three updates before leaving a long run unattended.
- Keep all compared arms on the same execution path; compiled-vs-eager is not an architecture comparison.
- When the user specifies a deployment branch (for example `main`), commit/push that branch and clone that exact commit. Do not introduce an extra experimental-branch transfer workflow.
- Report the active commit, run name, and numerical-gate result immediately.
