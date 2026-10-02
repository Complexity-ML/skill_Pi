# Composable autonomous diagram orchestration

Use this reference when a diagram is itself an executable orchestrator that may invoke other executable diagrams.

## Two levels that must never be collapsed

### Definition/catalog level

Every executable diagram is a peer definition:

```text
Diagram Registry
├── Autonomous Diagram Bot
├── Utility Diagram A
├── Utility Diagram B
└── Future Utility Diagram N
```

`Diagram Bot` is not a globally superior type. It is a `DiagramDefinition` like the utilities. A utility may be launched directly, invoked by an orchestrator, or itself compose other diagrams if its definition contains invocation nodes.

### Runtime level

A launched orchestrator run may parent the runs it creates:

```text
Autonomous Diagram Bot Run
└── parallel fork
    ├── Child Run A  -> Utility Diagram A definition
    ├── Child Run B  -> Utility Diagram B definition
    └── Child Run N  -> Future Utility Diagram definition
```

The parent/child relationship belongs to `DiagramRun`, not to the permanent definition hierarchy.

## Minimal contracts

```text
DiagramDefinition
  id
  version
  inputs
  outputs
  nodes
  edges
  capabilities

DiagramRun
  runId
  diagramId
  parentRunId?
  status
  inputs
  outputs
  childRunIds[]
```

A composition node should reference a definition (`InvokeDiagram(diagramId, version)`), never copy or move the child definition under the parent.

## What “autonomous Diagram Bot” means

Make the lifecycle explicit instead of treating `autonomous` as magic:

```text
launch directly
-> remain active (if persistent mode was requested)
-> receive an execution request/event
-> resolve only configured sibling diagram references
-> fork independent child runs
-> observe their states
-> return to active state or finish, according to the declared lifecycle
```

Do not assume persistent operation when the user may mean one-shot orchestration. If the conversation does not settle it, ask whether the bot stays active or exits after one composed run. Once the user says it “stays open/active,” represent the loop explicitly.

## Deterministic orchestrator vs parent agent

Do not call every persistent fork loop an agent “like Hermes.” There are two distinct contracts:

```text
Deterministic orchestrator
request -> resolve configured diagrams -> fork -> observe -> declared finish/loop
```

```text
Parent agent
objective
-> own parent context and state
-> select sibling diagram definitions
-> fork independent child runs
-> observe child results
-> parent decision
   -> continue/relaunch selected runs
   -> return result
-> wait for the next objective when persistent
```

Use the stronger parent-agent form only when the user explicitly asks for an autonomous agent, a “mini-Hermes,” or objective-driven decisions. The child diagrams do not automatically become full Hermes agents; they remain independent `DiagramRun` instances unless separately specified. MCP is still only an optional external adapter and is not what creates autonomy.

## Full sibling workflows vs internal utility subgraphs

The word “utility diagram” is ambiguous. If the user asks for “other diagrams like DATA LAB and CALL-DATA,” they are asking for complete, end-to-end domain workflows at the same catalog level—not low-level retry, audit, evidence, or approval primitives.

For an idea catalog:

- preserve existing projects as separate sibling definitions rather than copying their code;
- propose complete domain workflows with a trigger, incident/case, risk or policy decision, bounded action, verification, and terminal outcome;
- label concept candidates as unimplemented;
- prefer a few contrasting workflows to validate orchestration (for example phone side effect, deterministic technical action, and evidence/human-review flow) rather than claiming a broad platform from many sketches;
- keep cross-cutting retry/review/audit mechanisms inside a domain diagram unless the user explicitly promotes them to standalone executable diagrams.

## Parallel execution contract

Each child run needs its own:

- `runId`, `diagramId`, status and state;
- inputs copied or mapped from the parent;
- timeout/cancellation boundary;
- output/error record;
- human-review state when its own workflow requires it.

Only add a join policy when requested or required by the result contract. Valid policies include `all`, `allSettled`, `firstSuccess`, `race`, and `quorum`; do not silently choose one. A branch-local pause must not freeze unrelated branches unless the parent explicitly declares that behavior.

## Keep adapters outside the diagram semantics

Do not turn the concept into a UI shell, registry browser, or MCP wrapper unless requested.

```text
Optional future MCP server -> diagram runtime -> diagram registry
```

MCP may expose discovery/run/status/cancel operations later, but it does not define the business graph or make Diagram Bot autonomous. Likewise, a persistent diagram workspace is a UI projection, not the autonomous diagram itself.

## Visual contract for the architecture diagram

When the user wants both peer definitions and parent execution, show two labeled regions:

1. **Definitions — same level:** registry pointing to Diagram Bot and utility diagrams as siblings.
2. **Runs — contextual hierarchy:** Diagram Bot Run pointing through fork/parallel to independent child runs, with dashed links from utility definitions to their runs.

If autonomy is requested, add the bot run’s own active/request/fork/observe loop. Avoid presenting only `Parent Diagram -> children`, because that incorrectly implies a permanent type hierarchy. Avoid presenting only registry/workspace/MCP, because that omits runtime orchestration.

## Correction protocol

When the user corrects the model repeatedly:

1. Stop extending the previous interpretation.
2. Restate the corrected ontology in one sentence.
3. Replace the incorrect artifact instead of accumulating alternate diagrams.
4. Render and visually inspect the actual Mermaid/SVG/PNG.
5. Search the source for rejected concepts such as `Workspace`, `MCP`, or permanent `Parent Diagram` when those no longer apply.
6. Report exactly which semantic distinction is now visible.

## Verification checklist

- [ ] Diagram Bot is visibly a peer `DiagramDefinition`.
- [ ] Parent/child exists only between runtime runs.
- [ ] Child runs reference, rather than own/copy, utility definitions.
- [ ] Direct utility execution remains possible.
- [ ] Autonomous lifecycle is explicit and matches persistent vs one-shot intent.
- [ ] Parallel branches have independent run state.
- [ ] Join/failure policy is not invented.
- [ ] UI and MCP adapters are absent or visibly optional.
- [ ] Rendered output is inspected for clipping, crossing labels, and semantic ambiguity.
