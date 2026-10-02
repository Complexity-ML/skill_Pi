---
name: training-telemetry-contracts
description: Design architecture-aware training logs and control curricula through module-declared capabilities instead of trainer-side model-type conditionals.
metadata:
  pi_adapter:
    version: 1
    source: Hermes local skills
    runtime_verified: false
  copyright: Copyright (c) 2026 Complexity-ML
  ownership: Owner-confirmed original skill, generated with GPT in Hermes for Complexity-ML
license: MIT
---

## Pi compatibility

- This skill runs inside **Pi**, not the Hermes agent runtime. Use only tools actually declared in the current session.
- Resolve bundled scripts, templates, assets and reference paths relative to this `SKILL.md` directory. Preserve their contents and CLI syntax.
- Pi tool argument examples: `read({"path":"/absolute/file"})`, `write({"path":"/absolute/file","content":"..."})`, `bash({"command":"..."})`. Use `edit` for precise changes to existing files.
- Shell/Python/JavaScript code should run through `bash` using the appropriate interpreter; `execute_code` is not a default Pi tool. Do not pass natural-language pseudocode to an interpreter.
- Check prerequisites before running commands. Copying this skill does not install its CLIs, enable external services, or provide API keys.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Training Telemetry Contracts

Use this skill when a training framework supports multiple interchangeable architectures, routers, experts, residual branches, or optimizers and its CLI/logging must report only controls that actually affect the constructed model.

## Core principle

The built module tree is the source of truth. Generic CLI defaults are not evidence that a control is active.

A trainer must not print, schedule, or claim a control merely because the argument exists. Each participating module declares:

- which trainer-side curricula it supports;
- which scalar telemetry values it exposes;
- no capabilities and no telemetry by default.

## Contract

Give the common module base two side-effect-free methods:

1. `training_control_capabilities() -> frozenset[str]`
2. `training_telemetry() -> dict[str, float]`

Dense/default modules return empty values. Specialized modules override only what they own.

Examples of capabilities:

- `topk_primary_weight`
- `shared_routed_gates`
- `expert_diversity`
- `lexical_object_gate`
- `micro_expert_gate`

Telemetry names should be stable, concise progress-bar keys such as `topk_w`, `shared_gate`, `object_gate`, and `micro_gate`.

## Implementation workflow

1. Write a failing test where two different real module types declare different controls.
2. Add empty methods to the shared module base.
3. Override the methods in specialized modules.
4. Build a generic collector that scans modules, unions capabilities, and averages same-named scalar telemetry across layers.
5. Make the trainer gate curricula by declared capability, not class name, CLI value, or incidental attribute.
6. Build progress postfix fields from the collected telemetry dictionary.
7. Keep optimizer-specific details conditional on the selected optimizer.
8. Configure third-party loggers to avoid duplicated propagation while preserving fatal failures.
9. Run one real smoke per architecture family and assert forbidden fields are absent as well as required fields present.
10. Run targeted tests, full-suite tests, syntax/diff checks, then push.

## Verification matrix

For every supported architecture family, verify:

- the expected controls appear;
- irrelevant controls do not appear;
- reported values come from live parameters and change when those parameters change;
- unsupported curricula are not applied silently;
- legacy architecture behavior remains intact;
- warnings are not duplicated by library and root handlers.

A passing smoke should assert both positive and negative conditions. For example, a lexical residual run should contain object/micro gates and must not contain top-K or shared/routed gates.

## Pitfalls

- Detect structural capabilities once after constructing the model, but refresh learned telemetry only at logging intervals. Calling `.item()` every training step introduces needless device synchronization; doing it after the runner's normal log synchronization is acceptable.
- Keep configuration provenance separate from live telemetry: the realized run config records all arguments for reproducibility, while the human summary and progress bar show only controls supported by the built module tree.
- Do not call a runner “dynamic for the whole framework” after auditing only one runner. State the verified scope precisely.
- Do not infer architecture from YAML names; aliases and composed models make that brittle.
- Do not use incidental attribute probing as the final interface. It is acceptable for diagnosis, but modules should explicitly declare their contract.
- Do not restart a valuable active run solely to improve logging. Preserve its provenance and apply the correction to subsequent runs.
- Do not hide terminal network failures. Suppress duplicated retry chatter, but allow exhausted retries to fail normally.
- Do not bundle unrelated pre-existing full-suite failures into the telemetry fix; report targeted verification and identify unrelated failures explicitly.

## User-facing reporting

Lead with what changed and the verified scope. Distinguish:

- dynamic values read from live parameters;
- capabilities detected once from the constructed module tree;
- runners actually migrated;
- other historical runners not yet audited.

Never overstate “all framework runs” unless every runner has been searched, migrated, and smoke-tested.

## Reference

See `references/architecture-aware-runner-pattern.md` for a compact worked pattern and validation checklist.
