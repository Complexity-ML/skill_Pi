# Paid-GPU Data and Launcher Resilience

Use this pattern for long ablation suites on rented accelerators, especially when data is streamed from a remote hub.

## Preflight before allocating GPU work

1. Read at least one real training example and one evaluation example with the exact environment used by the service.
2. Verify tokenizer checksum, resolved dataset revision, and expected fields.
3. Do not infer service readiness from metadata access alone; force an actual content read.
4. If a hub uses signed object-store URLs, test from the GPU host itself. A laptop-side success does not prove region-side content access.

## Materialize publication data

Streaming is acceptable for exploratory runs, but reviewer-facing comparisons should use a local immutable token shard or local Parquet snapshot:

- materialize once;
- record source revision and file/token checksum;
- use the identical local train/eval sequence for every arm and seed;
- evaluate all final checkpoints again on one fixed offline eval set.

This prevents remote retries, expiring signed URLs, CDN region differences, and repeated eval-loader opens from contaminating reproducibility.

## Durable remote launcher

Do not attach a multi-hour suite to a foreground SSH session. A dropped SSH connection can terminate the child and waste all progress.

Prefer a durable service or tracked scheduler. Example pattern:

```bash
systemd-run \
  --unit=experiment-suite \
  --property=WorkingDirectory=/absolute/repo \
  /bin/bash -c 'set -euo pipefail; for cfg in ...; do python -m trainer --config "$cfg"; done'
```

Follow with:

```bash
journalctl -fu experiment-suite.service
systemctl status experiment-suite.service --no-pager
```

Use non-login `bash -c` unless login-shell initialization is required; login profiles can introduce unrelated setup failures.

## Checkpoint for failure cost, not only artifact policy

For paid long runs, save resumable checkpoints periodically even if only the final checkpoint will be published. Choose an interval that caps acceptable lost GPU cost (for example, every 250–500 steps), then retain only the latest intermediate plus final. Verify that resume restores optimizer, scheduler, scaler, data position, and exact step; otherwise call it a warm restart, not a resume.

## Streaming retry interpretation

A successful retry of the same remote object during evaluation usually affects wall-clock throughput, not model weights. Validate from metrics:

- evaluation completed with a finite result;
- training resumed at the next step;
- neighboring losses remain finite/plausible;
- no optimizer step was duplicated or skipped.

Mark the interval containing the stall as invalid for throughput. Do not silently threshold it away without recording the exclusion rule. If retries exhaust or the process exits, treat the run as interrupted.

Repeated stalls at evaluation boundaries indicate the eval iterator is reopening remote content. Fix the workflow by using a local fixed eval set rather than accepting recurring network dependence.

## Live-status commands

Before giving a user a hard-coded log path, inspect the currently active process. Sequential suites may already have advanced to the next run. Prefer the durable service journal. If deriving a run directory dynamically, select the actual Python trainer process and exclude the parent shell whose command line may contain every queued config.

On paid hardware, respond operationally: current run, current step, finite/non-finite state, ETA, and the exact command to follow logs. Avoid long explanations while the GPU is idle or blocked.

## Exact throughput optimizations

Before changing architecture semantics, remove repeated equivalent work:

- precompute deterministic token features once per model forward when every layer uses the same tensor;
- fuse independent same-input linear projections by concatenating weights, one GEMM, then split outputs;
- preserve separate parameters and add numerical equivalence tests;
- benchmark median stable throughput against the matched control after warm-up.

These optimizations can recover throughput without changing the ablation question.
