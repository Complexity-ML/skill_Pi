# Training-budget/runtime reconciliation

## Why this check comes first

A model-size label is not a training budget. “100M” can describe parameter count, training tokens, or both. Confusing 100M tokens with 1B tokens creates a 10× runtime error that can be mistaken for a throughput regression.

## Worked example

Resolved production shape:

- micro-batch per GPU: 32 sequences
- world size: 2 GPUs
- gradient accumulation: 8
- sequence length: 2048 tokens
- measured time: about 12.23 seconds per optimizer step

Effective tokens per optimizer step:

`32 × 2 × 8 × 2048 = 1,048,576`

For a 100M-token ablation protocol, 100 optimizer steps produce:

`1,048,576 × 100 = 104,857,600 tokens`

At 12.23 seconds/step, the estimated runtime is about 20.4 minutes. This agrees with a remembered “about 20 minutes” historical run even though 12 seconds/step initially sounds slow.

An accidental 954-step launch produces:

`1,048,576 × 954 = 1,000,341,504 tokens`

At the same step time, it takes roughly 3.2 hours. The hardware throughput did not become 10× worse; the requested token budget became roughly 10× larger.

## Diagnostic sequence

1. Read the resolved command or manifest, not the shorthand run label.
2. Confirm model parameter count separately.
3. Calculate effective tokens/optimizer step including world size and accumulation.
4. Calculate total training tokens from optimizer steps.
5. Reconcile expected wall time with a historical run before profiling kernels.
6. If the budget is wrong, stop immediately and fix the launcher.
7. Add regression assertions for step count, total token comment, checkpoint interval, and run-name prefix.
8. Relaunch under a name that encodes the corrected budget so partial wrong-budget artifacts cannot be mistaken for valid runs.

## Related but separate throughput issue

After the budget matches, kernel-path profiling can still reveal real inefficiency. For top-2 routing over four experts, a masked-dense fallback that evaluates every expert for each route performs eight expert passes where sparse dispatch needs two. That is a real structural slowdown, but it must not be conflated with a 10× token-budget mistake. Report both independently.
