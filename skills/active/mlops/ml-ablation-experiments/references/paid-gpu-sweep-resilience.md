# Paid GPU sweep resilience

Lessons for remote/paid ablation launchers where a failed loop wastes expensive idle time.

## Failure mode

A run can complete training, save checkpoint, and write `metrics.csv`, then abort during Python/CUDA/PyTorch teardown with a message like:

```text
terminate called without an active exception
Aborted (core dumped)
```

If the launcher is a plain `set -euo pipefail` loop piping through `tee`, this non-zero exit stops the entire sweep even though the run's loss data is usable.

## Robust launcher pattern

For each ablation run:

1. Run the trainer with `set +e` around only that command.
2. Pipe through `tee` but capture the trainer exit with `${PIPESTATUS[0]}`.
3. If exit code is non-zero:
   - Continue only if the expected `metrics.csv` exists and contains the intended final step.
   - Otherwise stop immediately.
4. Generate/update a loss-only summary CSV after each completed run.
5. Copy/mirror metrics CSVs promptly from the paid host; do not rely on checkpoints as proof when the requested artifact is losses.

Skeleton:

```bash
set +e
python train.py ... 2>&1 | tee "$log_path"
rc=${PIPESTATUS[0]}
set -e
if [[ $rc -ne 0 ]]; then
  if python scripts/check_metrics_complete.py "$metrics_path" "$expected_step"; then
    echo "WARNING: trainer exited rc=$rc after complete metrics; continuing"
  else
    echo "ERROR: run failed before complete metrics" >&2
    exit "$rc"
  fi
fi
python scripts/write_loss_summary.py
```

## User-facing behavior

When the user is paying for GPU time:

- Be terse and action-first.
- Secure `metrics.csv` / loss summaries immediately.
- Do not emphasize checkpoints unless explicitly asked; checkpoints are secondary to loss curves for ablation comparison.
- For exploratory comparison sweeps, default to no checkpointing (`--save-steps 0`, `--save-total-limit 0`, temp save dirs) unless the user asks for artifacts or resumability.
- If checkpoints were accidentally created and the user only wants losses, delete them promptly after confirming metrics are saved.
- If an automated sweep stops early, resume from the next missing run and make the launcher resilient before relaunching.
- If switching to faster paid hardware, stop the old paid process first; if SSH/API access is down, state that the old process state is uncertain instead of implying it is stopped.
