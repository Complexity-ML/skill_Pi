# Complexity Zipf/TR Tool Controller Pattern

Session-derived pattern for tool-controller work in Complexity-style repos.

## User correction captured

The user rejected a generic tool runtime that could be driven by arbitrary models. The intended architecture is a Complexity-specific tool controller tied to Zipf Token-Routed policies.

## Correct public shape

Prefer names like:

- `TokenRoutedToolController`
- `TokenRoutedToolPolicy`
- `ZipfToolRouter`
- `MCPToolProvider` only as a provider feeding the TR controller

Avoid public names like:

- `ToolController(model=any_callable, ...)`
- generic `ModelCallable` APIs
- docs saying "model-agnostic" or "any callable"

## Tests that encode the contract

Useful test cases:

- generic callable policy is rejected
- policy must inherit/implement `TokenRoutedToolPolicy`
- policy `route_family` must be `zipf_token_routed`
- public namespace does not export the generic controller symbol
- model-facing tools include routing metadata:
  - `strategy: zipf_token_routed`
  - `expert_id`
  - `num_experts`
- traces preserve `route_family` and `routed_tools`

## Design note

The runtime can still adapt external tools (e.g. MCP `list_tools`/`call_tool`), but those adapters should not make the controller generic. The adapter supplies tools; the Complexity Token-Routed policy remains the only supported controller driver.
