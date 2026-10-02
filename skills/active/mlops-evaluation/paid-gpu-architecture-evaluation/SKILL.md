---
name: paid-gpu-architecture-evaluation
description: Run controlled ML architecture comparisons on paid accelerators with fail-closed numerics, matched throughput, checkpoints, ablations, and cost-aware sequencing.
metadata:
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Legacy Hermes references used in the source:
  - `memory` → explicitly requested persistent Markdown notes.
- There is no default Pi `memory` tool. Do not automatically store personal or sensitive information. Ask before creating persistent notes.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Paid GPU Architecture Evaluation

Use this skill when comparing model architectures or ablations on rented GPUs where validity, throughput, and paid time all matter.

## Operating principles

1. **Keep the accelerator useful, not merely busy.** Stop runs immediately when they are numerically invalid, scientifically confounded, or materially below the accepted throughput floor.
2. **Report status before exposition.** State active run, step, finite loss, throughput, ETA, and next action. Provide a copy-ready monitoring command whenever the user asks how to follow progress.
3. **Match before claiming.** Keep GPU, batch, sequence length, precision, optimizer, LR schedule, data order, tokenizer, evaluation set, kernels, warm-up, and token budget identical unless the changed factor is the ablation.
4. **Fail closed.** A process exit code of zero does not validate a run if loss, gradients, gates, or parameters became non-finite.
5. **Separate descriptive history from controlled evidence.** Never mix throughput from different GPU types or code snapshots in one architectural comparison.

## Workflow

### 1. Freeze provenance

- Work from the reviewed primary branch when requested; avoid branch/worktree traffic during paid execution.
- Record source commit, resolved config, parameter count, tokenizer checksum, seed, software versions, GPU/driver, and exact token count.
- Preserve existing unrelated workspace modifications; stage only task files.

### 2. Validate cheaply

Before a long run:

1. Run focused causal/numerical tests.
2. Run a 2–3 update reproducer for failures that appear after optimizer steps.
3. Run a 100–200 step smoke with representative batch/sequence dimensions.
4. Verify finite loss and trainable controls, no OOM, expected backend, and stable post-warm-up throughput.
5. Compare throughput by median over stable intervals, not a single final point. Exclude documented evaluation, checkpoint, compile, cache-maintenance, and network-stall intervals.

### 3. Debug regressions by differential isolation

Change one factor per probe:

- eager vs compiled;
- custom kernels on vs off;
- dense component vs specialized component;
- tied vs independent parameters;
- first backward vs second backward;
- gradients before optimizer step vs parameters after optimizer step;
- production tensor shape vs reduced shape.

Inspect the first non-finite tensor and distinguish forward, loss gradient, compiled backward, and optimizer corruption. After roughly three falsified implementation fixes, stop speculative patching; use the validated fallback or isolate the problematic subgraph outside compilation.

### 4. Optimize or extend without weakening the baseline

Prefer mathematically exact transformations:

- hoist deterministic per-token work shared by every layer;
- fuse adjacent projections into one GEMM while keeping separate parameter slices;
- avoid recomputing values multiplied by a fixed zero gate;
- verify output equivalence with tests before benchmarking.

For a candidate intended to beat a strong baseline, prefer a **baseline-preserving residual contract** over replacing the proven operator:

1. Keep the baseline score/value path unchanged.
2. Add the new mechanism as a separately gated score or residual whose zero setting is mathematically the baseline.
3. Preserve the baseline's explicit attention scale when feature channels are concatenated; widening Q/K must not silently rescale contextual logits.
4. Keep values contextual unless lexical values are the isolated hypothesis.
5. Match total parameters by reallocating width elsewhere.
6. Test optimizer-level movement after warmup. A synthetic nonzero gradient is insufficient when the real lexical source or first-step LR starts at zero.
7. If a learned lexical table initializes at zero, distinguish two bootstraps: a deterministic token code permits a zero gate to move, while a small nonzero gate permits the learned table to move while the zero table still leaves the initial operator exactly at baseline. Test both the initial output equivalence and which parameter actually receives gradient.
8. Treat arbitrary token-ID hashes as a real ablation, not a harmless implementation detail. They can help early optimization yet overfit lexical identity later; compare a learned-only key path before concluding that lexical scores themselves fail.
9. When parameter matching reallocates capacity away from the baseline (for example by narrowing its MLP), run a temporary unadjusted-capacity diagnostic alongside the strict matched arm. This separates mechanism failure from compensation damage. Only the matched arm supports the final architecture claim.

Re-run both arms after any shared-path optimization. Do not compare a newly optimized arm against stale measurements of the control.

### 5. Run the evidence ladder

1. Primary matched seed.
2. Mechanism-off ablations with parameters retained and controls frozen.
3. **Use full-budget trajectories and learned controls to choose structural ablations before adding seeds.** If a candidate wins early but loses late, inspect every matched evaluation checkpoint rather than only the endpoint. Then inspect per-layer gates from the final checkpoint with `weights_only=True`. When upper-layer gates collapse toward zero while lower layers remain active, test bottom-$k$ placement (for example 4, then 2, then 1 layers) against the already completed matched control before spending on multi-seed replication. This is evidence-guided depth search, not permission to cherry-pick an intermediate checkpoint.
4. If the primary result survives, replicate primary/control on at least two additional seeds. A full-budget loss on the first matched seed is a valid rejection gate for an expensive candidate; do not run extra seeds merely to rescue a losing mechanism.
5. Compute per-seed differences plus mean and sample standard deviation; report paired differences and an interval, not just win count or pooled endpoints.
6. Save final checkpoints and inspect learned gates/controls directly from checkpoint state. Prefer `torch.load(..., weights_only=True)` for self-generated state inspection; request explicit approval before unsafe pickle loading.

### 6. Deploy and orchestrate remote runs durably

- Read the provider instance's own agent/operations guide before installing, exposing services, or choosing a process manager. Container images may require `supervisor` rather than `systemd`, and `/workspace` is not necessarily a persistent volume.
- Make Git the source of truth for code. Prefer a reviewed commit on the intended branch, then clone/fetch/reset that commit remotely. Do not repeatedly `rsync` a dirty framework tree. If the needed patch is uncommitted, obtain explicit permission to commit/push or transfer one small patch; preserve unrelated local changes.
- Download large pinned public datasets directly on the accelerator host from their authoritative repository instead of relaying them through a laptop. Pin revision and file path, then verify SHA-256 before training. Use laptop transfer only for genuinely local/private artifacts.
- Do not rely on a foreground SSH connection or a local background terminal to own a paid multi-run chain. A dropped controlling connection can terminate the remote child and waste all work since the last checkpoint.
- **Separate monitor health from job health.** A local poller exiting because SSH, shell startup, or status parsing failed does not imply the remote training services failed. Immediately query the provider-supported service manager without suppressing stderr, then inspect GPU processes and structured metrics. Report these as three distinct states: monitor, transport, and remote job.
- Make optional local monitors retry transient SSH failures with an explicit timeout instead of exiting on the first nonzero SSH status. Their only role is notification; remote supervisor state and artifacts remain authoritative. Do not hide SSH stderr in the only diagnostic path.
- Use the provider-supported remote service manager (`supervisor`, `systemd-run`, or durable job API). For finite scientific runs, disable automatic restart unless the wrapper can prove a partial run is safely resumable; an abnormal exit after final artifact writing must never silently launch a duplicate full run.
- On a multi-GPU rental, independent matched arms may run concurrently one GPU each to minimize paid wall time. Pin `CUDA_VISIBLE_DEVICES` per process and keep each arm single-process when DDP would change global batch/token budget. Check for shared I/O contention before interpreting throughput.
- Preflight data access, tokenizer loading, one train/eval batch, full production batch/sequence memory, and expected CUDA/Flash backend under the **same environment and service context** as the real job. Service processes may not inherit interactive-shell variables.
- Save intermediate checkpoints at a cadence that bounds acceptable paid-work loss. Final-only checkpointing is unsuitable for long chains even when each individual run is short.
- Progress bars with carriage returns may appear as binary/blob records in service logs; use the run's structured metrics CSV for readable live progress.
- If the instance has no persistent volume, treat every remote file as disposable: mirror metrics/configs/checkpoints needed for claims before stop, recycle, or destroy.

### 7. Handle streaming-data faults and build an offline escape hatch

- Automatic retry of the same remote object is acceptable if training/evaluation continues and the metric completes.
- Mark retry intervals as throughput outliers; do not count them in speed summaries.
- If retries become systemic, stop launching training and obtain the exact pinned shard locally. A native repository downloader may use a different transfer path than a failing HTTP `resolve` URL.
- Verify local shard byte size, row count/schema, and SHA-256; read at least one train batch and one eval batch before relaunching.
- Make local data selection explicit (for example, a documented environment variable) while preserving the remote default. Record repository, config, revision, shard path, and checksum in the artifact manifest.
- For publication, re-evaluate all checkpoints on one local, checksummed, fixed evaluation corpus. Streaming evaluation is operational evidence, not the final reproducibility artifact.

### 8. Archive before releasing the accelerator

- Distinguish **a run finishing** from **the user's search objective finishing**. If the standing objective is still unmet (for example, “continue until the candidate beats GQA”), archive the completed arm and move to the next evidence-driven ablation or ask for a decision; do not stop the rental merely because one pair completed.
- Copy resolved configs, metrics, checkpoints, logs/manifests, and any irreplaceable local dataset shard before terminating the instance.
- Use resumable transfers. Probe the local transfer-tool version first: older macOS `rsync` supports `--progress` but not newer `--info=progress2`.
- Hash large artifacts independently on source and destination and compare every digest. A successful transfer exit code alone is not scientific verification.
- Confirm the remote training service is inactive and no accelerator process remains. Tell the user to stop/terminate the provider instance; an OS shutdown may not stop billing.

### 9. Publication gate

Publish only after:

- multi-seed matched results survive;
- mechanism claims are supported by explicit ablations;
- final checkpoints/configs/metrics/checksums exist;
- tables are generated from archived data;
- claims distinguish quality gains from throughput costs;
- anonymous package and PDFs are rebuilt and inspected;
- the human submitter reviews every changed line and result.

## Monitoring commands

Give commands that show process, GPU memory, and the active run's `metrics.csv`. Before giving a hard-coded run path, query the live child process and verify which config is active; a sequential chain may already have advanced. Dynamic monitors must parse the actual trainer process rather than the parent shell command (which may mention every queued config), and must handle an empty result during run transitions without attempting `runs//metrics.csv`. Prefer `watch -n 2` over claiming stdout is available when the process was not redirected. State clearly when only metrics—not console output—are recoverable. For service-managed jobs, use `journalctl` for lifecycle/errors and structured CSV for progress bars that journal may encode as blobs.

## Reference notes

- See `references/contextual-wrv-h200.md` for a concrete case study of differential debugging, exact optimizations, and ablation interpretation.
- See `references/baseline-preserving-lexical-score.md` for the failed W/R/V replacement/depth search and the FlashAttention-compatible lexical-score residual contract that preserves exact GQA at a zero gate.
