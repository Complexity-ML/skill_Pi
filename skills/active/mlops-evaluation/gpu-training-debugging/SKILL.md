---
name: gpu-training-debugging
description: Diagnose numerical failures and throughput regressions in paid GPU training runs using cost-aware, falsifiable differential experiments before committing to full-budget runs.
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

# GPU Training Debugging

Use this skill when a GPU training run develops NaNs, diverges only under compilation, loses expected throughput, or differs from an earlier accelerator run.

## Operating principle

Treat paid accelerator time as a hard constraint. A process exiting with code 0 is not a successful training run if its loss, gradients, gates, or weights became non-finite. Stop invalid or materially underperforming runs immediately; do not let a full-budget run continue merely to collect a complete CSV.

Be direct with the user: report the measured regression, stop the waste, and move to the smallest decisive experiment. Avoid long explanations while the paid GPU is idle.

## Fail-closed launch sequence

1. Verify the exact source commit, resolved config, Python/PyTorch/Triton/CUDA/driver versions, GPU model, tokenizer checksum, and parameter count.
2. Run architecture tests, including causality/cache tests where applicable.
3. Run a 2–12 step numerical probe with per-step logging.
4. Run a 100–200 step throughput smoke only after the numerical probe stays finite.
5. Compute throughput from repeated post-warmup samples (median and mean); never use a single peak as the headline.
6. Start a full-budget run only if numerical and throughput gates pass.
7. Save the resolved config, metrics, final checkpoint, source hash, environment manifest, and learned control/gate values.

## Budget identity before performance triage

Before calling a run slow, stuck, invalid, or too expensive, reconcile the scientific budget from the resolved launch command rather than from the model label or run name:

1. Distinguish **parameter count** from **training-token budget**. A “100M run” may mean a 100M-parameter model, 100M training tokens, or both; never infer one from the other.
2. Compute effective tokens per optimizer step as `micro_batch_per_gpu × world_size × gradient_accumulation_steps × sequence_length`.
3. Compute total tokens as `tokens_per_optimizer_step × optimizer_steps` and compare it with the intended protocol and historical run.
4. Convert measured seconds/step into both tokens/second and whole-run ETA. A large seconds/step value can be normal when each optimizer step contains several accumulated micro-batches and over one million tokens.
5. Treat a 10× discrepancy in steps or total tokens as a launch-budget bug, not a throughput regression. Stop the wrong-budget run, correct the manifest, and relaunch under an unambiguous run name.
6. Only after budget identity matches should kernel-path, utilization, dataloader, or communication profiling determine whether throughput is actually regressed.

Launchers for paid runs should print and test all four quantities: parameter count, tokens/step, optimizer steps, and total tokens. Include the token budget in the run prefix where practical, and add a test that rejects stale prefixes or step counts after protocol changes.

See `references/training-budget-runtime-reconciliation.md` for a worked 100M-parameter/100M-token example and the failure pattern where 100 steps accidentally became 954.

## Numerical differential matrix

Change one axis at a time, using identical initial weights and batches whenever possible:

- eager vs compiled;
- custom kernels on vs off;
- learning rate zero vs nonzero;
- forward only vs backward vs optimizer step;
- small shape vs exact production shape;
- dense control vs suspect module;
- tied/shared parameters vs independent parameters;
- compile modes and Python/runtime versions only after the architecture differential is known.

Inspect finiteness at boundaries:

1. loss;
2. gradient entering the compiled model output;
3. each parameter gradient immediately after backward;
4. parameters immediately after optimizer step.

This distinguishes bad data/forward, loss backward, compiled model backward, and optimizer corruption.

## Root-cause standard

A differential only identifies a suspect. Do not call it the root cause until a targeted intervention makes the original exact-shape reproducer pass. If an intervention fails, explicitly retract the hypothesis and update the matrix.

After roughly three falsified code-level interventions, stop layering speculative patches. Choose a safe fallback (often eager), profile the real bottleneck, or change the runtime stack in an isolated environment. Keep the GPU productive only with scientifically valid work.

## Throughput discipline

Compare only matched measurements:

- same GPU model and GPU count;
- same eager/compile mode;
- same precision, batch, sequence length, loss backend, kernels, data path, and warm-up exclusion;
- same evaluation/checkpoint interference policy;
- same effective token budget and reporting checkpoints when loss and speed share a table.

Never compare a compiled run that produced NaNs against a valid eager run, or an H100/B200 result against an H200/RTX result, as if they were controlled. A generic capability line such as `custom_triton=true` does **not** prove that the intended kernel ran: log the concrete dispatch path (for example, CGGR versus a masked dense fallback) and verify its import/capability before interpreting architecture throughput.

When reviewer-requested controls must run on different hardware or at a reduced token budget:

1. Preserve the original full-budget table/panel unchanged.
2. Create a separately labeled short-budget/hardware panel.
3. Rerun at least two bridge controls (the primary method and a dense control) alongside the new variants on the same hardware, data shard, seed, batch, and budget.
4. Compare train/eval losses only within that matched panel; do not compare absolute short-budget losses against full-budget rows.
5. Omit throughput from the short panel, or label it explicitly as hardware-specific diagnostic throughput and state that it is not comparable across panels.
6. If reporting checkpoints are scaled (for example 750/950 to 75/95), label this as a deliberately shortened protocol, not an equivalent full-budget result.

Profile structural overhead before changing architecture semantics. Prefer exact optimizations such as fusing adjacent projections, hoisting identical per-layer computations, removing redundant materialization, and preserving parameter/state-dict meaning. Add equivalence tests before benchmarking.

See `references/matched-ablation-panels.md` for a compact reporting template for full-budget results plus short-budget reviewer controls.

## Short-smoke scheduling pitfall

A percentage-based warmup compresses when total smoke steps are reduced. A learning rate stable for a 3,000-step run may be reached in only a few smoke steps and cause a misleading divergence. Router schedules (top-k blend, gates, balancing coefficients) compress for the same reason. For throughput-only smokes, use a clearly labeled low smoke LR or preserve the production scheduler horizon. Never transfer the smoke LR into the scientific run silently.

A checkpoint from a compressed short-budget schedule is not a valid resume point for the full-budget run: LR decay and router/gate schedules have already reached late-training values too early. Use the short run only as a promotion filter, then restart the promoted full-budget candidate from step zero with the full scheduler horizon.

For cost-aware promotion, rank all candidates against matched bridge controls at the short budget using raw task loss (separate from auxiliary-loss contributions), evaluation loss, balance health, and matched throughput. Promote only the clear winner. When full matched controls are expensive, run the promoted candidate alone first; launch full bridge controls only if its full-horizon trajectory remains promising. Do not claim a reviewer-ready cross-run win until data/evaluation protocol and controls are matched.

## Router-ablation leakage audit

When comparing lexical, learned, and dense routing controls, audit every router-specific input before launch rather than trusting the model label:

1. Trace corpus-frequency tensors, token IDs, routing maps, auxiliary losses, and selection biases from data preparation through config construction into each module.
2. A learned hidden-state router must not receive or precompute corpus-frequency tables merely because a shared trainer supports lexical routing. Even if the module currently ignores the tensor, exclude it from the resolved config and logs so the control is unambiguous and cannot acquire accidental dependence later.
3. Dense controls must likewise skip lexical-routing preprocessing.
4. Frequency-aware lexical controls may use frequencies only when the mechanism explicitly requires them. Label them as **corpus-derived from the fixed shard**, never “hardcoded Zipf,” and record the shard checksum/source revision. Count frequencies in integer space (`int64` or an exact `bincount`), not float32: unit increments stop being exact above 2^24 and can silently undercount common tokens in billion-token corpora. Verify `sum(counts)` against the indexed source-token count before constructing a routing table; use float64 for CPU load-balancing calculations when large counts are converted.
5. Add positive and negative tests: frequency-aware lexical strategies receive counts; learned, dense, random, and frequency-independent strategies do not. Add an exact-count test that asserts integer dtype, per-token counts, and total sum.
6. If leakage-like preprocessing or an inexact count appears in a paid run, determine whether it affected math. Regardless, restart affected variants from clean run directories after removing it so manifests and logs remain reviewer-defensible. Preserve already-completed variants only when tracing proves they never consumed the bad input; relaunch the remaining subset explicitly rather than rerunning or overwriting valid controls.
7. Treat generic resolved-config summaries as untrusted presentation until checked against the instantiated module. Shared trainers often retain irrelevant fields (shared width, router mode, expert count, gates) for dense controls. Verify the concrete module class and named parameters before stopping a run, then condition summaries on architecture so unused fields are not printed.
8. Distinguish missing telemetry from pathological routing. `NaN` expert shares or a default dead-expert count can mean collection is disabled, not that experts are dead. Record an explicit telemetry-enabled flag or emit `not_collected`; never infer collapse from placeholder metrics.

See `references/router-ablation-input-isolation.md` for the concrete audit pattern, exact-count checks, architecture-log checks, and clean-restart checklist.

## Durable paid-run execution

Long remote runs must survive SSH and chat/session closure. Launch them under a remote service manager (for example a transient `systemd-run` unit) with an explicit working directory, environment, run prefix, and persistent logfile. Then:

1. verify the unit is active and inspect its exact child command;
2. verify the resolved trainer summary before accepting GPU spend;
3. provide separate commands for live log, GPU utilization, and service status;
4. make clear that closing `tail -f`, SSH, or the chat does not stop the remote service;
5. stop invalid units immediately and verify VRAM returns to zero;
6. use a new service/log name for a corrected launch, and delete only partial artifacts belonging to affected variants;
7. allow a run-subset override so completed valid variants can be preserved while only failed/invalid controls are relaunched.

Do not treat shell prompt/plugin warnings from the local SSH client as evidence that the remote training service failed; inspect remote unit state, log progress, process tree, and GPU memory directly.

## Repository safety

Before staging a fix in a dirty workspace, inspect the per-file diff against `HEAD`. Stage only intended hunks; a whole-file `git add` can accidentally commit pre-existing user work. If this happens, separate and restore the unrelated work before continuing.

## Verification checklist

- [ ] Parameter count, effective tokens/step, optimizer steps, total tokens, and reporting checkpoints match the intended protocol.
- [ ] Exact reproducer fails before the fix.
- [ ] Exact reproducer passes after the fix.
- [ ] Loss, gradients, parameters, and gates remain finite beyond the original failure step.
- [ ] Architecture/unit tests pass.
- [ ] Corpus-frequency inputs are isolated to declared lexical controls; exact count totals match the indexed source range.
- [ ] Concrete kernel/dispatch path is logged, not inferred from generic capability flags.
- [ ] Post-warmup throughput distribution is reported on matched hardware/software.
- [ ] Short-budget results are labeled as promotion filters and are not resumed into a full compressed schedule.
- [ ] Full run is launched only after explicit numerical and speed gates.
- [ ] Invalid/obsolete GPU processes are stopped and VRAM is released.
- [ ] Corrected remote runs use durable service/log names and preserve only verified unaffected artifacts.

## Session case studies

See `references/compiled-shared-path-case-study.md` for a compact example of debugging second-step NaNs and separating numerical correctness from throughput optimization.
