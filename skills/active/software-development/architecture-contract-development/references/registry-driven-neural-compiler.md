# Registry-Driven Neural Visual Compiler

Use this reference when a visual neural IDE must maintain a real bidirectional contract between semantic blocks, typed cables, and executable framework code.

## Product boundary

- The typed registry and graph IR are canonical. The renderer and generated code are projections.
- Historical research candidates and failed ablations do not become privileged compiler branches merely because they supplied the first demo canvas.
- Keep the default graph neutral and composed from basic semantic operations. A research architecture belongs as a preset/composite only when the user explicitly retains it.
- Apply an evidence gate to research-specific blocks: "promising" or "worth retrying" is not equivalent to beating the named baseline. Remove explicitly rejected or repeatedly non-probant candidates from active product code, tests, exports, and compiler branches.

## Semantic atom contract

A public executable atom needs a structured lowering, not a free-form display string:

- stable `atomId`;
- typed input and output ports;
- materialized editable settings;
- concrete module declarations;
- concrete forward statements;
- optional private helper definitions;
- a real framework-runtime smoke test.

Undefined helper calls, unmaterialized names such as `hiddenSize`, and pseudocode expressions must be treated as incomplete. Composite recipes must expand into atoms before compilation or report an explicit non-executable diagnostic.

## Port identity versus tensor type

Never conflate these values:

- **port ID** identifies one physical/semantic socket, such as `routed`, `shared`, `expertIndices`, or `expertWeights`;
- **tensor type** validates compatibility, such as `hidden`, `expert-indices`, or `routing-weights`.

Cable endpoints must carry both. Replacement cardinality is keyed by target port ID, while compatibility is checked by tensor type. This permits two different `hidden` inputs such as `routed` and `shared` to remain independently connected.

Persist port IDs on graph edges and expose them separately in DOM metadata. Resolve cable color/type from the registry definition, not by casting a port ID into a tensor type.

## Forward compilation

1. Validate node/edge existence and reject cycles.
2. Topologically order the graph from edges, never X/Y or renderer order.
3. Materialize definition defaults, graph context, then instance settings.
4. Emit stable node markers such as `# labo:node=<id> atom=<atomId>`.
5. Emit stable edge markers containing node endpoints and source/target port IDs.
6. Generate declarations and forward statements from the structured lowering.
7. Return semantic sink outputs.
8. Emit an explicit invalid program/diagnostic for disconnected required ports; never crash the editor or silently skip the atom.

X/Y-only movement must leave generated code byte-identical.

## Reverse parsing

For the managed dialect:

- changing a recognized declaration updates the same atom settings;
- adding a recognized `atom=<atomId>` marker plus valid declaration creates a semantic node;
- deleting a managed node marker removes the node and incident edges;
- changing/deleting an edge marker rewires/disconnects the cable;
- unknown atom IDs, mismatched templates, unknown endpoints, and arbitrary code produce explicit diagnostics or a custom block policy.

A practical generic inverse parser can turn declaration templates into anchored regular expressions: literal segments are escaped, registry-setting placeholders become typed captures, graph-context placeholders are matched but not written into instance settings, and Python booleans/numbers/quoted strings are decoded.

## Capability status

Derive status from the active graph and emitted program:

- executable only when every active semantic atom is supported and all required ports resolve;
- incomplete for disconnected or unsupported atoms;
- never globally green merely because one preset has a runtime test.

## Verification slices

Require at least:

1. a small neutral chain such as Input → RMSNorm → ReLU;
2. a branching multi-port graph proving distinct same-type inputs do not replace one another;
3. a real runtime graph covering Token Embedding → Router/Top-K → Routed + Shared Experts → Merge → LM Head;
4. reverse tests for setting update, node add/remove, and cable rewire/delete;
5. full UI tests for semantic DOM ports, code regeneration, deletion invalidation, and honest capability status;
6. final unit suite, renderer build, and desktop/Electron build before claiming completion.
