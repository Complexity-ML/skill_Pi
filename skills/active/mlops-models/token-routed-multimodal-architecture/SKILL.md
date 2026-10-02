---
name: token-routed-multimodal-architecture
description: Design and implement Token-Routed multimodal/any-to-any architectures with deterministic routing, Zipf balancing, target queries, and universal shared experts.
metadata:
  hermes:
    tags:
    - mlops
    - multimodal
    - token-routing
    - any-to-any
    - pytorch
    - architecture
    related_skills:
    - test-driven-development
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

# Token-Routed Multimodal Architecture

Use this skill when designing, reviewing, or implementing multimodal Token-Routed models: text-image/audio/video routing, Any-to-Any generation, deterministic experts, Zipf-balanced text routing, and shared expert paths.

## Core framing

- Treat text Token-Routed (TR) results as the established baseline result when the user says TR already beats the base model. Do **not** keep re-litigating whether TR can beat a dense base; the task is usually to extend the winning TR mechanism.
- For multimodal work, phrase the next step as: **generalize deterministic lexical routing to deterministic structural routing**.
- Avoid overclaiming. A joint encoder with reconstruction heads is not true Any-to-Any unless target modalities can be requested when absent from sources.

## Architecture checklist

1. **Separate source tokens from target query tokens**
   - Source tokens are the modalities actually provided as inputs.
   - Target query tokens are learned/generated query slots for modalities to produce.
   - Any-to-Any means outputs can be produced for target modalities absent from sources.

2. **Use the paper-aligned TR block**
   - Each token should activate:
     ```text
     deterministic_routed_expert(route_id, x) + universal_shared_expert(x)
     ```
   - Do not confuse a generic/general MLP pass with the paper's shared expert unless every token explicitly passes through a universal shared expert alongside its routed expert.

3. **Route deterministically by modality-specific structure**
   - Text source tokens: lexical/Zipf-balanced token-id routing.
   - Image tokens: spatial patch routes (position, quadrant, rings, Hilbert/Z-order, or balanced structural bucket).
   - Audio tokens: temporal or time-frequency routes.
   - Video tokens: spatiotemporal/tubelet routes.
   - Target queries: target modality + target position routes.

4. **Prefer discrete token heads first**
   - Text: vocab logits.
   - Image/audio/video: latent/codebook token logits when available.
   - Avoid claiming pixel/audio/video generation from a simple linear reconstruction head as production-grade generation.

5. **Keep legacy prototypes intact when trust/scope is sensitive**
   - If an existing `omni.py` or broad prototype exists, prefer adding a new module (`any2any_tr.py`) over rewriting it.
   - Preserve old code until the user explicitly asks for migration/removal.

## Implementation workflow

1. Confirm the workspace/repo is allowed before editing. If the target repo is outside the active workspace, switch projects or ask the user to open it.
2. Inspect current multimodal modules and tests.
3. Use TDD for the first public API:
   - test Zipf routing balance/stability,
   - test source-only image -> text target,
   - test source-only text -> image target,
   - test shared expert sees all source + target tokens,
   - test public exports.
4. Implement the minimal model surface:
   - config dataclass,
   - modality enum,
   - Zipf/structural router,
   - routed+shared MLP,
   - target query builder,
   - Any-to-Any model forward contract.
5. Export from the package namespace only after a failing export test.
6. Run targeted tests, import tests, syntax compile, and `git diff --check`.
7. If the repo has unrelated dirty files, do not touch or stage them; call them out in the final report.

## Public API pattern

Prefer a source/target contract like:

```python
out = model(
    sources={"image": image_tokens},
    targets={"text": 64},
)
assert "text_logits" in out
```

and:

```python
out = model(
    sources={"text": text_tokens},
    targets={"image": 256},
)
assert "image_logits" in out
```

This is materially different from reconstructing only modalities present in the input.

## Pitfalls

- Do not call a model Any-to-Any if `forward()` only emits heads for modalities present in the inputs.
- Do not describe position-routed image/audio/video paths as lexical routing. Use “structural routing.”
- Do not call a general MLP a shared expert unless it is explicitly parallel/composed with a routed expert for every token.
- Do not push claims against frontier any-to-any systems unless external benchmarks exist. The clean controlled claim is extending the already validated TR mechanism to multimodal Any-to-Any.
- If the user says “TR already beats the base model,” acknowledge that as premise and move to the Any-to-Any extension rather than explaining base-model comparisons again.

## References

- See `references/any2any-tr-implementation.md` for a concrete session-derived module/test scaffold and verification recipe.
