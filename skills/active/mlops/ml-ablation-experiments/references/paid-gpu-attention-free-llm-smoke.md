# Paid GPU smoke for attention-free LLM experiments

Use this recipe when moving an attention-free causal-convolution model from local diagnostics to a paid NVIDIA run.

## Preflight

1. Verify the exact remote commit and assert the causal mixer file exists.
2. Inventory GPU model/VRAM, driver/runtime, free disk/RAM, and active GPU processes.
3. Install in an isolated venv; verify `torch.cuda.is_available()`, device name, and supported SM architecture.
4. Run architecture tests remotely, including zero Q/K/V parameters and full-vs-cached decode equivalence.

## Progressive exact-shape smoke

- Start with a tiny full forward/backward/optimizer run.
- Increase to the intended sequence length before increasing batch.
- Sample VRAM, utilization, power, and temperature during each smoke.
- Treat output-vocabulary cross-entropy as a separate memory bottleneck: with o200k, the loss chunk can OOM even when the causal mixer fits.
- After an OOM, reduce batch and optionally loss-chunk size; do not infer fit from model parameter count.
- Ignore the first throughput step when it includes allocations/warm-up. Use stabilized later steps for ETA.

Observed useful pattern: a 98.2M model with hidden 384, 10 layers, exact o200k head, sequence 2048, BF16, and no grad checkpointing fit batch 16 in about 50 GiB on one H100 80GB; batch 32 OOMed near 81 GiB during cross-entropy. This is a reference point, not a universal batch prescription.

## Data integrity before long run

- Do not reuse one streaming iterator for train and eval.
- Partition by immutable document index or ID before tokenization, and test that train/eval predicates are disjoint.
- Make the held-out density high enough that eval does not scan an excessive number of remote documents. A sparse holdout can be statistically sufficient but operationally disastrous for streaming evaluation.
- Smoke the real tokenizer and real streaming dataset after the synthetic hardware smoke; data/network/tokenization can change throughput materially.
- A synthetic random-token smoke validates hardware and optimizer mechanics only, never model quality.

## Durable paid execution

- Run the long job under a durable remote supervisor such as a transient `systemd` unit so SSH loss does not kill training.
- Write continuous logs and `metrics.csv` outside ephemeral terminal buffers.
- Verify the service is active, GPU memory is allocated, and at least one stabilized metrics row is finite before leaving it unattended.
- Use a silent watchdog that alerts once on failure/completion rather than sending routine progress spam.
- Some streaming dataset clients can throw teardown/thread errors after final metrics are written. Apply the paid-sweep rule: treat the run as complete only when intended final-step metrics exist; preserve the error as a warning.

## Checkpoint policy

For cheap diagnostics, disable checkpoints. For a headline 1B-token run, keep at least one final checkpoint if downstream evaluation, inference benchmarking, or artifact reproducibility requires it. State this exception explicitly; do not accumulate intermediate checkpoints by default.

## Cost gate

After the real-data smoke, calculate ETA from stabilized throughput and show:

- exact token count and steps;
- measured tokens/s;
- estimated compute hours;
- hourly provider rate;
- expected cost and a conservative overhead range.

Require explicit user approval before crossing from smoke to the paid long run.