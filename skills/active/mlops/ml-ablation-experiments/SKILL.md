---
name: ml-ablation-experiments
description: Design, implement, and verify ML ablation suites with clean controls, matched budgets, and reproducible launchers.
license: MIT
metadata:
  hermes:
    tags:
    - mlops
    - ablations
    - experiments
    - training
    - controls
    - reproducibility
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

# ML Ablation Experiments

## When to Use

Use this skill when creating or auditing model-training ablations, baseline comparisons, routing/control experiments, trainer launchers, or experiment config suites.

Typical triggers:
- User asks for ablation scripts/configs or training launchers.
- A result looks surprising and may indicate a config/control bug.
- Comparing routed vs dense, Zipf vs random/modulo/round-robin, shared vs no-shared, or similar architectural controls.
- Preparing runs that are expensive enough that a bad config would waste meaningful compute.

## Core Principle

Ablations are only useful if the control is actually controlled. Verify the invariants before interpreting losses.

## Workflow

1. **Inventory existing trainers/configs first**
   - Read existing runner CLI, profile defaults, model config builders, and neighboring scripts.
   - Trace config keys from YAML/CLI into the actual model object; do not assume a key is consumed.
   - When the underperforming component is itself the research target, externalize it behind its final fixed-state contract and iterate standalone before touching the production model. Preserve the user's canonical shared-mechanism framing and promote only a measured winner; follow `references/standalone-shared-attention-iteration.md`.

2. **Define the experimental axis and hold everything else fixed**
   - Routing controls: keep model size, shared branch, top-k, optimizer, dataset, tokenizer, schedule, and token budget fixed.
   - Capacity controls: explicitly state which capacity changes are intentional (e.g. shared-only is smaller because it isolates the shared branch).
   - Dense controls: match parameter count or active MLP width, and document which one you chose.

3. **Write invariant tests before long runs**
   - Strategy purity: random/modulo/round-robin controls must not leak baseline behavior through auxiliary routes, fallbacks, defaults, or schedules.
   - Matched token budget: assert `optimizer_steps × micro_batch_per_gpu × gradient_accumulation_steps × seq_len × world_size` matches the intended budget. Record optimizer steps and effective global batch separately; matched tokens alone do not preserve the optimization protocol.
   - Matched params: instantiate full models (or use `torch.device('meta')` when supported) and compare actual parameter counts; use analytic formulas only to propose candidate widths.
   - Learned-router validity: test deliberately unbalanced top-k dispatch, differentiable auxiliary-loss gradients, loss-free non-gradient bias updates from globally aggregated loads, and separate language/router/total-loss logging. Follow `references/learned-router-ablation-checklist.md`.
   - Shared object identity: when a large token/object table is intended to be tied across layers, assert module identity and deduplicated trainable parameter count.
   - Neutral initialization: verify model-wide initialization did not overwrite zero/identity initialization of a conditional residual.
   - Parser/config plumbing: test that YAML/CLI values reach the model config.
   - For dense-substrate conditional-object experiments, follow `references/tensorized-conditional-object-ablations.md`.

4. **Smoke locally before scale**
   - Run a tiny 1–2 step smoke to catch parser, device, DDP, and metric-schema issues.
   - Then run a full-shape optimizer-step smoke on the target device with the intended sequence length, vocabulary size, effective global batch, gradient accumulation, and production loss backend. A tiny smoke does not validate target VRAM.
   - On paid accelerators, ramp the micro-batch at final sequence length while sampling peak VRAM. For large vocabularies, separately exercise the exact output projection/cross-entropy: it can OOM after the backbone forward succeeds. Prefer an explicitly required fused linear cross-entropy backend when available rather than a silent memory-heavy fallback.
   - If the intended per-GPU batch OOMs, preserve `effective_global_batch = micro_batch × world_size × accumulation`, optimizer-step count, schedule, sequence length, and total tokens. Use DDP `no_sync()` before the final micro-batch and test the realized run manifest; do not silently trade optimizer updates for memory fit.
   - Measure ETA from stabilized real-data steps, not the first warm-up step or a synthetic-token smoke. Synthetic data validates mechanics; the real tokenizer/stream validates end-to-end throughput.
   - For Apple/MPS experiments, inspect the saved `run_config.json` and confirm `backend=mps`; do not infer hardware from a run name or compare against a similarly named NVIDIA artifact.
   - When replacing attention or another major component, verify the realized config after launch and add a behavioral invariant test (for causal mixers: future inputs must not alter prefix outputs). This prevents a hard-coded profile default from silently restoring the baseline component.
   - For autoregressive attention replacements, causality alone is insufficient: verify full-forward versus cached token-by-token logits, fixed cache shapes, stable cache pointers under `no_grad`, and real cached-decode speed. Call the design CUDA-Graph-friendly until capture/replay succeeds on CUDA.
   - For recurrent/state variants, test finite forward and gradients at the target sequence length. Short tests can miss long-sequence overflow caused by algebraically cancelling powers/divisions; prefer fixed chunkwise scans when a global closed form is numerically fragile.
   - If the intended micro-batch OOMs, first preserve the agreed effective batch, optimizer updates, sequence length, and token budget with tested gradient accumulation. Reduce the per-run budget or change the optimization protocol only with explicit approval, and then relabel the comparison rather than silently changing one variant.
   - Run a short diagnostic only for sanity, not final claims.
   - Order diagnostics by the user's actual failure criterion. If the complaint is held-out LM loss, run the matched language-loss discriminator before replaying retrieval/induction evidence that is already known; keep secondary probes quiet unless they change the decision.
   - For architectures intended for very large distributed runs, define a joint promotion contract before exploration: required full-budget loss delta, maximum throughput penalty, and parameter budget. Convert measured slowdown into extra calendar days and GPU-days at the intended scale. A small quality win that adds several percent wall-clock cost is not a deployment winner.
   - When augmenting an efficient GQA/FlashAttention baseline, prefer learned residuals projected into the existing Q/K dimensions before widening attention heads. Preserve contextual V unless lexical V is the explicit axis, verify exact baseline initialization, and test one of Q+K, post-injection renormalization, gate sparsity, or frequency conditioning at a time. See `references/throughput-preserving-lexical-gqa-ablations.md`. For Zipf conditioning, derive counts from the exact frozen training corpus/tokenizer (excluding holdout), apply weights only to the intended residual, and compare ordered weights against a deterministic permutation with the exact same RMS and histogram; see `references/throughput-constrained-lexical-attention.md`.
   - If a short run gives a surprising ordering, audit invariants before changing scientific claims.

5. **Separate diagnostic runs from headline runs and preserve the evidence chain**
   - Short local runs are for detecting broken configs and early dynamics.
   - Before scheduling a redundant headline retrain, search the original training host and durable artifact stores for a completed canonical checkpoint's `metrics.csv`, realized `run_config.json`, and checkpoint. Hash and mirror those artifacts immediately. A same-seed short rerun may still be useful as a matched pilot control, but label it separately from the completed headline run.
   - Do not run checkpoint portraits or other diagnostics concurrently with training on the same paid GPU: contention invalidates throughput. Queue diagnostics under a durable supervisor to start only after the ablation service releases the accelerator.
   - Do not use 200-step local losses as final evidence against a dense baseline unless that is the explicit benchmark.
   - For claims, use the planned token budget, eval cadence, and matched setup.
   - When the user asks for JSON/PNG evidence, interpret PNG as plots of measured checkpoint or ablation results unless they explicitly request a conceptual diagram. Never substitute a schematic for missing measurements.
   - Make raw artifacts primary: write CSV during training, consolidate completed measurements to JSON, and generate every paper figure deterministically from those files. Keep the plotting command/script beside the artifacts.
   - For a new architecture, add checkpoint-level evidence beyond toy tests: realized parameter/module audit, future-perturbation causality, full-vs-incremental equivalence, fixed-state size/address checks, distance-swept recall/induction/ICL, and hardware throughput/memory scaling.
   - If zero-shot recall is at chance, run a matched supervised synthetic learnability control before redesigning or scaling: controlled vocabulary, online examples, GQA positive control, and distances inside/outside the realized receptive field. A good LM loss proves language learning, not content-addressable retrieval. See `references/attention-free-context-retrieval.md`.
   - For context-memory repairs, use explicit escalation gates: matched tiny control, isolated memory primitive, structural TDD, then a bounded accelerator probe with a chance-level stop rule. Fixed persistence is not equivalent to content addressability; validate previous-key/current-value binding, query/key alignment, write selectivity, and rank/collision capacity before integration. See `references/context-memory-repair-gates.md`.
   - If additive fast weights learn high write/high decay while their output gate collapses, diagnose recurrence stability before adding fusion capacity. Implement and test a residual Delta update, keep recurrent state FP32 initially, derive an exact chunkwise triangular-solve scan, and sweep chunks with backward at target shape. See `references/stable-delta-context-attention.md`.
   - After stabilizing the recurrence, inspect what is actually read and written before adding capacity. Distinguish hidden-value writes from exact lexical-value writes; test collision normalization while preserving the full matrix. For lexical forges, retain contextual hidden values and the baseline contextual address path, forge only the lexical read/write components, and initialize as an exact Stable Delta no-op. If a tied token modulation table already exists, reuse it through a compressed low-rank projection rather than adding another vocabulary table. Keep token-specific R/W in a compatible shared coordinate system: prefer a common forged center plus a zero-gated antisymmetric direction over independent per-token read/write heads. Never label token hashes or learned routing projections semantic without dedicated evidence. See `references/lexical-delta-memory-design.md`.
   - When adding routed occurrence capacity to WVR, projection vectorization is insufficient if each slot still owns a separate recurrent scan. Prefer one rectangular state with common and orthogonal routed W/R address subspaces, contextual values, and one Stable-Delta scan. Preserve the parent exactly at initialization by exposing routed read coordinates while zero-gating routed writes into initially zero state rows. Measure paired throughput against a freshly rerun parent in the same compiler/runtime, not a historical tok/s number. See `references/single-scan-routed-wvr.md`.
   - When a structural deficit is confirmed, do not blindly finish redundant expensive variants. Let a nearly complete condition finish, stop before already-covered reruns, and reuse the accelerator for bounded architecture probes that must beat chance before 100M/1B-token training.
   - Preserve a reviewer-reproducible chain: checkpoint/config hash -> raw CSV/JSON -> plotting script -> PNG/table.
   - Before freezing or committing a paper table, enumerate active experiment services/jobs and wait for any near-complete run that can change the ranking. Read the last finite held-out evaluation from its raw CSV, archive the realized config and metrics, then remove all `pending` prose consistently across method, results, limitations, conclusion, and translations. Do not publish a paper snapshot that is predictably obsolete minutes later.
   - Keep repository evidence lightweight: commit metrics/configs/hashes and deterministic figures, not multi-hundred-megabyte checkpoints unless weights are explicitly part of the deliverable. After deleting large artifacts, update and verify every checksum manifest so it references only files that remain.

6. **Build launchers that summarize results and survive teardown failures**
   - Each launcher should write per-run logs and a final `summary.csv` with run name, status, final train loss, last eval loss, best eval loss, and throughput.
   - Define completion from the runner's real logging cadence. A run configured for 3,052 steps with metrics every 10 steps may validly end its CSV at 3,050. Require a `Metrics saved`/completion marker plus a final row within one logging interval of the target; do not rerun an expensive completed condition because teardown aborted after metrics were saved.
   - Make launchers resumable by condition: preserve completed run directories and support skipping already-complete variants. A logger/config bug in a later ablation must not force baseline retraining.
   - For live/paid comparison sweeps, run the dense baseline first (or immediately after any already-near-complete current run) so every subsequent variant has a live reference. If you accidentally started with a non-baseline, either stop early or let it finish if near completion, then kill/reorder before the next run starts.
   - For shared+routed lexical experiments, frame the winning variant as a residual lexical branch on a shared dense backbone unless no-shared controls prove routing alone wins. See `references/shared-routed-residual-framing.md`.
   - For paid GPU runs, copy or mirror the loss/metrics CSV as soon as each run completes; the user cares about losses first, checkpoints second.
   - Run long paid jobs under a durable remote supervisor (for example a transient `systemd` unit), not an interactive SSH shell. Verify the service, GPU allocation, and a finite stabilized metrics row before leaving it unattended; use a silent completion/failure watchdog rather than routine progress spam.
   - When the user asks for an operational command during a live run (follow logs, copy an artifact, inspect status), return the exact copy-ready command first and keep explanation to one sentence only if needed. Do not redirect them into a different experiment, repeat settled background, or invent a broader workflow while they are waiting on the requested operation.
   - If checkpoints are not part of the analysis, disable them up front (`--save-steps 0`, `--save-total-limit 0`, temp `--save-dir`) and clean any checkpoint directories before relaunching. Do not spend time discussing or preserving checkpoints when the goal is loss comparison. For a headline run that must support downstream evaluation or inference benchmarking, one final checkpoint is a justified explicit exception.
   - Do not let a post-success Python/CUDA teardown abort waste the rest of a sweep: after each run, if the process exits non-zero but `metrics.csv` exists and reaches the intended final step, record a warning and continue to the next ablation; if metrics are missing/incomplete, stop.
   - When switching paid hardware mid-sweep (e.g. H200 → 2×B200), first stop the old remote process and verify it is stopped, then launch the new sweep. If SSH becomes unavailable, report that uncertainty explicitly.
   - Before provisioning paid cloud compute, inspect the provider’s current pricing and provisioning path, but do not hard-code transient prices into the skill. Run a bounded smoke first when possible, derive ETA/cost from measured throughput, present GPU/region/rate/maximum estimated cost/shutdown policy, and obtain explicit financial approval before creating the instance or crossing the smoke boundary.
   - Use run names that encode scale/budget/variant (e.g. `h200-4b-100m_zipf_shared`).

## Pitfalls

- **Matched-step spike attribution:** Per-batch loss spikes are not evidence of recurrent-attention instability by themselves. Compare candidate and GQA at exact steps on the same data stream and measure post-spike recovery. Matching spikes imply hard batches; candidate-only spikes plus state/read/update norm growth imply recurrence trouble. See `references/stable-delta-context-attention.md`.
- **Architecture-target drift:** When the user asks to upgrade an existing attention mechanism to beat GQA loss, do not divert into checkpoint grafts, auxiliary curricula, reproducing an already-losing model, or retrieval probes that were already settled. Externalize that attention, change one mechanism at a time, run the matched LM-loss discriminator first, and return to target-width evidence after any proxy false positive.
- **Gate-name ambiguity:** A context output gate and lexical `object_gate`/`micro_gate` are different mechanisms. State which remain before launching or explaining a run; do not claim “gate-free” unless every named scalar gate in scope is removed or explicitly excluded.
- **Additive fast-weight suppression:** If write and decay approach one while the learned output gate approaches zero, the model may be suppressing a noisy unnormalized recurrence. Do not keep adding gates/fusion around it. Test bounded repeated writes and replacement, then use a residual Delta update with an exact vectorized scan. See `references/stable-delta-context-attention.md`.
- **Lexical-is-not-semantic overclaim:** Deterministic token hashes, token identity, n-gram fingerprints, learned hidden-state addresses, and zero-initialized token modulation tables do not by themselves establish semantic retrieval. Name the measured mechanism precisely (lexical transition, contextual address, hidden-value write, lexical-value write, collision behavior, induction) and require a dedicated learned-similarity evaluation before using “semantic.” A learned projection is not automatically a semantic representation. When scalar Stable Delta remains behind GQA, preserve the full matrix and inspect read/write interference before partitioning capacity: value-column multi-timescale decay can win a 3,052-step miniature proxy yet lose at 98M/100M tokens. Treat target-scale reversal as authoritative and see `references/stable-delta-context-attention.md`.
- **Primitive-forward speed trap:** A recurrent attention primitive can look fast in forward-only microbenchmarks yet train 10× slower because backward traverses a Python token loop. Benchmark forward+backward, derive an exact chunkwise scan, assert equivalence, sweep chunk sizes at target shape, and finally smoke the compiled full model.
- **Small-model promotion trap:** A miniature model can beat GQA throughout a fully matched 3,052-step language proxy and still lose after target-scale 98M/100M-token training. Once this happens, the proxy is no longer a valid promotion gate for that architecture class. Preserve it as a learnability diagnostic, move decisions to bounded target-width evidence, and inspect scale-specific constraints such as receptive field versus sequence length. See `references/standalone-shared-attention-iteration.md`.
- **Compiled tensor-to-Python branch:** Calling `float(tensor)`, `.item()`, or branching in Python on a trainable tensor inside `forward` can break `torch.compile` and silently erase a throughput advantage. Use a static Python flag for configuration-fixed paths and remeasure stabilized target-shape throughput.
- **Progress-bar loss ambiguity:** A terminal progress line often displays the current training-batch loss while the paper criterion is held-out evaluation loss. When a run completes, read finite `eval_loss` rows from the raw metrics CSV and label both values explicitly; never present the final progress-bar loss as validation loss.
- **Optional-component logging crash:** A valid ablation may intentionally disable a gate/module and expose `None` telemetry. Smoke every structural variant through startup and its first metrics write; format absent controls as `disabled` rather than applying numeric format specifiers. Treat logging as part of the paid-run execution path.
- **Hidden-state equivalence is not token equivalence:** On real BF16 checkpoints, full-forward and incremental hidden states can differ materially from accumulation order even when cache addresses are stable. Report hidden error, logits error, and greedy-token agreement separately; rerun FP32 to distinguish numerical ordering from a state-update bug before claiming exact decode equivalence.
- **Synthetic recall floor:** Zero accuracy and chance-level rank on arbitrary key/value or induction probes—even inside the nominal receptive field—is a valid negative result, not proof that only long-range memory failed. Verify the task is learnable for a matched attention control and avoid presenting a distance curve as an architecture-specific long-context failure without that control. If the matched GQA control learns but convolution does not, distinguish temporal reach from content addressability: larger dilations or a diagonal vector state may extend reach without enabling key-conditioned retrieval. Follow the correction ladder in `references/attention-free-context-retrieval.md` before scaling.
- **Language loss is not retrieval evidence:** A QKV-free model can beat the uniform LM-loss floor substantially while remaining at chance on supervised associative recall. Report these as separate capabilities; never summarize the latter as “the model has no context” or generalize one mixer failure to every attention-free architecture.
- **Auxiliary-route leakage:** In top-k routed systems, it is easy for the primary route to use the requested strategy while secondary routes still use the baseline. Test top-k routes explicitly.
- **World-size budget mistakes:** A step count calibrated for 8 GPUs gives one-eighth the tokens on 1 GPU. Recompute tokens for the actual world size.
- **Parameter-count mismatch:** Removing a shared branch often shrinks the model unless routed width is increased. Verify counts before launching.
- **Overinterpreting early steps:** Dense baselines can look strong in very short runs; routed specialization may need longer. Use short runs to catch bugs, not to make final claims.
- **Schedule confounds:** If the ablation is about routing table quality, avoid simultaneous top-k/gate schedule changes unless schedule is the axis under test.
- **Hardware-fit assumptions:** Do not assume a large accelerator can hold a large batch because the model has few parameters; long-sequence activation memory can dominate. Smoke the exact target batch/sequence and adjust batch/steps/budget explicitly.
- **Iteration budget vs headline budget:** For exploratory ablations, a smaller but still meaningful budget (e.g. 1B tokens/run) can be preferable to a 4B+ budget when the goal is to rank controls before scaling.
- **Matched tokens do not match optimizer updates:** Changing sequence length or effective batch while holding total tokens fixed changes the number of parameter updates. Same-length variant comparisons remain controlled, but cross-sequence conclusions may be confounded. Report both token count and update count; add an update-matched control before interpreting sequence-length effects.
- **Tiny-corpus repetition trap:** Before a headline token-budget run, compare unique available training tokens with the requested budget. Repeating a small local smoke corpus hundreds of times is a memorization diagnostic, not billion-token pretraining. Require a manifest with exact unique train tokens and a document-disjoint held-out split.
- **Streaming holdout density trap:** A mathematically disjoint but extremely sparse held-out predicate can make every evaluation scan thousands of remote documents. Test both disjointness and operational density; reserve enough documents for efficient eval without exhausting the training budget.
- **`set -e` sweep abort after successful run:** PyTorch/CUDA can occasionally abort during process teardown after writing checkpoint/metrics. In paid sweeps, a plain `set -euo pipefail` loop can stop after the first completed run. Wrap each run, inspect `${PIPESTATUS[0]}`, and continue only if the metrics CSV exists and final step is present.
- **Loss CSV priority:** For paid remote ablations, immediately secure `metrics.csv`/loss summaries locally or in durable storage. Do not reassure the user with checkpoint presence when they asked for losses.
- **Checkpoint waste:** For comparison ablations, checkpoints can waste disk/time and distract from the requested artifact. Default paid exploratory launchers to no checkpointing unless the user asks for resumability or model artifacts.
- **Baseline-last live blindness:** If dense runs last, the user cannot judge whether paid variants are winning while the sweep is running. Put dense first for live comparison unless there is a deliberate reason not to.
- **Routing-replaces-dense overclaim:** If the winning architecture is shared-plus-routed, the claim is a routed lexical residual over a shared dense backbone, not replacement of dense MLP compute. Use no-shared and shared-only controls to support the wording.
- **Matched-token vs wall-clock conflation:** Matched tokens answers quality/sample-efficiency at equal data budget; matched wall-clock answers training-time compute efficiency and will favor the faster implementation. If routed variants are slower, report throughput separately and state “matched-token quality evidence, not a wall-clock efficiency claim.” Treat inference/serving throughput as a separate deployment metric, and only claim inference wins with a same-setup baseline.
- **Tokenizer artifact mismatch:** Do not assume the tokenizer bundled with an inference export reproduces the training vocabulary. Load it through the training tokenizer wrapper and assert its realized vocabulary size/special IDs against the model config before paid runs; inference exports may omit added or reserved entries while the model still allocates them.
- **Benchmark flag mismatch:** For official benchmark CLIs, verify dataset-specific length flags from the installed version. A generic input/output-length option may be ignored by a random-dataset generator, silently benchmarking default long prompts. Confirm realized prompt/output token counts in logs/JSON before publishing throughput.
- **Supplementary-code drift:** A paper supplement can match architecture and parameter count but still fail to reproduce the headline run if a data-dependent path silently falls back (e.g. Zipf routing with missing token frequencies becomes modulo). Audit the runnable script path, dataset modes, tokenizer defaults, and fail-loud behavior, not just model classes.
- **Wrong-code-path trap:** If the user says the headline result did not come from the paper's legacy supplementary code, stop patching that legacy path as if it were authoritative. Snapshot or mirror the actual training harness/commit used for the result, include the real configs/scripts/tokenizer stub/tests, and label old code as legacy/reference to avoid reviewer confusion.

## Verification Checklist

Before launching expensive ablations:

- [ ] Existing runner/profile/config path inspected.
- [ ] Experimental variants listed with the single intended difference for each.
- [ ] YAML/CLI parsing tested.
- [ ] Routing/control invariants tested.
- [ ] Param counts checked and documented.
- [ ] Token budget computed for actual world size.
- [ ] Local smoke passed.
- [ ] If the user needs live comparison during a paid sweep, dense/baseline is scheduled first or explicitly justified.
- [ ] Launcher writes logs and summary CSV.
- [ ] Paid/remote sweep launcher tolerates post-success teardown aborts only when final metrics are complete.
- [ ] Exploratory paid sweeps disable checkpointing unless checkpoints are explicitly needed.
- [ ] Metrics/loss CSVs are copied or mirrored promptly; checkpoint existence is not a substitute for saved losses.
- [ ] Shared+routed wins are framed as residual lexical specialization over a shared dense backbone unless no-shared controls prove a stronger claim.
- [ ] When moving to new paid hardware, old paid processes are stopped or their uncertain state is reported clearly.
- [ ] Claims clearly separate smoke diagnostics from final evidence.

## References

- `references/learned-router-ablation-checklist.md` — matched fixed-vs-learned residual routing, variable-load top-k dispatch, differentiable auxiliary balancing, loss-free DDP bias updates, gradient-accumulation contracts, and full-shape large-vocabulary smoke gates.
- `references/throughput-preserving-lexical-gqa-ablations.md` — quality/throughput promotion contracts and an evidence-driven ladder for learned lexical residuals over GQA without widening FlashAttention heads.
- `references/throughput-constrained-lexical-attention.md` — paired loss/throughput promotion gates, compression of slow lexical winners, and corpus-derived ordered-vs-permuted Zipf controls.
- `references/stable-delta-context-attention.md` — diagnose additive fast-weight instability, replace it with residual Delta writes, derive an exact triangular-solve scan, and benchmark backward/chunk sizes before target-scale promotion.
- `references/lexical-delta-memory-design.md` — iterate stable fixed-state lexical memories: distinguish hidden versus exact-token writes, normalize collision load without partitioning capacity, and design token-only read/write/value forges without semantic overclaims.
- `references/single-scan-routed-wvr.md` — add routed W/R occurrence capacity with one rectangular Stable-Delta state and one scan; includes parent-preserving initialization, TDD contracts, and paired H100 throughput gates.
- `references/standalone-shared-attention-iteration.md` — externalize an underperforming attention/context mechanism, iterate one minimal shared change at a time with TDD and matched standalone controls, then integrate only the winner.

- `references/new-architecture-reviewer-evidence.md` — matched-control matrix and checkpoint/functional/deployment artifact package for a new autoregressive architecture, including raw JSON-to-PNG provenance.
- `references/attention-free-context-retrieval.md` — interpret LM-vs-retrieval evidence, run matched supervised probes, and iterate fixed-state context mechanisms before expensive retraining.
- `references/context-memory-repair-gates.md` — stage context-memory redesigns through primitive retrieval, structural TDD, collision/rank checks, and bounded paid-GPU stop gates.
- `references/token-routing-ablation-controls.md` — concrete lesson from token-routed Zipf/random/modulo ablations, including top-k auxiliary-route leakage and H200 token-budget arithmetic.
- `references/supplementary-code-reproducibility.md` — checks for paper supplementary code that must reproduce a headline training result, including silent Zipf→modulo fallback and tokenizer-path drift.
- `references/paid-gpu-sweep-resilience.md` — robust paid-GPU sweep launcher pattern: tolerate post-success teardown aborts only when metrics are complete, and mirror loss CSVs promptly.
- `references/shared-routed-residual-framing.md` — how to order live baseline-first sweeps and phrase shared-plus-routed wins as residual lexical specialization rather than dense replacement.
- `references/apple-mps-lexical-object-ablations.md` — Apple/MPS workflow for tied o200k lexical objects, dispatch-free micro-experts, attention-free causal mixers, parameter matching, and interpretation safeguards.
- `references/paid-single-gpu-architecture-runs.md` — paid H100/H200/B200 workflow: immediate already-billing bootstrap, main-only Git deployment when requested, remote-command verification, target-device smoke ladder, exact-vocabulary loss OOMs, disjoint streaming splits, durable services, watchdogs, and claim locks.
- `references/paid-gpu-attention-free-llm-smoke.md` — progressive paid-NVIDIA smoke, large-vocabulary memory bottlenecks, disjoint streaming data, durable execution, and measured cost gating.
