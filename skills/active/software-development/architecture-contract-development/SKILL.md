---
name: architecture-contract-development
description: Preserve user-stated architecture boundaries during implementation; encode corrections as public API tests instead of generic abstractions.
license: MIT
metadata:
  hermes:
    tags:
    - software-development
    - architecture
    - api-design
    - testing
    - user-scope
    related_skills:
    - test-driven-development
    - systematic-debugging
    - plan
  hermes_frontmatter:
    version: 1.4.4
    author: Hermes Agent
    platforms:
    - linux
    - macos
    - windows
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

# Architecture Contract Development

Use this skill when implementing features where the user has strong architectural constraints, domain framing, or trust concerns. It is especially relevant when the user corrects a design as too generic, too broad, wrongly scoped, or not aligned with the project's core claim.

## Core Rule

A user-stated architecture boundary is a contract. Do not keep a convenient generic abstraction if the user explicitly narrows the system.

Examples:
- "I don't want this usable by other models" means the public API must reject or hide generic model callables.
- "Keep it Zipf/TR" means names, exports, tests, prompts, schemas, and metadata should encode Zipf Token-Routed semantics.
- "Delete the any-to-any" means remove the files/exports/tests for that direction and verify they are gone before continuing.
- "Do not touch this repo unless I open it" means switch/open the exact workspace first and avoid edits elsewhere.

## Workflow

1. Restate the corrected contract in concrete API terms before editing.
2. Inspect the existing implementation path before proposing new architecture:
   - trace where the component is constructed, where it is called, and how outputs combine
   - read config/profile/parser wiring before adding flags or scripts
   - if the user says a mechanism is already “free” or naturally coupled, verify the current dataflow instead of inventing a constrained variant
   - disambiguate three independent boundaries before editing: source-file separation, runtime module sharing, and runtime state ownership; a separate file does not imply a second model or a new model-level cache
   - treat user analogies and sketches as explanatory examples unless they explicitly promote them to canonical terminology or representation
3. For a new stateful/context mechanism, validate it outside the main architecture first:
   - write/read a known association deterministically before end-to-end training
   - audit address collisions or representation conditioning, not only tensor shapes
   - inspect gradients/gates and compare capacity settings under the same protocol
   - require a positive control and chance baseline
   - only reinsert the mechanism into the single intended model after the isolated primitive succeeds
4. Before launching a paid or long matched run, lock its experiment identity in one sentence: exact architecture, scientific role, parameter/token budget, existing controls, and explicitly excluded obsolete runs. “Run the corrected architecture iso-parameter” means train the replacement candidate; it does not authorize an unsolicited rerun of the broken predecessor.
5. Write or update tests first so the wrong abstraction fails:
   - reject generic callables/policies when the system is project-specific
   - assert public exports expose only the intended API
   - assert required metadata/framing is present in traces/schemas
   - assert deleted features are no longer importable or present when appropriate
   - assert experiment configs encode the intended architectural controls before launching long runs
6. Run the targeted test and verify it fails for the expected reason.
7. Patch production code minimally to satisfy the corrected contract.
8. Re-run targeted tests, then relevant import/syntax checks.
9. Summarize exactly which files changed and which pre-existing user changes were not touched.

## Public API Discipline

When the user rejects genericity, remove it from the public surface, not just the docs:

- Rename generic names to domain-specific names.
- Stop exporting deprecated/generic symbols.
- Validate constructor arguments against the project-specific interface.
- Put the domain contract in docstrings and trace metadata.
- Keep low-level helper code internal unless the user asks for reusable infrastructure.

## Atomic Visual Compiler Contracts

When the user asks for an atomic block-based research IDE, “atomic” applies to operations, links/ports, settings, code lowerings, metrics, and standalone results—not merely to how cards look.

- Keep a typed IR/registry as the only source of truth; Blocks and code are projections of that IR.
- Keep the application shell small. Split studio orchestration, graph canvas/cards, pointer/cable interaction, and pure IR mutation/lowering into separate modules; do not accumulate editor logic in `App.tsx` or the Electron shell.
- Never hardcode demo metrics, shapes, block lists, inspector values, or alternate generated-code branches in the renderer. Derive them from active editable graph state.
- Do not let the first demo preset or an old research candidate become a privileged compiler architecture. Keep the compiler registry-driven and the default graph neutral. If the user rejects a mechanism as repeatedly non-probant, remove its branches, exports, tests, presets, and product terminology; “promising” is not “beat the named baseline.” Retain research-specific composites only when explicitly approved by the user and supported by the evidence standard they set.
- When a dense paper-derived preset obscures the core mechanism, add a focused pedagogical preset instead of replacing or mutating the canonical full-model preset. Keep both behind an explicit preset selector; label the focused graph as a module or representative slice, use separate token-ID and contextual-hidden inputs when the architecture requires them, group palette atoms by scientific role, and retain stable atom IDs/lowerings. Prove the focused preset with a topology contract test, generated-code signature test, real framework-runtime shape smoke, and visual collision check before presenting it as executable.
- A static canvas is not an editor. Prove select, move, edit, add, duplicate/remove, subgraph encapsulation, and immediate code regeneration before visual polish.
- When links are requested, implement node-editor cables rather than decorative SVG lines: visible typed plugs, elastic Bézier preview, unplug/replug from one end, drop-to-disconnect, output multi-plug, single-input replacement, and cables that leave ports before curving so they do not cut through cards. Keep connection mutation as tested pure IR code and pointer/geometry behavior in a dedicated hook.
- Preserve semantic ports through the entire stack. A registry entry with typed multi-input/multi-output ports is not complete if conversion to canvas nodes collapses them to one generic `hidden` port or if the compiler ignores the added node.
- Keep **port identity** separate from **tensor type**. `routed` and `shared` may be distinct target sockets with the same `hidden` tensor type; replacement/cardinality is keyed by port ID, while compatibility and cable styling are keyed by tensor type. Persist both through IR edges, pointer drafts, DOM metadata, parser markers, and compiler input lookup. Never cast a semantic port ID such as `expertIndices` into its tensor type `expert-indices`.
- Expose semantic research blocks, not kernel plumbing. For MoE-style models, public blocks may include Router, Top-K Routing, Routed Expert Bank, Shared Expert Bank, Expert Merge, Load-Balancing Loss, and an expandable composite; keep dispatch/gather/scatter/all-to-all internal to lowering/runtime unless explicitly requested.
- Keep training semantics separate from forward-graph semantics: optimizers and schedulers belong in a Training IR/Studio, not as tensor-processing cards in the model graph. Verify runtime signatures before generating optimizer settings, especially version-sensitive operators such as Muon or Adafactor.
- Token embedding maps IDs to hidden vectors; it may feed a learned router but is not itself token routing. Represent learned routing, lexical/ID routing, Top-K selection, experts, and merge as distinct semantic contracts.
- Group large registries by semantic family (for example Transformer Core, Routing & Experts, Activations) with counts/search or disclosure controls; do not solve completeness by dumping a long flat palette that hides the primary workflow.
- Typed links may remain hidden in the UI when the user rejects drawn connections; hiding links does not permit deleting or simplifying their IR semantics.
- Use expandable composites for full models (model → layer → attention/MLP → atoms) rather than flattening every primitive onto one canvas.
- When deriving a preset from a paper, inspect the exact user-named manuscript **and** runnable supplement before wiring blocks. Separate the ordinary backbone from the novel path (for example, standard GQA attention versus lexical routing confined to the MLP), reject incorrect substitutes in tests, and make declared contracts such as tied weights operational rather than cosmetic. A one-layer canvas must be labeled representative when the published model repeats it; verify the topology with a shape-preserving miniature under the real framework, then restart the desktop dev process before visual inspection because HMR may preserve stale initial graph state. See `references/paper-derived-neural-presets.md`.
- A populated code textarea or hardcoded model template is not code synchronization. Every publicly executable block needs a concrete declaration, a forward invocation driven by incoming edges, materialized settings, and a real framework-runtime smoke test. Undefined helper names and pseudocode strings are placeholders and must be disabled or labeled incomplete.
- Emit stable managed markers for semantic edges and round-trip them: deleting a marker removes the cable, changing endpoints rewires it after validation, and X/Y-only movement leaves generated code byte-identical. Generate forward order from graph topology, never renderer order.
- Keep block deletion and cable deletion distinct. Deleting a block removes its declaration and invocation; deleting one elastic removes only that edge/dataflow. Keep endpoint declarations present, omit only invocations whose required inputs are unavailable, continue independent executable branches, and never erase the whole program with an invalid stub or silently invent an external input.
- Read valid graphs as stable dependency levels, not a flat node array: execute/color independent blocks in one parallel wave and tie-break by canonical node order so reattaching the same elastic cannot reorder code. For invalid open-port graphs, preserve authored order to report the first missing-input atom instead of promoting it to an artificial indegree-zero root.
- Never show a global green “synchronized” state when only a subset of blocks has executable lowerings. Derive capability status from the active graph and surface unsupported mappings explicitly.
- In an elastic node editor, cards, ports, and cables must share one world transform. Recompute cable endpoints after selection/layout changes and `ResizeObserver` events, keep boundary ports unclipped, make semantic composites draggable, and support X/Y pan, pointer-centered zoom, and fit-to-graph.
- When the user reports that implementation is absent in source, inspect definitions, compiler/parser paths, and runtime tests before taking more screenshots. Do not use visual evidence as a substitute for code-level verification.
- Treat tokenizer construction as its own atomic tool with shared Python/Rust lowerings; materialize selected token objects rather than rendering an entire vocabulary. Keep its permanent atom library independent of the current pipeline so deleting every step does not make rebuilding impossible.
- Define an “atomic result” as a matched standalone implementation benchmark for one semantic contract, not as training loss or an activation trace. Refuse universal rankings across different contracts.

See `references/atomic-neural-research-ide.md` for the complete IR, hierarchy, tokenizer, interaction, benchmarking, and Electron execution contract. See `references/atomic-graph-code-roundtrip.md` for executable block/cable round-trip contracts, runtime verification, and elastic viewport geometry. See `references/registry-driven-neural-compiler.md` for structured lowerings, neutral evidence-gated presets, port-ID/type separation, topological generation, reverse parsing, and runtime verification slices.

## Pitfalls

- Do not defend the previous abstraction. Convert the correction into tests and code.
- Do not claim the system is aligned just because docs say so; assert it in tests.
- Do not broaden scope while the user is correcting trust/scope issues.
- Before scaffolding an ambiguous `client`, classify the deliverable explicitly: library SDK, CLI, VS Code extension, or standalone Electron app. These are different products. If the user mentions more than one, ask them to select before writing production code; once selected, delete the abandoned scaffold rather than leaving mixed public surfaces.
- For proprietary desktop clients, distinguish product licensing from dependency notices: the application may remain `UNLICENSED`/closed while Electron and bundled third-party code retain mandatory notices. Simplifying or closing a derivative never removes upstream license obligations; avoid a fork when the user wants an original proprietary implementation.
- When a user requests a visual reference such as a cyberpunk game, extract general principles (HUD density, angular geometry, technical typography, restrained neon accents) rather than copying logos, assets, or exact branded screens. Preserve functional content, run a visual slop audit, inspect the rendered primary viewport, and repair clipping/overlap before rebuilding the distributable artifact.
- Do not invent a new architectural variant before reading the current wiring. For ablations, first distinguish “component absent”, “component global/free”, “matched-parameter replacement”, and “same-size non-routed control”.
- Do not let internal run nicknames redefine the product. When a corrected component is reinserted into the intended single model, describe the expensive run as the corrected full architecture and its matched budget—not as a separate “contextual model/run.” Never queue an obsolete predecessor as an extra control unless the user explicitly requests that training expenditure.
- During rapid architecture iteration, lead with the one active candidate, the failed/passed gate, and the immediate action. Do not introduce a taxonomy of “old/full/contextual” models unless the user asks for it; this can make a single replacement path sound like multiple products. If the user says the explanation is overcomplicated, stop, collapse back to the intended candidate, cancel any accidental queued controls, and verify service state.
- Do not turn an implementation analogy into the architecture name. Terms such as “table 2D”, “grid”, or “cache” may describe one possible internal representation without defining the public contract. Use a capability-level name until the representation is explicitly fixed.
- “Develop it separately, then share it with the model” usually means one standalone component in a dedicated file, tested in isolation, then composed into the same model. It does not authorize a second model, a new top-level cache, or a changed state API. Ask specifically whether sharing applies to parameters, outputs, or runtime state if that remains ambiguous.
- For fixed-state associative context, collision diagnostics are mandatory. A primitive can work with random addresses yet fail end-to-end because deterministic token addresses are nearly collinear. Measure Gram-matrix max/p99 similarity and retrieval capacity before blaming rank or training.
- After proving behavior, profile sequence-length throughput before scaling. A correct token-by-token Python recurrence can be scientifically valid yet unusable; preserve full/incremental equivalence while moving to a causal chunk scan, then rerun the synthetic positive controls because vectorization may change the update rule.
- A context branch that succeeds synthetically can still damage LM loss when injected at full random strength. Treat its residual gate as a parent-preservation mechanism: test neutral zero-init under the deployment training schedule, record gate telemetry, and require matched LM checkpoints before scaling; see `references/standalone-shared-context-mechanism.md`.
- Parameter sharing does not imply compute sharing or runtime-state sharing. Count how many layers invoke the shared component; a single parameter instance called ten times still pays ten forward/backward costs. Inspect cache allocation separately: two layers may reference one module yet own two independent recurrent matrices. Architecture prose, state counts, and tests must distinguish shared parameters from per-invocation state. Search the quality/throughput frontier by varying invocation points while keeping one parameter instance, and require both the behavioral positive control and the user-stated throughput threshold before restarting a paid pilot.
- For routed recurrent memory, computing all route/address/value projections in parallel is not enough if every slot still performs an independent causal scan. Treat scan count as an architecture-level performance contract. Prefer a single rectangular recurrent state whose W/R address rows combine common and orthogonal routed subspaces while contextual V columns remain fixed; assert one state matrix per active invocation and one scan in the implementation.
- Distinguish an execution kernel from the architecture it usually serves. “Use FlashAttention with WVR” can mean an IO-aware/fused W/R/V kernel while preserving WVR equations; it does **not** authorize silently replacing W/R/V with GQA Q/K/V. Conversely, calling stock FlashAttention with read/write/value tensors computes softmax attention and must be described honestly as attention. Keep public names and explanations in the user's W/R/V vocabulary; mention `q=`/`k=` only as unavoidable third-party API argument names, never as the architecture definition.
- When an attention-free model is close in throughput but behind in quality, do not assume another kernel optimization will close the quality gap, and do not place generic Flash/GQA at the center with the original mechanism demoted to a residual. Pre-register a minimum-attention threshold study instead: preserve the canonical conv/WVR/lexical substrate and its stateful invocation points, replace a fixed small number of ordinary layers with the project's own lexical W/R/V attention, and test 0→1→2 layers against the full-attention control. Short proxies may reject instability or unacceptable throughput but may not choose the winner when prior evidence says proxy rankings fail at full budget. See `references/wrv-flash-and-minimal-attention.md`.
- If a paid pilot violates an explicit efficiency ceiling, stop it immediately, preserve its partial metrics as negative evidence, and iterate with short realistic hardware benchmarks. Do not defend the run because the implementation improved relative to an earlier prototype; compare against the actual control the user named. Translate throughput loss into calendar days and GPU-days at the intended scale before accepting a quality gain.
- For remote GPU experiments, Git is the source of truth for code, configs, tests, and manifests: push an audited targeted commit and checkout that exact commit remotely. Do not repeatedly rsync a working tree. Use direct pinned dataset downloads plus checksum verification, and reserve rsync/scp for small runtime wrappers and result artifacts. Distinguish local monitor failure, SSH failure, supervisor state, and training state.
- After a one-seed full-budget win, preserve it as a positive control. If it is too slow or over-parameterized, simplify its learned path while retaining the fused baseline tensor shapes, then run a paired next-seed replication before claiming success. See `references/paid-gpu-architecture-experiment-operations.md`.
- When using compilation to cross a performance gate, exclude compile warm-up from steady-state throughput and record compile mode. For publication-grade efficiency claims, rerun the relevant control under the same compilation policy; beating a historical uncompiled control is an engineering gate, not yet a fully matched scientific claim.
- If the learning-rate scheduler depends on the configured total step count, never compare step 250 from a 250-step pilot against step 250 from a 500- or 3052-step run as though the optimization trajectory were matched. Compare models under the same total horizon, warm-up, decay schedule, evaluation cadence, and seed; otherwise label the observation exploratory.
- For paper-grade architecture comparisons, separate three claims: fixed-budget quality, steady-state compiled throughput, and architecture-specific hyperparameter tuning. Existing runs remain valid measurements when one axis differs, but they are not automatically a matched proof. Add explicit LR/compile columns, give the principal control the same short tuning budget, and avoid calling prior runs “invalid” when the correct action is to narrow the claim.
- For paper/figure architecture corrections, treat the figure as part of the architecture contract: remove obsolete concepts from both manuscript text and visual assets, search source + generated-facing files for stale terms, and visually inspect the regenerated image before reporting success.
- Treat image correctness and manuscript flow as separate verification targets. After changing a figure, compile twice and read the extracted text for the page before, the figure page, and the page after. Never let a float split an introductory sentence from its enumeration, proof, or explanation.
- For standalone stateful sequence-layer foundations, turn numerical equivalence, incremental/full equivalence, caller-owned stable state storage, slot routing, absolute positions, exact checkpoint names, rejected QKV surfaces, and the no-integration scope boundary into separate observable tests. Keep scheduler policy out of the layer; see `references/fixed-state-stateful-layer-foundations.md`.
- For top-level vLLM integration of an attention-free fixed-state model, mirror Mamba-family state, PP, logits, and CUDA-graph interfaces while preserving canonical checkpoint-facing names. Token-conditioned routing IDs must cross PP boundaries explicitly, and exact loading must cover persistent buffers as well as parameters; see `references/vllm-attention-free-stateful-model-integration.md`.
- When feedback says the paper text is displaced or disorganized, stop iterating on pixels until you determine whether the issue is the image, LaTeX float placement, or manuscript prose. Do not redesign the wrong layer.
- If a simplified diagram replaces a detailed one, update surrounding prose and captions to say `simplified schematic` or `overview`; do not continue calling it the complete architecture.
- If the user identifies a diagram as coming from an external app/exported PNG, do not silently introduce a new LaTeX/TikZ source as the canonical diagram. Either edit/regenerate the requested asset in its existing format or explicitly ask before changing the source-of-truth workflow.
- When adapting a diagram from one project to another, treat its topology and its domain semantics as separate contracts. Inspect any authoritative target page/specification before choosing the new use case; a folder name is not domain evidence. Preserve only explicitly requested terms, translate every domain-specific node, scan all target artifacts for stale source terminology, and use the requested canonical format (for example `.mmd` when the user asks for Mermaid rather than substituting HTML). If the user says “just make the Mermaid” or “bref,” stop expanding the design, produce/render the canonical artifact immediately, and keep progress narration minimal. If the user asks for a grouping bot without extrapolation, limit it to the named operations and keep any future MCP interface visibly optional. See `references/diagram-domain-adaptation.md`.
- For composable executable diagrams, separate peer definitions from runtime parentage. An autonomous Diagram Bot may be a sibling `DiagramDefinition` in the registry while its active `DiagramRun` parents independent child runs that reference utility definitions. Do not reinterpret it as a registry UI, persistent workspace, globally superior diagram type, or MCP wrapper. Distinguish a deterministic configured orchestrator from a parent agent: when the user asks for a “mini-Hermes,” show objective, parent context/state, sibling selection, parallel child runs, observation, parent decision, result, and persistent next-objective loop. Also disambiguate “utility diagram”: requests for more diagrams “like DATA LAB and CALL-DATA” mean complete sibling domain workflows, not retry/audit/approval primitives. Make persistent-vs-one-shot autonomy and parallel/join policy explicit rather than inventing them. See `references/composable-autonomous-diagram-orchestration.md`.
- When regenerating architecture diagrams programmatically, prefer simple non-overlapping layouts with generous spacing and validate the actual rendered image; a syntactically generated PNG is not acceptable if arrows/text overlap or the visual story is unreadable.
- Do not treat a short local smoke result as architectural evidence; use it to catch broken settings, then align long-run configs with the known-good regime before drawing conclusions.
- Keep verification layers distinct in dirty or hardware-sensitive repositories: targeted tests can validate the changed surface while the full suite remains non-green. Never disturb unrelated user edits to manufacture a baseline, never call the repository clean when a platform-specific test still fails, and never attribute a failure to the change without a safe baseline comparison. See `references/repository-verification-evidence.md`.
- Do not commit or push unless the user explicitly asks.
- Before calling a renamed or reinterpreted operator a new architecture, run an algebraic and matched-weight functional-equivalence audit. A zero/disabled residual, unused parameter, or different initialization order does not create novelty. Require a test that the proposed active mechanism changes outputs under identical shared weights, and trace its enabled flag into the realized full-model config before paper submission or paid scale-up. For lexical attention, distinguish indirect lexical information in hidden states from a direct token/object path into R/W/Q/K/V; see `references/hybrid-lexical-contextual-attention.md`.

## References

- `references/complexity-zipf-tr-tool-controller.md` — concrete pattern for keeping a tool controller Complexity/Zipf/TR-specific instead of generic model-agnostic.
- `references/complexity-ablation-configs.md` — pattern for designing Complexity ML ablation configs without inventing unnecessary architectural variants, including shared-expert controls and local smoke-run cautions.
- `references/complexity-external-generation-boundary.md` — pattern for enforcing the Complexity boundary where PyTorch owns training/export while generation/serving is delegated to vLLM or SGLang, not native `model.generate()`.
- `references/complexity-paper-figure-contract.md` — pattern for correcting Complexity paper architecture diagrams/manuscript text: remove obsolete concepts everywhere, preserve external PNG workflows unless changed explicitly, and visually validate regenerated figures.
- `references/diagram-domain-adaptation.md` — procedure for reusing a diagram’s topology across projects without leaking source-domain semantics, including Mermaid canonicalization, stale-term scans, grouped views, and optional future MCP boundaries.
- `references/composable-autonomous-diagram-orchestration.md` — contract for autonomous orchestrator diagrams: peer definitions, contextual parent runs, persistent-vs-one-shot lifecycle, independent parallel child runs, and separation from UI/MCP adapters.
- `references/paper-figure-layout-and-flow.md` — LaTeX workflow for giving a large figure dedicated space without breaking the surrounding narrative, including page-by-page verification.
- `references/proprietary-electron-client-contract.md` — contract and verification workflow for closed Electron AI clients, including licensing boundaries, secure process separation, SSE testing, DMG packaging, and reference-driven visual redesign.
- `references/fixed-state-stateful-layer-foundations.md` — contract tests and ring-buffer design for standalone stateful sequence layers with full/decode equivalence, stable caller-owned state, request slots, absolute positions, checkpoint-compatible names, and strict integration boundaries.
- `references/vllm-attention-free-stateful-model-integration.md` — top-level vLLM integration checklist for fixed-state attention-free models: Mamba interfaces, PP token routing transport, canonical module names, exact parameter/buffer loading, and focused contract verification.
- `references/standalone-shared-context-mechanism.md` — workflow for isolating, collision-testing, vectorizing, reinserting, and measuring a shared fixed-state context mechanism without creating a second model or an unsolicited model-level cache.
- `references/wrv-flash-and-minimal-attention.md` — separates W/R/V semantics, Flash-style execution, and stock softmax attention; includes matched throughput diagnosis and a pre-registered 0→1→2 minimal-attention threshold protocol.
- `references/hybrid-lexical-contextual-attention.md` — novelty gate and minimal R/W lexical-address design for a genuinely lexical-contextual SDPA/FlashAttention model, including grouped-head, gate-init, cache, gradient, and matched-weight tests.
- `references/paper-derived-neural-presets.md` — source-of-truth audit and verification workflow for translating a manuscript plus runnable supplement into neutral visual atoms, an executable preset, and a representative-vs-full-model honest UI.
- `references/paid-gpu-architecture-experiment-operations.md` — Git-first remote deployment, paired-run controls, supervisor/monitor failure separation, artifact archival, and scale-aware throughput gates for rented accelerators.
- `references/repository-verification-evidence.md` — safe verification in dirty worktrees: runtime selection, layered gates, baseline isolation, platform-failure triage, and evidence-accurate reporting.

## Verification Checklist

- [ ] Public API names match the user's architecture language.
- [ ] Wrong/generic entry points are rejected or unexported.
- [ ] Tests cover the corrected contract, not just happy-path behavior.
- [ ] Traces/schemas include required architecture metadata when relevant.
- [ ] Existing unrelated modified files are left untouched.
