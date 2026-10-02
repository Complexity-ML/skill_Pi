---
name: ml-architecture-review
description: Review ML/AI architecture claims and turn them into defensible model definitions, baselines, and experiment plans.
metadata:
  hermes:
    tags:
    - ml
    - architecture
    - research
    - baselines
    - multimodal
    - model-design
    related_skills:
    - research-paper-writing
    - arxiv
    - systematic-debugging
  hermes_frontmatter:
    version: 1.0.0
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

# ML Architecture Review

Use this skill when the user asks for an opinion on a model/framework/research architecture, asks whether a claim is credible, or wants to define a new architecture without immediately editing code. Operate in audit/design mode unless the user explicitly authorizes file changes.

## Workflow

1. **Stay read-only unless explicitly authorized**
   - If the user expresses low trust or says not to touch files, switch to audit-only: inspect, reason, and propose changes without applying them.
   - Do not offer sweeping refactors as if they are already approved.

2. **Inspect the actual implementation before judging claims**
   - Read README/package metadata plus the specific model modules that implement the claim.
   - Search for concrete symbols: output heads, decoders, generation methods, shared-expert paths, target-query construction, routing functions, and losses.
   - Distinguish docstring/marketing claims from implemented behavior.

3. **Define the architectural contract precisely**
   - State what inputs are accepted, what outputs are produced, and whether outputs can target modalities absent from the input.
   - For “any-to-any”, require a source/target split: source tokens + target query tokens + target-specific heads. Reconstruction of modalities already present is not enough.
   - For routed architectures, write the per-token equation and the routing key.

   **Run a notation-stripped equivalence audit before implementation, paid compute, or submission.** Rewrite the proposal using canonical tensor operations and ask whether a bijective renaming maps it to an established mechanism. For example,
   $R=hW_R$, $W=hW_W$, $V=hW_V$, followed by $\operatorname{softmax}(RW^\top)V$, is in the Q/K/V family under $R\leftrightarrow Q$ and $W\leftrightarrow K$ unless an actual constraint or additional signal changes the operator. Compare head grouping, dimensions, normalization, positional transforms, parameter tying, cache behavior, and direct input dependencies—not the semantic names assigned to tensors.
   - If the proposed novelty disappears under renaming, say so **before** drafting the title/abstract or recommending submission. Do not use a small empirical delta between isomorphic parameterizations as proof of a new attention class.
   - Locate the real differentiator explicitly. A token-identity term such as $R_{ctx}(h)+\beta R_{lex}(x)$ and $W_{ctx}(h)+\alpha W_{lex}(x)$ creates a direct lexical dependency that lexical-off Q/K/V does not have; $V$ may remain contextual. Then define matched controls that isolate that term.
   - Preserve the user's intended research target. If the user asks for lexical attention, do not silently make a lexical-off variant the headline merely because it benchmarks cleanly. Label lexical-off as a control/equivalence audit and keep the true lexical mechanism as the candidate.
   - Treat this audit as a hard pre-publication gate. Packaging, checksums, and clean multi-seed metrics cannot repair a missing novelty distinction discovered after posting.

4. **Separate current implementation from desired design**
   - Use labels such as “implemented now”, “claim implied by docs”, and “needed for the desired claim”.
   - Correct overstatements directly: e.g. a shared general MLP path is not automatically the same thing as a paper-style universal shared expert.

5. **Make baselines reviewer-proof**
   - Define the base model unambiguously: same tokenizer/interface/data/optimizer/training budget, but with the experimental component removed or replaced.
   - Prefer controlled internal baselines before external frontier comparisons.
   - For routed + shared designs, compare at least dense, routed-only, shared-only, and routed+shared under matched compute/active-parameter budgets when feasible.

6. **Give a minimal viable research path**
   - Start with the smallest modality/task pair that can validate the claim.
   - Delay audio/video/full-stack claims until text-image or another minimal pair proves the mechanism.
   - Keep public framing honest: experimental/sandbox/future-work until there are results.

7. **Audit attention-free inference claims in stages**
   - Distinguish full-sequence training correctness, cached incremental correctness, graph-friendly design, and verified CUDA Graph capture. Evidence for one does not establish the others.
   - Before calling a QKV replacement inference-ready, require strict causality, full-versus-incremental logit equivalence, fixed state shapes, no prefix recomputation, and a cached-decode benchmark.
   - Treat stable state addresses and static control flow as prerequisites for CUDA Graph, not proof. Verify actual capture and repeated replay on the target CUDA stack.
   - For finite-context mixers, calculate and report the effective receptive field against the evaluated sequence length.
   - See `references/attention-free-inference-and-cuda-graphs.md` for the detailed architecture and deployment checklist.

8. **Identify the canonical control from primary evidence before modifying it**
   - Read the actual results table and raw metrics before assigning a remembered loss or throughput number to a mechanism. Do not infer that a round number such as “126k tok/s” belongs to GQA, WVR, or convolution from conversational memory.
   - Separate three questions: fastest attention-free mechanism, attention-free mechanism closest in quality to the attention control, and absolute dense-attention throughput. They may be different rows.
   - Before adding attention or another mechanism, restore the exact canonical baseline and remove rejected selectable variants from config/CLI/tests. Then benchmark baseline and candidate back-to-back in the same runtime; compare relative overhead rather than mixing archived and live absolute throughput.
   - Before claiming that a candidate beats a baseline, audit the optimizer schedule from raw per-step metrics as well as serialized configs. Equal data, seed, token budget, parameter count, and hardware are still not a matched architecture comparison when peak learning rate, warmup, decay, checkpointing, or numerical settings differ. Report such rows as descriptive cross-run observations and name the missing rerun explicitly.
   - Require one archived raw artifact per table row. If an intermediate run exists only in chat, a terminal log, or remembered output, omit it from the submitted table; without that row, do not attribute a later gain to one component when multiple factors changed together.
   - Checkpoint availability is part of the evidence contract. A completed metrics CSV without a final checkpoint can support loss/throughput reporting, but not post-hoc claims about learned gates, routing tables, state tensors, or which residual was actually used. Disclose the limitation and require checkpoint saving in confirmation runs.
   - A baseline CSV without its realized config supports only the numeric metric row. It does not establish matched tokenizer, dimensions, parameter count, seed, token budget, optimizer, kernels, or evaluation construction. Likewise, one logged throughput value is a point measurement, not a reproducible speedup estimate.
   - Zero-initialized residuals prove neutral initialization only. Without a residual-off run or a saved final checkpoint showing that gates opened, do not attribute the result to that residual or foreground it causally in the title. If a transition changes layer placement and normalization together, call it an architecture-path comparison, not an isolating ablation.
   - When the reviewed code is corrected after the run, enumerate behavior-changing fixes and label the supplement an audit-corrected implementation rather than an exact historical snapshot. Causal attention replacements specifically require tests with no mask, bool/additive padding masks, one-token cached decode, and multi-token cached chunks; cached `q_len != kv_len` does not make a multi-token chunk non-causal.
   - Preserve architecture vocabulary across API boundaries. For W/R/V attention, `q`, `k`, and `v` may be unavoidable FlashAttention argument names, but code, equations, and discussion should remain Write/Read/Value. Distinguish using a flash-style kernel from changing the mechanism to attention.
   - When the user rejects a paid-GPU candidate, stop it immediately and verify VRAM release before redesigning.
   - See `references/minimal-attention-threshold-ablation.md` for the restore-first and 0/1/2-layer attention protocol.

9. **Run a paper-wide architecture consistency pass before requesting more compute**
   - Trace the exact evaluated configuration through the abstract, equations, architecture prose, tables, captions, theory, experiments, conclusion, and supplement. A top-1 equation cannot silently stand in for a top-$k=2$ experiment; a stated shared-expert width must match the configuration table.
   - Treat evaluated checkpoints as higher-authority evidence than run names, intended configs, source comments, or plots. Inspect saved `config`, launch `args`, tensor shapes, and persistent routing tables with memory-mapped loading before rewriting claims.
   - For deterministic routing, test the complete saved table against exact candidate rules (modulo, permuted modulo, hash, frequency bin-packing) on every layer. Separately distinguish vocabulary assignment counts from observed corpus traffic.
   - Trace dataset-specific initialization branches for silent fallbacks. A frequency table populated for local text but not for a streaming dataset invalidates a frequency-aware claim even when the run and config are named “zipf.”
   - Distinguish routed experts from the expert-selection mechanism: a static top-k lookup still routes through experts even though it has no learned router. Treat learned shared/routed branch scalars as branch gates, not expert selectors. Name ablations by exact realised primary and secondary rules (for example, modulo-primary/balanced-secondary versus modulo-adjacent), not ambiguous labels such as “default fallback.”
   - Deduplicate resumed metric CSVs by step before trailing-window summaries, and compare candidate/baseline at the last common validation checkpoint and equal token budget.
   - Search for stale mechanisms and examples from earlier designs (old routing rules, removed controllers, obsolete model scales, masked-dispatch cost claims). Remove them rather than preserving a historical narrative in the main architecture section.
   - Build a claim-to-evidence ledger. Every assertion such as functional specialization, per-expert perplexity, balance, deployment compatibility, or benchmark superiority must point to an actual table, figure, or reproducible measurement. If the measurement is absent, narrow the wording to a hypothesis or interpretation.
   - Prefer deleting fragile theory over defending it with proof sketches. Disjoint data partitions do not by themselves imply independent or orthogonal gradients; generic universal-approximation results do not establish the benefit of the proposed routing mechanism. Keep only formally defined propositions that describe the implemented model.
   - Check that validation evidence is numeric and reproducible: dataset/split, number of examples or batches, evaluation cadence, checkpoint matching, and exact values—not only a curve and prose saying one model “remains ahead.”
   - Audit release and reproducibility statements against actual artifacts. Do not promise weights, checkpoints, complete code, or public release unless those artifacts really exist in the submission plan.
   - Treat the supplementary artifact as a second executable claim surface, not merely an attachment. Enumerate every training entrypoint, YAML, launcher, tokenizer, and default; remove unrelated legacy profiles that can start a different architecture under the same model-size label. A single verified experiment should have one unambiguous canonical launcher or a serialized exact command.
   - Verify startup semantics through the real parser. Load every YAML with the production config-merging path, construct the resulting model config, and assert checkpoint-grounded dimensions, routing strategy, top-k weights, branch-gate initialization, tokenizer vocabulary, seed, dataset, token budget, and world-size interpretation. Reading YAML fields alone misses parser defaults and launcher overrides.
   - Audit weighting semantics as separate namespaces. Fixed top-$k$ mixture weights (for example, 0.5/0.5 between two selected experts), learned shared/routed branch gates, and the final learned gate tensor values are different quantities. Record each with its provenance and lifecycle stage (configured initialization versus checkpoint value); never copy one into another merely because the numbers look plausible. When metric summaries, launch notes, current defaults, and checkpoint tensors disagree, preserve the disagreement until the saved config/args establish what was initialized and the state dict establishes what was learned.
   - Distinguish an exact historical snapshot from an audit-corrected reproduction. If code is hardened after the run (for example, replacing a silent fallback with a named strategy and fail-loud validation), document that fact explicitly rather than claiming the corrected code is byte-for-byte what generated the checkpoint. Preserve historical metric filenames only as provenance while using verified runtime labels in tables and figures.
   - Package and load-test the exact tokenizer asset used by the evaluated checkpoint. Do not infer tokenizer identity from directory names or vocabulary size alone; verify source provenance and checksums, normalize filenames only in the packaged copy, and add a startup guard against an incompatible vocabulary.
   - Audit evaluation data construction, not just metric arithmetic. Two iterators over the same training split are not an independent validation split. Name such values as evaluation on a fixed stream or subset of the training split unless a held-out partition is actually implemented and documented.
   - Include the raw metric inputs needed to regenerate every reported table and figure. A plotting script without its CSV or log inputs is not an auditable result; throughput numbers likewise require raw logs or a documented aggregation method.
   - Audit non-canonical translations independently. A translated paper can retain removed theorems, stale routing mechanisms, false conclusions, or malformed tables even when the canonical source is corrected; run the same architecture and claim search on every language version before building deliverables.
   - Preserve reviewer-requested ablations when they remain informative, but relabel conditions from verified runtime behavior rather than intended config names. If controls collapse to equivalent assignments or use single seeds, present the table as exploratory, state the confound, and avoid causal ranking claims instead of deleting the evidence.
   - Regenerate every architecture, routing-distribution, and ablation figure from verified checkpoint tables or raw metrics. A corrected paragraph is insufficient if a PNG still carries an obsolete mechanism name, invented assignment counts, or stale gate values.
   - Move implemented-but-unevaluated mechanisms to Future Work rather than the evaluated method. Specify the validation protocol needed next (data provenance, serialized routing-table hash, expected/realized traffic checks, matched baseline, seeds) so silent fallback cannot recur.
   - When compute is constrained, first use existing checkpoints/logs for frequency-binned loss, token-level error slices, exact validation tables, and bootstrap uncertainty. Multi-seed large-scale runs are not the default remedy; narrowing claims is often valid.
   - When generalizing a shared-plus-routed result, frame it as a bounded design principle: a regular dense computational substrate plus a narrow conditional residual, $y=F_{dense}(x)+\alpha G_{conditional}(x,z)$. State explicitly that shared execution does not make arbitrary Python objects kernel-compatible: conditional modules still need tensors, registered parameters, differentiable operations, and sometimes grouped GEMM or custom kernels. If measured routed throughput is lower, present the pattern as an integration strategy rather than an efficiency theorem.
   - Run a closest-prior-work novelty search on the exact mechanism, not only the broad family. For token-identity routing, check fixed/hash layers; for shared-plus-routed decomposition, check shared-expert MoEs and any statistical analyses. Cite such work as motivation and differentiation, and do not transfer guarantees whose routing or estimation assumptions differ from the evaluated model.

## Peer-to-peer and Discord responses

When the user asks for a response to a technical peer, especially for Discord:

- Return one paste-ready fenced `text` block when they want to copy it directly.
- Synthesize rather than reproducing the full audit: lead with the architectural intuition, then 3–8 compact risks or conclusions.
- Keep equations only when they materially clarify the mechanism; avoid turning a conversational reply into a paper review.
- If the user asks to make it shorter, substantially compress it instead of merely trimming a sentence or two.
- Preserve epistemic scope in the concise version: distinguish implemented behavior, diagnostic evidence, and future direction.

## Pitfalls

- Do not conflate “shared attention” or “general MLP” with a universal shared expert unless every token explicitly passes through a shared expert in parallel with its routed expert.
- Do not call a model “any-to-any” merely because it has several modality heads; it must generate target modalities that are not provided as inputs.
- Do not claim to beat vague “base models”. Define the matched dense/base architecture exactly.
- Do not compare against frontier proprietary any-to-any systems unless the task, data, compute, and evaluation are framed honestly.
- When the user corrects your interpretation, acknowledge and restate the corrected claim before continuing.

## References

- See `references/attention-free-inference-and-cuda-graphs.md` for the detailed architecture and deployment checklist.
- See `references/attention-free-llm-validation.md` for the matched-training, persistent-state, pointer-stability, and CUDA Graph claim ladder used when replacing QKV with convolutional or recurrent mixers.
- See `references/multimodal-any2any-routing.md` for a concrete checklist distilled from a Complexity-style deterministic routing discussion.
- See `references/reviewer-driven-architecture-cleanup.md` for cleaning an architecture paper after reviews identify unsupported or removed mechanisms in the title/abstract/theory/experiments.
- See `references/checkpoint-grounded-routing-audit.md` for resolving paper/config/checkpoint contradictions, detecting routing fallbacks, deduplicating resumed metrics, repairing stale figures, and hardening an audit-corrected supplementary artifact. Run `scripts/audit_routing_checkpoint.py` to inspect persistent routing tables in a PyTorch checkpoint.
- See `references/supplement-startup-equivalence.md` for verifying that packaged launchers, parser defaults, YAML overrides, tokenizers, raw metrics, token budgets, and translated papers reproduce the checkpoint-grounded claim without ambiguous startup paths.
- See `references/minimal-attention-threshold-ablation.md` for restoring a canonical attention-free control, distinguishing historical from live throughput, preserving W/R/V vocabulary at FlashAttention API boundaries, and measuring the minimum number of attention layers needed to close a quality gap.
- See `references/wvr-paper-and-artifact-audit.md` for defining fixed-state Write/Value/Read mechanisms, distinguishing them from QKV without overreaching into KV-cache claims, extracting last-finite evaluations from raw CSVs, and auditing multilingual paper/artifact contradictions.
