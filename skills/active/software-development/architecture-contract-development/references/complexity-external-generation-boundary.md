# Complexity external generation boundary

Session learning: when improving Complexity Framework as a PyTorch-layer framework, do **not** make native `model.generate()` the framework generation path if the user has stated that generation should be handled by vLLM/SGLang.

## Contract

- Complexity's PyTorch layer owns model definition, forward passes, training, checkpointing/export, and config/preset management.
- Text generation and serving are external runtime concerns: vLLM, SGLang, or another OpenAI-compatible serving backend.
- Public examples/docs should not present `model.generate(...)` as the recommended UX.
- If a legacy `generate` API remains for compatibility, it should fail loudly or delegate explicitly to an external serving client, not run an in-process autoregressive PyTorch loop.

## Implementation pattern

1. Trace all generation entry points before editing:
   - model methods (`ComplexityModel.generate`, wrapper `Model.generate/chat`)
   - public docs/docstrings (`complexity/__init__.py`, `models/__init__.py`)
   - CLI commands (`complexity inference generate`, `serve`)
   - API convenience wrappers (`complexity.api.inference.Generate`)
   - tests asserting generation behavior
2. Convert the user correction into tests:
   - assert native `ComplexityModel.generate(...)` raises with a message mentioning vLLM/SGLang
   - add tests for any external client payload/endpoint behavior
3. Add a small external-serving boundary rather than a generic generation framework:
   - e.g. OpenAI-compatible client for `/v1/completions` and `/v1/chat/completions`
   - backend field constrained to `vllm` / `sglang` if that is the user-stated boundary
4. Update CLI wording and arguments:
   - use `model`/served model id, not local checkpoint path
   - require/accept `--backend vllm|sglang` and `--base-url`
5. Remove misleading examples that call `model.generate(...)`.

## Pitfalls

- Do not defend native generation as useful for smoke tests once the user says generation must be vLLM/SGLang.
- Do not leave old docstrings advertising `model.generate(...)`; they become public API promises.
- Do not broaden this into “any inference backend” if the user named specific serving runtimes.
- Do not confuse low-level inference utilities (KV cache, batching, speculative helpers) with the product-level generation path.
