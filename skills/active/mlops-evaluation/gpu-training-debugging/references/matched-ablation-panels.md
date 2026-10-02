# Matched ablation panels across hardware and budgets

Use this pattern when new reviewer-requested controls cannot be run under the original accelerator or full token budget.

## First reconstruct the protocol

Do not infer token budget from labels such as “100M ablation.” Compute:

```text
tokens_per_optimizer_step = micro_batch_per_gpu × gpu_count × accumulation × sequence_length
total_tokens = tokens_per_optimizer_step × optimizer_steps
```

Cross-check the result against all reporting checkpoints. A table with `Eval @ 750` and `Train @ 950` necessarily requires a run longer than 950 optimizer steps; a 95-step proxy cannot silently replace it.

## Recommended table structure

### Panel A — original full-budget study

State explicitly:

- accelerator type and count;
- parameter count;
- total training tokens and optimizer steps;
- train/eval reporting checkpoints;
- data split/stream definition;
- measured throughput.

Keep historical rows and values unchanged.

### Panel B — short-budget reviewer controls

State explicitly:

- different accelerator type/count;
- reduced total-token budget;
- short-protocol train/eval checkpoints;
- identical seed, data shard, effective batch, and runtime across all rows;
- primary-method and dense bridge controls rerun beside the new controls.

Suggested rows:

1. new learned/control variant A;
2. new learned/control variant B;
3. primary method bridge control;
4. dense bridge control.

Compare losses and rankings only within Panel B. The bridge rows answer whether the new variants help under the short protocol; they do not transform Panel B into a direct replication of Panel A.

## Throughput presentation

Preferred options, in order:

1. omit throughput from Panel B when the runtime kernel path differs;
2. report it in a separate column headed with the exact hardware, such as `Tok/s (2× accelerator, diagnostic)`;
3. add a note: `Throughput is hardware- and implementation-specific and is not compared across panels.`

Never put B200/H100 and RTX/H200 speeds in one ranking without a matched rerun. Also verify the concrete active dispatch path: a generic `custom kernels available` flag can coexist with a slow fallback.

## Safe wording

> Panel (a) reports the original full-budget ablations. Panel (b) reports reviewer-requested router controls under a deliberately reduced budget on different hardware. All Panel (b) variants, including the primary and dense bridge controls, use the same data, seed, batch, and runtime. Losses and throughput are compared only within a panel.
