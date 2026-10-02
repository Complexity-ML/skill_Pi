---
name: anonymous-paper-submission
description: Prepare double-blind paper submissions and supplementary ZIPs without identity leaks.
license: MIT
metadata:
  hermes:
    tags:
    - research
    - paper-submission
    - double-blind
    - anonymization
    - supplementary-code
    - openreview
    - tmlr
    related_skills:
    - research-paper-writing
    - requesting-code-review
    - ml-ablation-experiments
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

# Anonymous Paper Submission

## When to Use

Use this skill when preparing, auditing, or uploading double-blind research submissions, especially when the user is submitting to TMLR/OpenReview/ICLR/NeurIPS/ICML or attaching supplementary material such as code, data, figures, PDFs, or ZIP files.

Triggers:
- User asks whether a paper/supplement is anonymized.
- User is about to submit/upload to TMLR/OpenReview or another double-blind venue.
- Supplementary code is copied from a real repo or experiment harness.
- A paper archive/ZIP/PDF includes source code, LaTeX build outputs, checkpoints, logs, generated figures, or metadata.

## Core Rule

Treat **everything uploaded for review** as part of the anonymous submission: PDF, appendix, supplementary ZIP, code, data, README, licenses, package metadata, generated logs, and PDF metadata.

For TMLR specifically, the author guidelines state that supplementary material may include source code/data/videos in PDF or ZIP format, and: **“Like submissions, supplementary material must be anonymized.”**

## Workflow

1. **Check the venue rule first**
   - Verify whether supplementary material must be anonymized. For TMLR, yes.
   - Do not rely on memory; use the current venue guidelines if accessible.

2. **Prefer a clean anonymous ZIP over a public repo link**
   - Do not submit a GitHub/GitLab URL unless the repository owner, commit authors, issues, remotes, history, CI, and package metadata are anonymous.
   - Most real repos are not anonymous because of commit history, remote URL, org name, author emails, and issue/PR metadata.
   - Build a fresh review ZIP without `.git/`.

3. **Stage only necessary files**
   - Decide whether you are building a full submission archive or a supplement-only ZIP. For OpenReview/TMLR supplementary upload, prefer a supplement-only ZIP unless the venue/upload field explicitly asks for paper source/PDF inside the supplement.
   - Include supplementary code, configs, small tokenizer/config stubs, and reproduction README.
   - Include the paper PDF/source only when the target artifact is explicitly a full submission bundle; otherwise keep the paper PDF separate from the supplementary ZIP to avoid confusion.
   - Exclude checkpoints/model weights unless explicitly intended and anonymized.
   - Exclude large generated caches; for tiktoken, include only a tiny config such as `tiktoken_config.json` when sufficient, not cache blobs.

4. **Scrub identity metadata**
   - Replace names, emails, affiliations, org names, package authors, copyright owners, repo URLs, and public commit hashes that identify the authors.
   - Check `LICENSE`, `README`, `pyproject.toml`, file headers, comments, generated HTML, scripts, and every archived `run_config.json`/YAML copied from a training host.
   - Watch for local paths (`/Users/<name>`, `/home/<name>`, `/root/...`), tokenizer/checkpoint paths, paid-GPU IPs/hostnames, service names, and cloud run directories. Scrub only the review copy (for example `[REDACTED]/tokenizer`) so the original evidence remains intact.

5. **Remove build and cache artifacts**
   - Remove/exclude `.git/`, `.DS_Store`, `__pycache__/`, `.pytest_cache/`, `*.pyc`.
   - Remove/exclude LaTeX outputs that leak local paths: `*.log`, `*.aux`, `*.out`, `*.toc`.
   - Remove/exclude transient run logs unless they are intentionally part of the supplement and anonymized.

6. **Scan the final artifact, not just the source tree**
   - Create the ZIP.
   - Extract it to a scratch directory.
   - Scan the extracted content for identity strings and forbidden artifacts.
   - Inspect PDF metadata with `pdfinfo` and use `strings` on PDFs when possible.

7. **If supplementary code must reproduce experiments**
   - Before any architecture paper is frozen or uploaded, run the algebraic and matched-weight functional-equivalence gate in `references/architecture-novelty-equivalence-audit.md`. Packaging quality and directional multi-seed metrics do not establish novelty when the submitted operator is isomorphic to its baseline under renamed tensors or disabled gates. Explicitly classify the result as novel, equivalent, or dependent on an inadequately controlled component before telling the user to submit.
   - Before stopping or terminating a paid GPU instance, enumerate and mirror every run that may be cited: primary seeds, component ablations, negative controls, and historical numeric rows. Verify destination-side hashes before shutdown. Do not assume that preserving only the headline runs is enough; an unmirrored ablation must be excluded from the final quantitative claims unless recovered from the original host/store.
   - For controlled multi-seed studies, follow `references/controlled-multiseed-freeze.md` for the pre-shutdown freeze, deterministic bilingual-table generation, isolated staging test, and post-test clean rebuild sequence.
   - Preserve the actual run evidence (realized configs, raw metrics, source provenance, and table-generation logic). If the historical harness is shareable, snapshot the actual path rather than a stale reference implementation. If it is private/proprietary or too broad to disclose, do **not** make the supplement depend on it and do not copy the whole framework: build a standalone mini-framework that implements the same claimed equations, dimensions, data split, and parameterization, then state clearly that it is not a byte-identical historical snapshot.
   - For a new architecture claim, package the complete executable path: core mixer/attention replacement, conditional/object modules, model/block builder, config schema, incremental cache path, training/evaluation runner, and exact ablation configs. A parameter-name audit alone is not sufficient evidence. See `references/standalone-review-mini-framework.md` for the private-framework boundary, exact-count tests, provenance wording, and checkpoint policy.
   - Include raw CSV/JSON measurements and deterministic plotting scripts for every submitted table/PNG. Plots are derived artifacts, not substitutes for machine-readable results; do not create a conceptual architecture schematic when the user requested measured result figures.
   - Audit every numeric table row against a concrete local artifact before freezing the PDF. If a baseline value survives only in a run registry, chat transcript, paper macro, or remembered result, mark the missing artifact as a submission blocker and retrieve or mirror the original CSV/JSON. Never manufacture a replacement “raw” file from prose or memory. An internal draft may label the provenance gap explicitly, but the final reviewer package may not.
   - Treat experimental matching as a field-by-field artifact audit, not a prose label: compare peak learning rate, warmup/decay, optimizer, seed, data split, token budget, numerical mode, checkpointing, parameter count, and hardware from raw metrics/configs. If any consequential field differs, label the comparison descriptive rather than “matched.”
   - Checkpoints are optional for ordinary loss/throughput claims: realized configs plus raw metrics can support those measurements. Require a saved checkpoint only for claims about learned gates, routing tables, final residual usage, hidden-state probes, or post-training weight structure. If such a checkpoint is absent, disclose that limitation and narrow only the learned-state claim—not the unrelated loss/throughput evidence.
   - Do not infer a component ablation from two runs that change multiple factors. If the only intermediate result lacks a mirrored raw artifact, remove that row and state that the remaining joint change cannot isolate causality.
   - Include fail-closed tests for the paper's structural claims (for example no QKV projections/modules), realized parameter counts, tied-object identity, causality, full/incremental equivalence, fixed cache shape/address, and exact token budgets.
   - Add a manifest mapping each paper claim/figure/table to its config, raw artifact, regeneration command, and expected output. Future ablation artifacts should drop into the same stable directory/schema without repackaging the entire supplement.
   - Label old simplified code as `legacy/reference` if retained.
   - Keep reproduction paths anonymous while preserving scientific fidelity.

8. **Update the submission form as well as the PDF**
   - OpenReview/TMLR revision fields are independent artifacts. After changing the PDF, rewrite the title, abstract, “changes since last submission,” and supplement upload text to match the revised claims.
   - Do not leave old form prose about removed components, obsolete ablations, or future work that the paper no longer claims; reviewers read the form next to the PDF.
   - For rebuttals/revisions, first update the revision metadata and artifacts, then answer reviewers against the revised scope.
   - When a figure has been simplified, do not call it the “complete architecture.” Use “simplified schematic,” “overview,” or “300M schematic,” and make the caption match the real scope.
   - Read the compiled PDF page-by-page around changed floats. A large figure inserted between a paragraph setup and its bullet list can make the paper feel broken even if LaTeX compiles. Prefer a dedicated figure page (`figure[p]` plus `\FloatBarrier`) before the next subsection when a schematic is large.

9. **Handle AI-assistance concerns without escalating them**
   - If a reviewer questions AI-generated prose, freeze uploads and do not answer immediately with another polished, rapidly generated rebuttal.
   - Separate human scientific contributions from AI-assisted drafting, language editing, implementation, and artifact analysis. Disclose only what is true, but do not hide substantial assistance or describe author-directed work as autonomous AI invention.
   - Never claim universal verification when a rushed revision introduced inconsistencies. Acknowledge insufficient checking, accept author responsibility, and audit the exact uploaded PDF against raw evidence before replying.
   - Do not speculate about reviewer motives. Address concrete claims such as smoothed versus raw NLL, mixed train/eval tables, unsupported provenance, and unresolved experimental design.
   - Have the author rewrite any final disclosure in their own voice; the assistant should fact-check rather than produce prose that masquerades as unaided human writing.
   - Treat withdrawal as a separate consequential action: confirm whether the user means the complete submission or only a recent revision/comment. A reviewer recommendation is not yet an editorial decision.
   - Follow `references/ai-assisted-revision-disclosure.md` for the disclosure structure, metric audit, withdrawal guard, and resubmission recovery path.

10. **OpenReview/TMLR resubmission final pass**
   - Match the OpenReview title/abstract/change list to the exact revised PDF wording and limitations.
   - Choose “Long submission” if main content exceeds the venue’s regular-page limit; do not choose regular just because the form allows it.
   - Use “Beyond PDF” only for interactive webpage submissions, not for supplementary ZIPs or LaTeX source.
   - If the user wants paste-ready form content, return every field under its exact form label in a separate fenced `text` block. Keep upload paths and radio-button choices in their own blocks; do not bury options in prose. This enables one-click copying and prevents old form text from being mixed with its replacement.
   - After any final paper edit, recompile and regenerate hashes before giving upload paths. State which artifact changed (PDF versus supplement) so the user does not replace an unchanged attachment unnecessarily.
   - See `references/tmlr-openreview-revision-layout.md` for a compact checklist covering PDF layout, figure scope wording, and TMLR revision-field alignment.

## Verification commands

See also `references/tmlr-supplementary-anonymization.md` for a TMLR-specific supplement-only ZIP checklist, revision-form alignment checklist, dropped-component cleanup checklist, and final-gate scan commands.

Adapt the identity regex to the project/author:

```bash
# Extract and scan the final ZIP, not only the working tree.
rm -rf /tmp/submission_scan && mkdir -p /tmp/submission_scan
unzip -q dist/submission_supplement.zip -d /tmp/submission_scan

grep -RInE 'AuthorName|UserName|OrgName|email@example|/Users/name|/home/name|/root/|github.com/org|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' /tmp/submission_scan \
  --exclude-dir=.git --exclude-dir=tokenizer --exclude-dir=figures --exclude='*.pdf' --exclude='*.pyc'

find /tmp/submission_scan \
  -name '.git' -o -name '*.log' -o -name '*.aux' -o -name '*.out' -o -name '.DS_Store' -o -name '__pycache__' -o -name '.pytest_cache' -o -name '*.pyc'

pdfinfo /tmp/submission_scan/paper.pdf
strings /tmp/submission_scan/paper.pdf | grep -Ei 'AuthorName|OrgName|email|/Users/name|github.com/org'
```

## Pitfalls

- **Repo-link deanonymization:** A public repo link can reveal identity via owner/org, commits, issues, stars, CI, package metadata, and old branches. Upload a ZIP for review instead.
- **License leak:** `LICENSE` often names the real organization/author even when paper text is anonymous.
- **LaTeX log leak:** `.log` files can expose local TeX paths like `/Users/<name>/Library/texmf/...`.
- **PDF metadata leak:** The PDF may have an empty visible author but still include metadata or strings; inspect it.
- **Generated cache bloat/leak:** Tokenizer caches and Python caches can be huge or identifying; include minimal config stubs only.
- **Stale supplement trap:** A clean but wrong simplified supplement is not enough. If the claim came from a different training repo/harness, include an anonymized snapshot of that real path and remove/clearly exclude legacy paths that no longer correspond to the evaluated claims.
- **ABI-name false-positive trap:** Structural audits must distinguish computation from compatibility naming. An attention-free export may retain paths such as `self_attn` or `post_attention_layernorm` for a framework ABI while containing only convolutional mixer tensors. Fail on actual Q/K/V/QKV projections or unexpected module/tensor types, and document inherited names instead of either overclaiming or reporting a false violation.
- **Completed-run artifact amnesia:** Before retraining a claimed canonical model, search the original training host, persistent volumes, and artifact stores for its run directory. Mirror and hash `metrics.csv` and realized `run_config.json` immediately. Mirror a checkpoint only when a planned learned-state/weight claim requires it; do not make checkpoints a blanket prerequisite for loss/throughput evidence. A persistent cloud volume can often be remounted briefly to recover tiny CSV/JSON artifacts without rerunning training.
- **Top-level stale config trap:** After moving the real harness under a subdirectory (for example `supplementary_code/o200k_framework/`), scan and remove old top-level configs such as `supplementary_code/configs/model_config.json`. A single stale config with the wrong tokenizer/vocab/model shape can make the supplement look inconsistent even if the runnable harness is correct. Do not overgeneralize: generic framework defaults or paper tables may legitimately mention an older vocabulary size; remove the stale top-level artifact, not every occurrence of the number.
- **Concept-cleaning means complete removal:** When a reviewer/user says a component is no longer part of the paper (e.g. a dropped mechanism), do not leave it as “future work,” appendix framing, CLI flags, README prose, file names, figures, or inactive compatibility code in the review artifact unless explicitly required for backwards compatibility. Search code, docs, configs, figures, and ZIP contents for both prose names and implementation identifiers.
- **Supplement-only ZIPs:** If the venue accepts a separate paper PDF plus supplementary ZIP, build the supplement ZIP without the paper PDF/LaTeX source unless the submission form explicitly asks for a combined archive. Including the paper inside the supplement can confuse scans and review artifacts.
- **Ambiguous final-artifact location:** Do not make the user choose among a source tree, staging directory, `supplement 2`, and several ZIPs across worktrees. Build from one canonical mini-framework source, put the verified upload PDF/ZIP in the workspace the user actually browses, re-hash after copying, and identify the exact `.zip` to select. See `references/standalone-review-mini-framework.md` for final-delivery hygiene.
- **Mechanism-title overclaim:** Shared lexical routing in hidden states does not make the compared attention operator explicitly lexical. Name the paper after the controlled axis; reserve “lexical attention” for a direct token/object path into R/W/Q/K/V. See the naming section in `references/standalone-review-mini-framework.md`.
- **Renamed-operator novelty trap:** A Write/Read interpretation does not create a new attention class when `R=hW_R`, `W=hW_W`, and `softmax(RW^T)V` have the same dimensions, grouping, norms, RoPE, masking, and cache behavior as Q/K/V. Audit equations and copy matched weights before interpreting small training differences. Disabled or zero-gated lexical paths cannot support a lexical-attention claim. Follow `references/architecture-novelty-equivalence-audit.md` before submission.
- **Rendered-form clipboard trap:** OpenReview/TMLR may render TeX correctly while copying the rendered summary omits MathJax nodes. Verify the actual page Preview before rewriting a correct abstract; distinguish a clipboard extraction artifact from missing submitted content.
- **Post-push safety:** Pushing to a non-anonymous Git remote is not a valid anonymous supplementary submission. The review artifact should be the scanned ZIP; do not provide a GitHub link unless the repo owner/history/metadata are anonymous.

## Final Gate

Before telling the user the submission artifact is ready:

- [ ] Venue anonymization rule checked.
- [ ] Final ZIP created without `.git/`.
- [ ] Identity grep over extracted ZIP is clean.
- [ ] Artifact/caches scan over extracted ZIP is clean.
- [ ] PDF metadata/strings checked.
- [ ] Size under venue limit.
- [ ] Reproduction README points to anonymous paths only.
- [ ] Every reported table/PNG traces to raw CSV/JSON plus a deterministic regeneration command.
- [ ] Structural architecture claims are backed by the complete executable model path and fail-closed tests, not only parameter-name audits.
- [ ] Architecture novelty passed an algebraic and matched-weight equivalence audit under the exact submitted flags/config; renamed tensors, shared substrate, unused parameters, and zero/disabled gates are not counted as novelty.
- [ ] If the production harness is private/proprietary, the review code is a genuinely standalone mini-framework: clean install succeeds, paper configs rebuild exact parameter counts, tests pass from the extracted ZIP, and no private package import/directory remains.
- [ ] Negative checkpoint diagnostics and full/incremental discrepancies are preserved and scoped honestly; no polished figure is treated as validated until matched controls and numerical-mode checks are complete.
- [ ] User is warned not to submit a non-anonymous GitHub URL when the ZIP is the anonymous artifact.
