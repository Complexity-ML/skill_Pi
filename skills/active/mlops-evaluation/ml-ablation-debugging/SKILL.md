---
name: ml-ablation-debugging
description: Design, run, and debug ML architecture ablations with clean controls, especially routing/MoE experiments.
license: MIT
metadata:
  hermes:
    tags:
    - mlops
    - evaluation
    - ablations
    - routing
    - moe
    - experiments
    related_skills:
    - test-driven-development
    - systematic-debugging
    - weights-and-biases
  hermes_frontmatter:
    version: 1.0.0
    author: Hermes Agent
    platforms:
    - linux
    - macos
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

# ML Ablation Debugging

## When to Use

Use this skill when creating or debugging model-training ablations, especially:

- routing strategy controls such as Zipf vs random/modulo/round-robin
- shared-vs-routed expert comparisons
- dense residual / shared-only controls
- local smoke runs before expensive GPU training
- reviewer-facing experimental evidence where confounded controls are dangerous

## Core Principle

A run name is not evidence. Verify that the code path, config, model parameters, routing tables, gates, schedules, token budget, and metrics match what the run name claims.

## Workflow

1. **Define the scientific question first.**
   - Example: “Does Zipf-balanced lexical routing beat random/modulo controls?”
   - Avoid adding new architectural hypotheses just because they are easy to code.

2. **Inspect the current architecture before inventing new knobs.**
   - Trace where shared branches, routed branches, gates, and top-k routing actually sit in the forward pass.
   - If the user questions an assumption, stop and read the code before implementing.
   - Lock the intervention class the user selected. If the request is to upgrade an existing attention/context mechanism, improve that mechanism first; do not silently substitute auxiliary curricula, frozen-adapter grafts, extra injection points, or a reproduction of an already losing model.
   - Prefer the smallest interpretable architectural delta before a multi-axis redesign. Example: add learned contextual read/write projections to an existing lexical associative memory and initialize their blend neutrally; test this before introducing multi-head/multi-timescale state.

3. **Use TDD for ablation controls.**
   - Add a failing test proving the new config/parser/model behavior is missing.
   - For routing, test the actual mapping tensors, not just parser acceptance.
   - For top-k routing, test every route, not only the primary route.

4. **Verify parity before running.**
   - Parameter count, active width, shared/routed capacity, gates, top-k schedule, optimizer, token budget, batch size, sequence length, dataset/tokenizer, and evaluation cadence should be explicit.
   - When reproducing an archived throughput result, diff the live command against the archived `run_config.json` before blaming the architecture. Check gradient checkpointing, custom-kernel mode, active Triton telemetry, compile mode, precision, loss backend, and warm-up window. Read the source table first when the user identifies a control by an approximate speed; never assign the number to a mechanism from memory.
   - Use `torch.device('meta')` where possible to compute parameter counts without allocating the full model.
   - Treat logs as part of experimental correctness: derive architecture-specific summaries and progress fields from capabilities found on the built model, not from generic parser defaults. A displayed control that has no setter, parameter, or forward path is false telemetry even if training itself is correct.
   - Add negative smoke-log assertions: fields for inactive model families and optimizers must be absent.

5. **Externalize architecture iteration, but benchmark the actual blocking metric first.**
   - Put an experimental mechanism behind the same runtime contract as production (inputs, outputs, fixed state), and iterate there before wiring it into the main model.
   - Preserve an exact neutral setting that reproduces the old mechanism; test this bit-for-bit before activating the experiment.
   - Start with the metric that caused the production model to lose. If the blocker is held-out language loss, run the matched language proxy before spending time foregrounding already-solved synthetic recall/induction probes. Keep mechanistic probes as secondary sanity checks.
   - Once the standalone mechanism wins, integrate only that delta into the main model and re-check parameter parity.
   - Treat miniature language models as debugging screens, not launch gates, when scale reversals have occurred. Synthetic recall, 500-step proxies, and even long miniature proxies cannot establish full-scale FineWeb superiority; the decisive evidence is the matched production-scale held-out curve.
   - For fixed-state fast-weight attention, inspect effective write/decay rates, state/read norms, recurrence precision, and learned output suppression. High write plus near-unit decay plus a tiny output gate suggests additive-memory interference; test a bounded residual delta-write rule before adding surrounding capacity.
   - Do not label a learned hidden-state projection “semantic” unless semantic behavior is directly operationalized and measured. For lexical mechanisms, keep both implementation and claims lexical. Deterministic multi-order token-context fingerprints are honest lexical mechanisms, but not automatically useful: splitting rank across `1/2/4/8` memories can reduce capacity and multiply Delta-scan cost. Reject this branch when the matched proxy loses to both GQA and single-state Stable Delta.
   - After bounded Delta fixes additive interference but remains behind GQA, temporal organization is a valid diagnostic but not a presumed upgrade. Multi-timescale Delta can preserve the address/full matrix while partitioning value columns and learning bounded decay/write rates per group; batch the groups into one triangular solve and require full/incremental equivalence plus production-shape backward throughput. Treat a miniature-proxy win as non-authorizing: this design can learn clearly distinct horizons yet still lose to single-timescale Stable Delta at production scale because fixed channel partitioning constrains capacity.
   - After bounded Delta fixes additive interference but remains behind GQA, preserve matrix capacity before adding heads or rank partitions. Test diagonal causal collision-load normalization as a fixed-state anti-interference control; if investigating lexical read/write, distinguish lexical addresses from hidden-state values and compare against deterministic token-identity value codes. Never relabel deterministic lexical codes, hidden projections, or token modulation tables as semantic representations. Production evidence can reverse the lexical-value proxy: if pure token-code values regress at scale, retain contextual hidden values and restrict any lexical forge to read/write routing. A forge candidate must preserve the baseline contextual path and be exactly neutral at initialization; removing contextual routing is a confounded ablation, not a clean forge test.
   - For token-conditioned lexical forges, preserve a shared read/write coordinate system. Independent per-token R/W heads, gated antisymmetric direction corrections, and neutral-gated contextual-value modulation can all add expressivity while worsening loss or missing the effect-size gate. When successive clean forge extensions fail a predeclared gate, stop: retain the simplest production-validated forge, archive the negative ablations, and move loss work to an orthogonal mechanism. If combining the retained forge with a proven collision normalizer, compare against a collision-only arm using the same lexical MLP/table and verify the three-component state full/incrementally.
   - When fixed-state WVR still trails QKV independent of KV-cache considerations, frame the gap as compressed-memory occurrence selection versus per-instance retrieval. Before adding heads, check whether contextual occurrence addressing already exists. If it does, test only the missing factor as a neutral-gated control—for example, a deterministic absolute-position signature with one fixed-state position counter—and require gate-off baseline equality plus full/incremental counter equivalence. Keep cache/state complexity and held-out language quality as separate comparisons.
   - Diagnose train-loss spikes against an exact-step baseline on the same data stream. Matching spike positions/amplitudes and matching 10/20/30-step recovery indicate hard batches, not candidate-specific attention instability.
   - For minimal-attention studies, first test one layer to estimate marginal effect, then test the maximum compatible count while preserving protected substrate/context layers. If that arm improves substantially but remains behind, distinguish substrate limitation from attention limitation with a parameter-matched true maximum (for example 10/10 attention with no protected WVR layers) before redesigning. If a maximum beats the dense control, descend by binary search; if the true maximum does not, redesign the attention rather than spending on every intermediate count. Before calling a remaining gap architectural, match the dense control's per-head normalization path exactly: RMSNorm on contextual read/write heads before RoPE can dominate the result even when head counts, scaling, and FlashAttention are otherwise matched. If a lexical residual starts at zero, do not credit it for a win without gate telemetry and a checkpoint ON/OFF ablation.

6. **Run a numerical gate, then a tiny smoke.**
   - Before compiled paid-GPU training, run at least three real-shape optimizer updates and assert finite loss, output gradients, parameter gradients, parameters, and gates after every update. A one-step check misses graph-reuse failures that appear on update two.
   - If eager is finite and compiled training is not, localize with a one-variable differential matrix: compile mode, custom kernels, frozen (`lr=0`) update, dense control, real vs reduced shape, and tied vs independent state. Inspect boundaries before and after `optimizer.step()` rather than guessing from the final NaN.
   - Never finish or quote throughput from a numerically invalid smoke. Add a fail-fast non-finite guard to the production loop.
   - Example: 2 steps can prove construction/parser/data/logging, but it does not replace the three-update numerical gate.
   - Then run local diagnostics (e.g. 200–1000 steps), clearly labeled as diagnostic only.
   - A short pilot may authorize a long run only when its optimizer and scheduler are configured with the long run's full horizon. A cosine schedule that ends at pilot step 500 is not predictive of step 500 inside a 3052-step run.
   - On rented hardware, use the branch the user explicitly requested, push it, clone the exact commit, and report that commit. Do not invent an experimental-branch transfer workflow when the user asked for `main`.
   - In a workspace with pre-existing user changes, inspect `git diff --cached` before every commit. Stage only the intended paths or hunks; never assume a tracked file contains only the current fix. If an unrelated local change is accidentally staged, stop and restore its uncommitted state before pushing.

7. **Summarize metrics mechanically.**
   - Read `metrics.csv`; report final train loss, final eval loss, best eval loss, throughput, and deltas vs baseline/control.
   - Do not over-interpret short local runs as paper evidence.
   - Match the scheduler horizon as well as the nominal step: step 250 of a 250-step cosine run is not equivalent to step 250 of a 3052-step run.
   - Separate mechanistic capacity under direct supervision, emergence after ordinary LM pretraining, and held-out LM quality. Success on one is not evidence for the others.

8. **Validate new residual mechanisms at initialization and after training.**
   - For `base + gate * branch`, test gate initialization rather than injecting a random branch at full strength by default.
   - Log every learned gate/mix and run mechanism ON/OFF checkpoint diagnostics. A low scalar output gate can reveal that a useful address/memory mechanism is being globally throttled.
   - When the user chose to improve the mechanism itself, do not substitute a frozen graft or auxiliary curriculum. First externalize a stronger shared fusion that can select context per token and dimension (for example, GLU-style fusion of hidden state and retrieved state) instead of merely tuning a global scalar.
   - Delete inherited but unused projections before iso-parameter matching; dead parameters can silently consume the candidate's capacity budget.

## Routing-Control Pitfalls

- **Top-k contamination:** when `top_k > 1`, controls can be silently contaminated if the primary route uses the requested strategy but auxiliary routes use the default strategy. Test this explicitly.
  - Bad: `random primary + Zipf-balanced auxiliary` labeled as `random_shared`.
  - Good: random primary and random deterministic auxiliary, distinct per token.
- **Load balance is not the whole story:** Zipf can be perfectly mass-balanced and still underperform because of semantic grouping, shared-branch interaction, gates, or top-k schedule.
- **Short-run surprises are debugging signals:** if random beats Zipf sharply in a smoke/local diagnostic, inspect the config/code path before explaining it as noise.
- **Shared branch interpretation:** keep “global shared expert” free/global unless the architecture already supports a more constrained shared mode. Do not invent pair-shared or other new variants unless the user explicitly chooses that hypothesis.

## Local Diagnostic Pattern

For quick Mac/local checks:

- Use a small local text sample if available.
- Override expensive distributed settings: small `batch_size`, moderate `seq_len`, no checkpoints, frequent eval.
- Keep run names explicit, e.g. `local-200-balanced-100m_zipf_shared`.
- Store logs under a diagnostic directory and metrics under distinct run directories.

Example summary columns:

```text
name,step,train_loss,last_eval_loss,best_eval_loss,tok_s
```

## Before Expensive Runs

Do not launch long 4B+ token ablations until:

- targeted routing/control tests pass
- parameter counts are checked
- a 2-step smoke passes
- local diagnostic results are at least plausible
- any surprising local result has been traced to either a real effect or a fixed bug

For expensive paid-GPU ablation suites:

- **Run the dense/baseline control first** unless the user explicitly chooses another order. This gives an immediate live reference for deciding whether later variants are worth continuing.
- Preflight the exact dataset path by reading real train/eval content from the GPU host before launching. For publication evidence, materialize an immutable local token shard or Parquet snapshot and record its revision/checksum; re-evaluate every final checkpoint on one fixed offline eval set.
- Launch multi-run suites through a durable remote service or scheduler, not a foreground SSH child. Use periodic resumable checkpoints sized to cap acceptable lost rental cost, even when only the final checkpoint will be published.
- When remote data retries succeed, verify finite eval and resumed training, then mark the affected timing interval as excluded throughput with the exclusion rule recorded. Repeated eval-boundary stalls require a local eval set; exhausted retries make the run interrupted.
- Before giving a live-log command, inspect the actual active trainer. A queued parent shell may mention every config and produce a stale run name; prefer `journalctl -fu <service>` for durable services.
- On paid hardware, communicate operationally and briefly: active run, step, finite state, throughput, ETA, and exact follow command. Do not spend idle GPU time on long explanations.
- Disable checkpoints by default when the deliverable is loss curves/tables only (`--save-steps 0`, `--save-total-limit 0`, and a throwaway save dir). Delete accidental checkpoints promptly after confirming metrics are safe.
- Treat `metrics.csv`/loss CSVs as the primary artifact: copy them off the remote machine immediately after each completed run, not only at the end of the full suite.
- Before terminating a rented GPU, evacuate metrics/config/profile first and the checkpoint second; verify local byte size and SHA-256 before telling the user it is safe to shut down.
- Compare throughput only under a matched software path: same precision, compilation mode, warm-up, batch, sequence length, and measurement window. Never present compiled-vs-eager speed as an architectural delta.
- Before changing architecture semantics to chase throughput, remove repeated equivalent work: precompute deterministic shared token features once per forward, and fuse same-input linear projections into one concatenated GEMM followed by a split. Preserve separate parameters, test numerical equivalence, and benchmark median stable throughput.
- If a launcher aborts after writing `metrics.csv` (e.g. CUDA/PyTorch teardown), continue only when the metrics file exists and is non-empty; otherwise stop as a real failure.
- If run order must be changed mid-suite, prefer a small watcher/wrapper that lets the current valuable run finish, kills the next unwanted run as soon as it starts, deletes partial metrics, and relaunches the remaining suite in the corrected order.

## References

- `references/routing-topk-control-contamination.md` — concrete session-derived pitfall and verification pattern for top-k routing ablations.
- `references/architecture-aware-runner-telemetry.md` — capability-driven logging for multi-architecture runners, negative smoke assertions, warning deduplication, and paid-run provenance.
- `references/context-mechanism-ablation-protocol.md` — separates supervised capacity from LM emergence, matches scheduler/compile controls, validates residual gates, publication figures, and remote artifact evacuation.
- `references/shared-associative-attention-long-horizon.md` — externalized mechanism iteration, decisive-metric ordering, static compile-path selection, teardown validation, and the scheduler-horizon failure that invalidated a promising short pilot.
- `references/fast-weight-attention-stability.md` — checkpoint diagnostics for additive-memory interference, bounded delta-write invariants, FP32 recurrence checks, and the failure of miniature proxies to predict full-scale FineWeb ranking.
- `references/lexical-delta-attention.md` — exact chunk-vectorized Delta recurrence, stability invariants, deterministic multi-order lexical addressing, production-shape chunk sweeps, and exact-step spike diagnosis.
- `references/compressed-lexical-forge-ablation.md` — token-conditioned neural read/write forges, shared-table compression, strict paired controls, neutral initialization, proxy-to-production reversals, and parallel R/W design.
- `references/hybrid-attention-threshold-and-throughput.md` — source-first control identification, archived-runtime throughput reproduction, W/R/V naming, maximum-to-minimum attention threshold search, and teardown-safe metric validation.
- `references/compiled-training-numerical-gate.md` — three-update finite-value gate, eager/compiled differential localization, tied-state compiler debugging, fail-fast paid-GPU discipline, and exact-branch deployment.
- `references/paid-gpu-data-launcher-resilience.md` — content-level data preflights, offline publication datasets, durable systemd launchers, resumable checkpoint cadence, retry interpretation, dynamic live logs, and exact throughput optimizations.
