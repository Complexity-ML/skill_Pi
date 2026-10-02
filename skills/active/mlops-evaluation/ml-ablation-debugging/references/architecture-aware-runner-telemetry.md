# Architecture-aware runner telemetry

## Failure mode

A generic ML runner may expose parser defaults for several model families. If startup summaries and progress bars print those arguments unconditionally, they can report controls that the built model never consumes—for example top-k route weights on a lexical-residual MLP with no top-k setter. Training may be numerically correct while the telemetry is scientifically false.

## Capability-driven pattern

1. Build the concrete model before formatting architecture-specific logs.
2. Inspect modules for the capability that makes each control effective:
   - a callable schedule setter;
   - the actual learned gate parameter;
   - routing counters or expert tensors;
   - the instantiated sequence mixer class.
3. Store a small immutable runtime-capabilities record.
4. Apply schedules only if their target capability exists.
5. Construct startup summaries and progress fields from capabilities, not generic CLI defaults.
6. Report learned scalar values by reading model parameters after synchronization, rather than echoing initialization arguments.
7. Branch optimizer summaries so inactive Muon/MoE settings are not printed for AdamW.
8. Preserve CSV compatibility separately: irrelevant legacy columns may be `NaN`, but should not appear as active status fields.

## Regression test

Use tiny dummy modules for each supported family and assert both positive and negative detection. Then run a one-step smoke for each family and assert:

- expected architecture name and active gates are present;
- fields belonging to other families are absent;
- the optimizer summary contains only active optimizer controls.

Negative log assertions are essential because the bug is misleading presence, not a crash.

## Third-party warning duplication

Some libraries install their own handler and also propagate to the root logger, printing the same recoverable warning twice. Configure the named library logger and disable propagation. Suppress only retry chatter; terminal failures must still raise.

## Active paid runs

Do not restart or hot-patch a healthy paid run merely to clean display fields. Preserve its code provenance, fix future runs, and interpret stale fields from the archived startup configuration.
