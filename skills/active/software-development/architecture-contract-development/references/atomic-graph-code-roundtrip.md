# Atomic Graph ↔ Executable Code Round-Trip

Use this reference when building node/Blockly-style ML editors where semantic blocks, typed cables, and generated framework code must stay aligned.

## Truth hierarchy

1. The typed graph IR is the source of truth.
2. Blocks and code are two projections of that IR.
3. X/Y position and camera state are presentation only; they must not affect generated code.
4. Topology, ports, block settings, and composite expansion are semantic and must affect code.

Never call a UI “synchronized” merely because a textarea is populated from a hardcoded template. A registry string that calls undefined helpers is a placeholder, not a lowering.

## Executable-block contract

A block is publicly available as executable only when all of these hold:

- stable block/node ID;
- typed input and output ports;
- concrete module declaration or functional operation;
- concrete forward invocation using values from incoming edges;
- settings materialized as valid framework literals;
- generated source executes in the pinned runtime;
- deleting the block removes its declaration and invocation;
- unsupported edits produce diagnostics rather than silent drift.

Disable or clearly label planned blocks whose lowerings still reference undefined helpers. Never show a global green synchronization status when only a subset of blocks is supported.

## Block deletion versus cable deletion

These are different semantic mutations and must never share one fallback:

- **Delete a block:** remove that block's module declaration, managed node marker, forward invocation, and incident edges.
- **Delete a cable:** retain both endpoint block declarations; remove only that edge marker and its dataflow contribution. If a target no longer has every required input, omit its forward invocation rather than deleting its declaration, inventing an external argument, or replacing the entire file with an `InvalidGraph` stub.
- Continue lowering independent branches whose required inputs remain available. Return the last executable sinks so the partial program remains valid and representative of the current topology.
- Validation may still report the open required port. Validation diagnostics and interactive code generation are separate contracts: a locally invalid cable state must not erase unrelated code.

When a user gives a visual analogy such as a “2D table” or “perfect/imperfect pattern,” first identify the underlying block/cable/code invariant. Do not implement the literal analogy until the user confirms it is the desired product surface.

## Cable/code contract

Emit stable managed markers for every semantic connection, for example:

`# labo:edge=<id> source=<node> target=<node> source_port=<port> target_port=<port>`

The code parser must round-trip these markers:

- deleting a managed edge marker removes the cable;
- changing source/target rewires the cable after endpoint/type validation;
- unknown endpoints, cycles, and type mismatches return diagnostics and do not silently mutate the graph;
- generated forward order comes from topological order, not renderer order or X/Y coordinates;
- topological tie-breaking is stable by canonical node order, never by edge-array insertion order, so disconnecting and reconnecting the same cable cannot reorder unrelated generated code.

For a collapsed composite, multiple internal links may be rendered as one visual bundle, but they remain distinct IR edges and separate again when expanded.

## Parallel atomic execution levels

A graph is not a flat `nodes[]` playback list. For a valid graph, derive stable Kahn-style dependency levels from typed edges:

- nodes in the same level have no dependency on each other and may be shown/executed as one parallel wave;
- mark the whole wave running/passed together (`Promise.allSettled` is suitable for the UI controller);
- green means passed, blue means the current level, gray means not yet executable, and red means the first concrete failure;
- keep ordering inside one level stable by canonical node order;
- reconnection may change dependency levels only when topology actually changes, not because the edge was appended later.

For an invalid open-port graph, preserve the authored/canonical block order when locating the first atomic error. Otherwise a disconnected target has indegree zero and a naive topological sort incorrectly promotes it to the first stage. The runtime should resolve values by exact `sourcePort`/`targetPort`, execute all preceding valid atoms, fail at the first block missing a required port, and never mark later atoms as passed.

## Real verification

For each newly supported semantic block/composite:

1. RED: assert generated code contains every managed node and edge marker.
2. RED: rewire one edge through an intermediate block and assert the generated invocation changes.
3. Assert moving only X/Y leaves generated code byte-identical.
4. Parse an edited marker back into the graph and verify the cable change.
5. Execute generated source with the real framework runtime and check output shape/dtype.
6. For training-capable blocks, add forward/backward and gradient checks.
7. Only then expose an “executable/synchronized” status.

A static string assertion is insufficient evidence of executable PyTorch.

## Elastic node-editor geometry

Use one world transform for cards, ports, and SVG/canvas cables. Convert screen↔world coordinates around the same pan/zoom state. Recompute cable geometry when:

- graph topology or node positions change;
- camera pan/zoom changes;
- selection expands or collapses inline editors;
- cards resize (`ResizeObserver`);
- composites expand/collapse;
- window/canvas size changes.

Ports centered on card boundaries require visible overflow; otherwise they are clipped in half. Composite headers must be draggable, while controls/ports/settings remain interactive. Provide wheel/trackpad X/Y pan, pointer-centered pinch/ctrl-wheel zoom, background or middle-button drag, zoom controls, and fit-to-graph.

## Workflow correction for code-level complaints

When the user says a feature is not implemented in the code, inspect definitions, call sites, compiler/parser paths, and runtime tests first. Do not substitute repeated screenshots or visual commentary for source inspection. State plainly when the current UI is only a mock/template, then implement and execute one truthful vertical slice before claiming coverage.