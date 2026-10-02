# Paper-Derived Neural Presets

Use this reference when turning a published architecture into a visual graph, compiler preset, or executable demo.

## Source-of-truth order

1. Use the exact manuscript/workspace named by the user. Do not infer the canonical paper from similarly named repos or historical copies.
2. Read both the manuscript and the runnable supplement. The prose establishes the scientific contract; executable code resolves projection order, tensor layout, gates, routing, and weight tying.
3. Inspect verified architecture figures or figure-generation scripts when available, but do not substitute the figure for code-level tracing.
4. Record conflicts explicitly instead of silently choosing one source.

## Decompose the claim correctly

Separate the ordinary backbone from the paper's novel path. For example, a model may retain standard GQA Q/K/V attention while applying lexical routing only inside the MLP residual. Never let a research adjective migrate onto unrelated Q/K/V or attention blocks.

Trace one decoder layer end to end:

- token embedding and any tied output head;
- pre/post normalization points;
- Q/K/V projections, Q/KV head counts, head dimension, QK normalization;
- positional transform, KV expansion, causal SDPA/Flash path, head merge, output projection, residual;
- shared MLP branch, routed branch, routing source, expert calculation, branch gates, residual;
- final norm/head and model-level repetition count.

Distinguish learned hidden-state routing from fixed token-ID lookup. A fixed routing table is not a learned router followed by Top-K, even when both produce expert indices and weights.

## Visual/compiler implementation contract

- Add neutral semantic atoms for missing operations rather than one hardcoded paper block.
- Keep port identity distinct from tensor role, including Q/K/V and same-type residual/branch inputs.
- Make declared settings operational. A `tieEmbeddingWeights=true` flag is incomplete unless generated modules share the exact same `Parameter` object.
- Implement the paper's actual expert nonlinearity. A SwiGLU expert needs gate/up/down projections; `Linear → SiLU → Linear` is not equivalent.
- If the canvas shows one representative layer, label it as such and expose the paper's repeat count. Do not call a single-layer graph the complete N-layer model.
- Prefer an expandable layer/model composite when the visual editor supports hierarchy; avoid flattening N identical layers on the primary canvas.

## Verification pattern

1. Add a contract test that asserts required atom IDs and rejects incorrect substitutes (for example, learned router atoms in a fixed-routing preset).
2. Compile all newly added primitives independently.
3. Run every primitive with real framework tensors.
4. Clone the paper graph into a shape-preserving miniature: reduce hidden width, heads, vocabulary, expert width, and layer count without changing topology.
5. Execute the miniature end to end and assert output shape, finite values, and identity-sensitive contracts such as tied weights.
6. Update UI tests for labels, typed ports, edge count, disconnection, deletion, and code round-trip.
7. Run full tests, lint, renderer build, and desktop build.
8. Restart the dev desktop process before visual verification. Hot-module replacement can preserve old React state initializers and make a corrected preset appear unchanged.
9. Inspect both the accessibility tree and rendered canvas; a green runtime test does not prove the architecture is visible.

## Session example: canonical TMLR routed-MLP preset

Canonical source supplied by the user: `~/Dev/tmlr-paper-pool`.

The manuscript and supplement established this separation:

- standard causal GQA attention: Q/K/V projections, 16 Q heads, 4 KV heads, head dimension 64, QK-Norm, RoPE, KV repeat, SDPA/Flash, output projection, residual;
- routing only in the MLP residual: shared dense SwiGLU plus four small routed SwiGLU experts;
- routing source: deterministic token-ID table, top-2 fixed weights, not a learned hidden-state router;
- branch gates initialized independently (shared 1.0, routed 0.1);
- tied token embedding and language-model head;
- one canvas layer is representative; the published 300M model repeats the decoder layer 18 times.

A durable runtime probe used a smaller graph with the same topology and asserted both logits shape and `model.head.weight is model.embedding.weight`.
