---
name: stateful-attention-free-serving
description: Build and validate production inference backends for attention-free causal models with fixed-size per-request state, including prefill/decode APIs, scheduler integration, CUDA Graph capture, packaging, and framework-equivalence tests.
metadata:
  hermes_frontmatter:
    version: 1.0.0
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
- Legacy Hermes references used in the source:
  - `memory` → explicitly requested persistent Markdown notes.
- There is no default Pi `memory` tool. Do not automatically store personal or sensitive information. Ask before creating persistent notes.
- Source compatibility has been adapted, but runtime behavior and third-party dependencies have **not** been tested.

# Stateful Attention-Free Serving

## Trigger

Use this skill when adapting a causal convolution, recurrent, or state-space language model to a production serving engine that is normally organized around Transformer KV caches.

## Core rule

Preserve the model's native state contract. Do not invent Q/K/V tensors or disguise convolutional/recurrent state as a growing KV cache merely to satisfy an attention-oriented interface.

## Workflow

1. **Freeze the reference contract**
   - Load a completed checkpoint and its realized model configuration.
   - Define `allocate_state`, `reset_state`, `prefill`, and `decode_step` in the reference framework.
   - Record exact state shapes, dtypes, receptive spans, and pointer-stability requirements.

2. **Prove eager equivalence first**
   - Compare full-forward logits with token-by-token cached logits.
   - Test batch size 1 and greater, prompt boundaries, reset/reuse, and mixed request lengths.
   - Compute only final-token logits when evaluating a large vocabulary; avoid allocating `[B,T,V]` unnecessarily.

3. **Map to the serving scheduler**
   - Reuse request scheduling, continuous batching, sampling, tokenization, and API layers.
   - Associate fixed state buffers with scheduler slots/request IDs.
   - Use existing recurrent/SSM state infrastructure (for example Mamba support) as the closest pattern when the engine is KV-centric.
   - Define explicit slot copy, swap, reset, prefill, decode, and request-finalization semantics.

4. **Make CUDA Graph constraints explicit**
   - Static input and state shapes per graph bucket.
   - Preallocated buffers with stable addresses.
   - No token-dependent Python control flow, `.item()`, allocation, or CPU synchronization inside capture/replay.
   - Warm up on a side stream; capture and replay repeatedly; compare eager and graphed outputs.
   - Maintain separate graph buckets for batch sizes and prefill lengths when needed.

5. **Package correctly**
   - A prebuilt wheel is an installation artifact, not an editable source base.
   - Modify the source fork, then build a fresh wheel on the target Linux/CUDA/Python ABI.
   - Inspect release wheel tags (`cpXY`, platform, architecture) before reuse.
   - Keep downloaded wheels in an ignored artifact directory, not in source control.

6. **Verify on target hardware**
   - Install the rebuilt wheel in a clean environment.
   - Run model-load, prefill, decode, reset, concurrent-request, and OpenAI-compatible API smokes.
   - Measure TTFT, decode latency/token, throughput, peak memory, state bytes/request, capture time, and replay overhead.
   - Do not claim CUDA Graph compatibility before real target-device capture and replay.

## Testing strategy

Use TDD for each seam:

- checkpoint key mapping;
- state allocation and shapes;
- full/eager incremental equivalence;
- slot reset and reuse;
- batching and scheduler state movement;
- CUDA Graph eager/replay equivalence;
- API-level generation.

Keep mocked scheduler tests clearly separated from real GPU integration tests.

## Pitfalls

- Treating an attention-free model as PagedAttention with fake KV blocks.
- Reordering learned operations during adaptation while only testing the new full path against its own decode path; also compare against the reference framework and real checkpoint.
- Writing the current token into a ring before reading a maximum-delay entry that aliases the same slot.
- Mapping padded graph rows onto a real request state slot instead of reserving or kernel-masking padding state.
- Recomputing the entire prefix during decode.
- Producing logits for every prompt position when only the final position is needed.
- Editing or unpacking a wheel as though it were maintainable source.
- Building CUDA extensions on macOS and assuming ABI compatibility with Linux/H100.
- Updating a live training checkout during a reproducibility-sensitive run.
- Claiming performance from unit tests or design intent rather than measured target hardware.

## Project-specific references

See `references/complexity-causal-conv.md` for the current Complexity/vLLM adaptation notes and file map.