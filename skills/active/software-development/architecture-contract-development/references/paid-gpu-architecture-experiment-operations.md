# Paid GPU architecture experiment operations

Use this note for matched architecture searches on rented accelerators where correctness, cost, reproducibility, and throughput all gate the result.

## Deployment contract

- Put source, tests, YAML configs, and small manifests in Git. Push an audited targeted commit, then `git pull`/checkout the exact commit remotely.
- Do not repeatedly rsync a working tree. It hides provenance and can overwrite remote state.
- Reserve rsync/scp for runtime supervisor wrappers and result artifacts: metrics, run configs, logs, and selected checkpoints.
- Download public datasets directly on the GPU host from the pinned canonical revision. Verify size and SHA-256 before training; do not upload multi-GB shards from a laptop unless the canonical source is unavailable.
- Record the realized commit, model config, backend, hardware, tokens per step, total tokens, and seed in every run directory.

## Paired-run protocol

1. Run baseline and candidate on separate identical GPUs when possible.
2. Match seed, shard, tokenizer, batch, sequence length, token budget, optimizer, LR schedule, evaluation cadence, precision, compile policy, and kernel policy.
3. Use supervisor with `autorestart=false`; an abnormal post-save exit must never silently restart and duplicate a paid run.
4. Separate monitor failure, SSH failure, supervisor status, and training-process status. A local monitor exit is not evidence that training failed.
5. Inspect the full evaluation trajectory. Short probes may reject memory, NaNs, impossible throughput, or a clearly harmful representation; only full-budget runs establish quality.
6. Archive metrics/configs before stopping an instance. Keep checkpoints only for promising or diagnostic models; rejected checkpoints are usually unnecessary.

## Scale-aware throughput gate

Translate throughput loss into the user's actual scale before accepting a quality gain:

- slowdown fraction: `1 - candidate_tok_s / baseline_tok_s`
- candidate elapsed days: `baseline_days * baseline_tok_s / candidate_tok_s`
- extra GPU-days: `(candidate_days - baseline_days) * gpu_count`

A single-digit throughput penalty can be catastrophic at hundreds of GPUs. Example: 86k versus 94.3k tok/s is about 8.9% slower; a 44-day, 512-GPU job grows by roughly 4.3 calendar days, or over 2,000 GPU-days. Stop or redesign such a candidate unless the user explicitly accepts that tradeoff.

Prefer baseline-preserving paths that retain the stock fused-kernel tensor shapes. A small full-budget loss win is not a production win if it widens attention heads, disables FlashAttention, or adds a recurring per-layer scan.

## Search discipline after a one-seed win

- Preserve the winning config and metrics as a positive control.
- If the winner is too slow or over-parameterized, simplify the path while retaining its useful learned signal; do not discard the positive control or rerun unrelated failed predecessors.
- Run a fresh paired replication on the next seed before making a multi-seed claim.
- If a simplification loses clearly at an intermediate full-horizon evaluation and the failure mechanism is shared across arms, stop it and redirect the GPU to a paired replication or a better-motivated design.
