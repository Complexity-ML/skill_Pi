---
name: ml-research-validation
description: Validate causal sequence-model implementations and GPU experiments from code invariants through matched controls, provenance, and reviewer-ready evidence.
license: MIT
metadata:
  hermes:
    tags:
    - ml
    - causal-attention
    - gpu
    - ablation
    - reproducibility
    - paper-review
    related_skills:
    - test-driven-development
    - requesting-code-review
    - ml-ablation-debugging
    - github-pr-workflow
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
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# ML Research Validation

A fail-closed workflow for turning an experimental sequence-model result into defensible evidence. Use it for attention variants, recurrent/state-space mixers, cache implementations, architecture ablations, throughput claims, and paper review.

## Core rule

A good metric is not yet a scientific result. The implementation contract, comparison protocol, source/config provenance, and statistical surface must all survive independent review.

## 1. Audit implementation invariants before more GPU spend

For causal mixers, test more than tensor shapes:

1. Full-sequence causality with no mask.
2. Causality with an all-valid padding mask.
3. Bool and additive masks when supported.
4. Token-by-token cached equivalence.
5. Multi-token cached-chunk equivalence.
6. Non-default positional settings such as RoPE theta.
7. Fail-closed behavior for unsupported config flags.
8. Repository-wide residual-output initialization conventions.

Use TDD: add a test that fails for the suspected leak, verify RED, implement the smallest correction, then verify GREEN and the relevant sibling paths.

See `references/causal-sequence-review.md`.

## 2. Separate historical evidence from corrected code

If review finds a bug after a run:

- Determine whether the executed training path was affected.
- Never imply that corrected source is byte-identical to the historical run.
- Archive the historical metric as an observation.
- Require replication with the corrected source before promoting it to the headline result.
- Save the exact source revision, realized config, tokenizer checksum, checkpoint, environment versions, and raw metrics for the replication.

## 3. Design matched controls

Change one scientific factor at a time. Match model budget, non-target modules, data order, tokenizer, seed, token budget, precision, batch, context, optimizer, LR schedule, warmup, weight decay, clipping, compilation, kernels, loss backend, evaluation cadence, accelerator, and software stack.

If the candidate changes attention and MLP simultaneously, build a control with the same MLP and only the attention changed. If the headline names a lexical residual, include a residual-off control. If normalization is suspected, include the corresponding normalization-off control.

Stage cost: run one-seed matched controls, stop and interpret, then repeat only the two main arms on additional seeds if the first gate remains positive.

## 4. Native-engine evaluation contract

When the user names an inference engine, run the evaluation through that engine rather than a neighboring training-framework loader or generic generation script. Treat tokenization as part of the model contract:

- Inspect the tokenizer's registered special tokens and IDs before encoding.
- Do not infer that a defined BOS/begin token should be injected. For raw pretraining or refinement evaluation, explicitly encode with `add_special_tokens=False`, apply no chat template, allow no BOS fallback, and assert that no reserved special IDs occur in every benchmark input.
- Keep canonical checkpoint files immutable. Put loader-only aliases or derived-field omissions in a separate temporary adapter directory and record each adaptation.
- Pin and report checkpoint repository/revision, weight checksum, tokenizer repository/revision, engine source revision, device, dtype, dataset source/checksum, split size, scoring formula, and raw artifact path.
- For causal-choice benchmarks, report both total continuation log-likelihood accuracy and length-normalized accuracy. Never promote a smoke subset to a final benchmark result; disclose examples, choices, and scored continuation tokens.
- Explain timing in terms of the actual workload and backend. Teacher-forced choice scoring evaluates every continuation token for every option; eager MPS timing is not directly comparable to CUDA Graph generation throughput.
- Before borrowing an accelerator, verify whether it is serving a live training run. Do not interrupt or contend with training merely to accelerate an evaluation.

See `references/native-causal-choice-evaluation.md` for a TR-Hash/PIQA worked pattern and loader pitfalls.

## 5. GPU smoke discipline

A smoke is for correctness and steady-state throughput, not final quality.

- Run arms sequentially on one GPU.
- Exclude compilation and warmup from throughput.
- Detect non-finite loss/gates immediately and stop.
- Do not compress a full-run LR schedule into a tiny smoke: reaching peak LR in a handful of steps can create NaNs unrelated to the architecture. Use a documented low smoke-only LR, or preserve the full schedule horizon while bounding execution.
- Report median/mean/dispersion across a fixed post-warmup window, not one progress-bar point.
- Hardware changes require rerunning every throughput arm on the new hardware; never compare H100 throughput directly with H200 throughput.

See `references/gpu-smoke-and-evidence.md`.

## 6. Paper claim gate

For every headline sentence, map `claim -> run -> raw metric -> realized config -> source revision -> checkpoint`.

Downgrade claims when any link is absent:

- Different LR or missing config: descriptive cross-run ordering, not matched superiority.
- One seed: observation, not general superiority.
- One logged speed point: no reproducible speedup claim.
- Multiple factors changed: no causal attribution.
- No checkpoint: no post-hoc gate/mechanism interpretation.
- Backend merely enabled: say "configured to permit dispatch," not "executed," unless profiled.

## 7. Main-only workflow preference

When the user explicitly asks for a direct `main` workflow, do not create, push, or deploy an experiment branch.

1. Inspect all worktrees and the dirty state of the primary `main` workspace.
2. Commit the reviewed experiment changes.
3. Merge into the primary `main` worktree while preserving unrelated local edits (autostash if appropriate).
4. Resolve conflicts by combining intent; restore pre-existing edits to their original unstaged state.
5. Push `origin/main`.
6. Clone or fast-forward `main` on the GPU host and verify the exact revision.
7. For later config-only changes, stage and commit only those files so unrelated dirty work is not swept in.

Do not leave a paid GPU idle while discussing workflow; perform prerequisite checks and launch bounded setup/tests promptly.

## 8. Exit criteria

A result is reviewer-ready only when invariant tests pass; matched controls complete with finite metrics; raw artifacts, exact configs, revisions, and checkpoints exist; throughput is repeated and hardware-matched; claims fit the evidence; anonymous PDFs/supplement rebuild; and an independent adversarial reviewer finds no blocking issue.
