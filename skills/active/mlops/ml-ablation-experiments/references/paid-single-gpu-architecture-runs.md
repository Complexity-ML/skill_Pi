# Paid single-GPU architecture run: production checklist

Use this pattern when moving a locally validated language-model ablation to a paid H100/H200/B200 instance.

## Before provisioning

- Inspect current public price and distinguish spot from fixed/on-demand pricing.
- Never provision or cross from smoke to a long paid run without explicit approval of GPU, hourly rate, measured ETA, and cost range.
- Keep the candidate and baseline token budgets exact; compute steps from `batch × sequence × world_size`.

## Already-provisioned instances: minimize paid idle

When the user provides access to an instance that is already billing, switch from planning to execution immediately.

1. Report the hourly and per-minute rate concisely, then verify SSH, GPU identity, VRAM, driver, disk, RAM, and current GPU utilization in the same turn.
2. Prefer a reproducible Git deployment over ad-hoc file transfer. If the user requests a main-only workflow, commit the reviewed work, preserve dirty changes in the primary worktree, merge into `main`, push `origin/main`, clone `main` remotely, and verify the remote commit hash. Do not leave the paid host on an experiment branch after that request.
3. If `main` is checked out in another worktree, inspect that worktree before merging. Use Git autostash to preserve tracked local edits, resolve any reapplication conflict deliberately, and return preserved edits to their original unstaged state before pushing the merge commit.
4. Execute bootstrap commands explicitly through `ssh host '...'`. For background installs, the tracked local process must wrap the SSH command; otherwise an apparently remote install may accidentally execute on the controller machine.
5. Verify every expensive transition: remote clone branch/hash, environment location, PyTorch/CUDA visibility, target tests, then bounded smoke. Do not let setup narration consume paid minutes.
6. If an operation is blocked or interrupted, state that immediately and switch to the user's preferred reproducible path rather than repeatedly retrying a flagged transfer command.

## Target-device smoke ladder

1. Verify GPU identity, VRAM, driver/runtime, disk, RAM, and that no process owns the GPU.
2. Test architecture invariants on the target host (e.g. expected mixer class and zero QKV parameters).
3. Run a tiny forward/backward/optimizer smoke.
4. Increase to the intended sequence length with conservative batch sizes; monitor peak VRAM externally.
5. Treat the exact-vocabulary cross-entropy as a separate memory bottleneck. A model may fit while the `[chunk_tokens, vocab]` logits allocation OOMs. Reduce batch and/or loss chunk size rather than changing the scientific token budget.
6. Measure stabilized throughput after warm-up; first-step throughput includes allocation/compilation and must not drive ETA.
7. Repeat on the real streaming dataset. Synthetic throughput is only a hardware ceiling.

## Streaming data invariants

- Train and evaluation documents must be disjoint by a deterministic source-document rule, not by creating two iterators over the same stream.
- Make the held-out selection dense enough that evaluation does not scan an excessive number of remote documents.
- Verify the exact tokenizer and vocabulary explicitly; a synthetic smoke may set vocab size directly, but headline training may not use fake data or a fake tokenizer.
- Streaming-library teardown errors after a complete metrics artifact are not training failures. Preserve metrics first and judge completion from the intended final step.

## Durable paid run

- Launch through a durable remote service (`systemd` or an equivalent scheduler), not an interactive SSH shell.
- Write a continuous log, realized config, environment manifest, and metrics CSV.
- For a headline run, retain one final checkpoint when downstream evaluation requires it; avoid intermediate checkpoint churn unless interruption/resume risk justifies it.
- Add a silent watchdog that alerts once on failure or completion.
- Never start another paid condition automatically.

## Claims

- Separate matched-token quality from wall-clock efficiency.
- A single candidate run is not a paper comparison. At minimum, smoke and budget the baseline before claiming superiority.
- Lock unfinished paper table cells to explicit `PENDING` macros so intermediate metrics cannot become headline claims accidentally.
