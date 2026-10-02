# Atomic Neural Research IDE Contract

Use this reference when building a visual/PyTorch research environment for composing models, tokenizers, or kernels from atomic operations.

## Product boundary

This is a bidirectional research IDE, not a static architecture diagram, educational Blockly clone, or catalog of canned variants.

```text
Manipulable blocks <-> typed IR <-> executable source
```

For model research, source targets are usually PyTorch. For tokenizer research, use Python as the executable reference backend and Rust as a production/performance backend; PyTorch is relevant only for learned tokenization or downstream model integration.

"Semantic" means typed computational intent and contracts (query, key, value, normalization, routing, residual, etc.), not a claim of natural-language understanding.

## Atomicity contract

Atomicity applies to the whole system:

- Nodes are operations with typed ports, settings, lowering rules, and optional provenance.
- Links are first-class typed atoms too: direct tensor flow, residual, gate, concat, broadcast/repeat, routing, parameter sharing, or shape transform.
- Links may remain hidden in the UI to avoid visual spaghetti; hiding them does not permit deleting or hardcoding them outside the IR.
- Shapes, parameter counts, code, compatibility status, and validation results are derived from the current IR.
- Never place plausible demo constants such as `98.18M params`, fixed head counts, static shapes, or hand-drawn edge paths directly in renderer code.
- A starter preset may carry concrete settings, but the UI must label it as a preset and let users edit those settings. A computed metric over an immutable preset is not yet an atomic editor.
- Blocks must be manipulable: select, move, configure, add, duplicate, delete, and encapsulate a connected subgraph as a reusable custom block.
- Unknown operations must survive round trips as typed custom source blocks rather than being dropped.

Turn these boundaries into tests before UI implementation: edit one atom, assert the source preset is unchanged, and verify generated code/statistics change from the edited graph.

## Hierarchical composition

Do not show a whole model as one flat canvas. Support expandable composites:

```text
Model
|- tokenizer artifact
|- token embedding / position
|- layer x N
|  |- norm
|  |- attention
|  |  |- Q/K/V projections
|  |  |- attention-head topology (MHA/MQA/GQA)
|  |  |- position transform
|  |  |- score/mask/aggregation
|  |- residual
|  |- norm
|  |- MLP/SwiGLU/MoE
|  |- residual
|- final norm
|- LM head (tied or untied)
|- loss
```

Both attention heads and the LM output head must be represented explicitly. A composite can be opened into atoms, edited, and closed into a custom block.

## Tokenizer Studio and Token Lab

Represent the full path:

```text
Dataset -> tokenizer pipeline -> token objects -> embedding/context -> model
```

Tokenizer atoms include normalization, pre-tokenization, byte mapping, BPE/Unigram/WordPiece, trainer, merge rules, special tokens, byte fallback, post-processing, and decoder. Typed links distinguish text, bytes, pieces, vocabulary, and token IDs.

A tokenizer artifact exposes family, files/checksum, normalization rules, special tokens, encode/decode, and checkpoint compatibility. Do not render an entire 200k vocabulary as blocks. Token Lab provides filtering and materializes only selected tokens as atoms with ID, displayed piece, exact bytes, length, special status, corpus frequency/rank, and tokenizer provenance. Never infer corpus frequency from numeric token ID order.

## Standalone atomic results

When the user asks whether one atom is "better" than another, do not introduce model training or LM loss by default. Compare autonomous implementations of the same atomic contract on matched synthetic inputs:

- forward and backward error against a reference;
- finite values and determinism;
- dtype/shape coverage;
- latency, memory, and allocations.

Only rank implementations that target the same semantic contract. If contracts differ (for example RMSNorm vs LayerNorm), report satisfied properties but refuse an unconditional winner. Use contract tolerances and Pareto-style verdicts (`candidate-better`, `baseline-better`, `inconclusive`).

Training loss is a separate architecture-level experiment, not an atomic implementation result.

## Desktop execution boundary

Electron is suitable for the desktop UI. Keep React in a context-isolated renderer and expose a narrow preload API. A local Python runtime/sidecar executes generated PyTorch and tokenizer reference code. Rust artifacts are built through a separate controlled backend. Renderer code never gets arbitrary filesystem, process, or IPC access.

In development, start the renderer and gate Electron startup on renderer readiness (for example with `wait-on`). A living Electron main process that logged `ERR_CONNECTION_REFUSED` is not a successful launch. After tests and both builds, launch the real app and visually inspect the primary Model and Tokenizer Studio viewports.

## Delivery sequence

1. Encode atom, link, edit, and lowering contracts in tests.
2. Implement the typed IR and operation registries.
3. Prove one vertical loop: manipulate an atom -> regenerate code -> execute -> show derived result.
4. Add hierarchical composites and custom blocks.
5. Add tokenizer/model studios using the same principles.
6. Only then add polished catalogs, provenance, Codex transformations, and experiment management.

## Failure patterns

- A beautiful canvas whose cards cannot be manipulated.
- A graph with hand-authored SVG edges while claiming links are atomic.
- Static library labels duplicated in UI rather than sourced from the operation registry.
- Hardcoded parameter counts or tensor shapes presented as live results.
- Architecture-specific branches hidden inside a supposedly generic compiler.
- Calling activation telemetry during training an "atomic result" when the request was an autonomous kernel/operator comparison.
- Promising arbitrary Python-to-block round trips; support a typed subset and preserve unsupported code as a custom block.
