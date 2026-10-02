# Diagram Adaptation Across Projects

Use this procedure when a user supplies a diagram from one project as a structural reference for a different project.

## Contract split

Before editing, separate three things explicitly:

1. **Source topology** — nodes, decisions, loops, checkpoints, and visual hierarchy worth reusing.
2. **Source-domain semantics** — product names, integrations, data models, metrics, and operational assumptions that must not leak into the target automatically.
3. **Target contract** — the new project, retained terms, requested format, and capabilities the user actually named.

A diagram can supply topology without transferring its domain. If the user says to keep one term such as `incident`, preserve that term only; do not infer that DataHub, schema drift, graph repair, or other neighboring concepts also carry over.

If the target is defined by a linked hackathon, product page, specification, or repository, inspect that authoritative target source **before** choosing the target use case or rewriting labels. A directory name such as `call-data` is not evidence that the project concerns data pipelines, and a source diagram's domain is not evidence about the challenge's required domain.

## Adaptation workflow

1. Inspect the authoritative target source when one exists (challenge page, product docs, repository, or specification).
2. Inventory the source diagram node-by-node, including edge labels and loops.
3. Restate the target in one sentence before editing.
4. List the source-domain terms to remove and the terms the user explicitly wants retained.
5. Translate each node into the target domain while preserving only the requested topology.
6. Use the requested source format. If the user asks for Mermaid, make `.mmd` the canonical source; do not substitute a custom HTML/SVG artifact.
7. Generate SVG/PNG from the canonical Mermaid when visual assets are useful.
8. Keep README Mermaid synchronized with the canonical source programmatically.
9. Search the entire changed scope for stale source-domain terminology.
10. Inspect the rendered image for tiny labels, clipped nodes, crossing arrows, and loops whose direction is unclear.
11. Report the exact files changed and whether generated alternatives such as HTML were removed.

## Minimality rule

When the user says “without extrapolating,” model only the operations they named. For example, a diagram workspace requested to list, open, group, and remain open should not silently gain edit, generate, execute, merge, delete, or autonomous reasoning capabilities.

When the user says “just make the Mermaid,” “bref,” or otherwise stops the design discussion, stop adding conceptual layers. Produce or replace the canonical `.mmd` immediately, render it, and report the artifact paths. Keep progress narration to one short sentence per actual action; do not make the user repeatedly ask what is happening.

If MCP is mentioned only as a possible later interface, show it as optional/future (for example, a dashed edge) and expose only the already-defined operations. Do not turn a conceptual diagram into an implemented MCP server without a separate request.

## Disambiguate visual grouping from executable orchestration

The phrase “group these diagrams” can describe two different architectures. Do not default to a registry workspace when the user means an executable diagram.

### Presentation-only grouping

Use this only when the user asks to list/open/show diagrams together:

```text
Diagram sources -> registry -> diagram controller -> persistent workspace
                                      |
                                      +-> single view
                                      +-> grouped view (no forced merge)
```

This is a UI projection. It references independent diagrams and does not grant execution or autonomy.

### Executable composition

If the user says the bot is itself a diagram, stays autonomous, acts as a parent, or launches siblings in parallel, switch to the executable-diagram contract in `composable-autonomous-diagram-orchestration.md`:

```text
peer DiagramDefinitions in registry
-> autonomous Diagram Bot Run
-> independent child DiagramRuns
```

Here, parenthood exists only between runs. Do not retain workspace, registry-browser, or MCP-wrapper semantics from the presentation model unless the user separately requests them.

Future definitions may join either model without mutating existing diagram semantics.

## Verification checklist

- [ ] Target project and source project are named separately.
- [ ] Explicitly retained terms remain.
- [ ] Source-only domain terms are absent from target artifacts.
- [ ] Requested format is canonical.
- [ ] README and canonical source agree.
- [ ] Rendered SVG/PNG parse and pass visual inspection.
- [ ] No unrequested capabilities appear.
- [ ] Stale alternate artifacts are removed when the user asks.
