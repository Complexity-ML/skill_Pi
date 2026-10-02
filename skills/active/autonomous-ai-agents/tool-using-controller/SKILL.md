---
name: tool-using-controller
description: Build tool-use integrations around official MCP servers/SDK for Complexity lexical/Token-Routed models; avoid custom generic controller runtimes.
metadata:
  hermes:
    tags:
    - agents
    - tools
    - mcp
    - controller
    - token-routed
    - zipf
    - testing
    related_skills:
    - test-driven-development
    - systematic-debugging
    - hermes-agent
  hermes_frontmatter:
    version: 1.0.0
    author: Hermes Agent
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

# Tool-Using Controller

Use this skill when connecting Complexity lexical / Token-Routed models to external tools via MCP. The target is not a generic agent framework: prefer official MCP SDK/server integration and keep Complexity-specific logic focused on lexical/TR policy, routing metadata, traces, and evals.

## Core framing

- A tool-use runtime is not training. Keep it outside `training/` unless it is actually producing or consuming training jobs.
- Do **not** build a custom generic controller just because a model needs tools. First ask whether existing MCP servers/SDK already provide the needed filesystem/browser/GitHub/design/etc. tools.
- The user's preferred direction for Complexity is: **lexical / Token-Routed model enters the MCP ecosystem**, not “reinvent GitHub/Figma/browser” and not “generic wrapper usable by any model.”
- A zero-training MVP is valid, but it should normally be: official MCP SDK client + optional Complexity policy adapter + traces/evals. Do not start by inventing a handler registry unless explicitly requested.
- For Complexity-style work, public framing may include Zipf/Token-Routed metadata, but avoid overclaiming: the model/policy is Token-Routed; MCP executes actions.

## Preferred architecture

```text
Complexity lexical / Token-Routed policy
  -> official MCP SDK client/session
  -> existing MCP server(s)
  -> tool observations
  -> policy continues or finalizes
```

Core objects should be thin wrappers around official MCP concepts, not replacements:

- MCP stdio/http config for launching or connecting to servers.
- Lazy SDK import so the core framework still imports without the optional `mcp` package.
- Normalized `MCPTool` metadata (`name`, `description`, `input_schema`, raw object).
- Normalized `MCPToolResult` (`content`, `is_error`, raw object).
- Optional Complexity policy/action codec layer that decides which MCP tool to call.
- Optional trace/eval layer that records calls/results for later training, without making training mandatory.

Only add an internal handler-based registry if the user explicitly wants non-MCP local test tools or if it is confined to tests/fixtures.

## TDD workflow

1. Write tests for the external behavior before implementation:
   - the package imports lazily when the optional MCP SDK is not installed,
   - optional dependency extra (e.g. `tools = ["mcp>=..."]`) is declared,
   - a fake official SDK can list tools and call a tool,
   - SDK results are normalized without losing the raw object,
   - unrelated dirty repo files are not touched.
2. Run the targeted test and confirm RED.
3. Implement the smallest official-SDK bridge to pass.
4. Keep the bridge thin: use SDK `ClientSession`, stdio/http transport helpers, and server-provided schemas. Do not reimplement filesystem/GitHub/browser/design tools.
5. Run targeted tests, import tests, `py_compile`, and `git diff --check`.

## Zipf/TR tool routing

A simple durable implementation:

- Accept optional `tool_frequencies: Mapping[str, float]` and `num_tool_experts`.
- Sort tools by descending frequency, then name for deterministic tie-breaking.
- Greedily assign each tool to the least-loaded expert.
- If no frequency exists, use a stable Zipf prior based on lexical rank (`1 / rank`).
- Add model-facing metadata:

```json
"routing": {
  "strategy": "zipf_token_routed",
  "expert_id": 0,
  "num_experts": 8
}
```

## MCP SDK integration direction

Prefer the official MCP SDK over custom JSON-RPC or handler registries.

Python stdio bridge shape:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_parameters = StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", workspace])
async with stdio_client(server_parameters) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("tool.name", arguments={...})
```

Implementation notes:

- Put the SDK dependency behind an optional extra (for example `[tools]`) and lazy import it inside the MCP bridge. The main package must import without `mcp` installed.
- Normalize MCP tool metadata into a small dataclass if helpful, but preserve the raw SDK object for future compatibility.
- Accept both `inputSchema` and `input_schema` when normalizing tool schemas.
- For tests, fake the official SDK modules via `sys.modules` rather than launching real MCP servers.
- Do not call a handler-based provider “MCP” unless it actually uses MCP SDK/protocol.

## Trace collection

Always keep traces lightweight but training-ready:

- task/user request,
- model-visible tools including route metadata,
- assistant tool call,
- tool result/observation,
- final answer,
- optional scores.

Do not require a dataset for the MVP; collect traces passively so later SFT/DPO can learn tool choice, JSON validity, repair behavior, and stopping criteria.

## Pitfalls

- Do not put tool-use runtime under training just because traces can later become data.
- Do not reinvent GitHub/Figma/browser/filesystem tools; connect to existing MCP servers via the official SDK unless the user explicitly asks for a custom local tool.
- Do not build a generic model-agnostic controller when the user wants Complexity lexical/TR to “enter MCP.” Keep generic examples in tests only.
- Do not overclaim MCP if only a handler-based tool registry exists. Call it handler-based or MCP-like until real MCP SDK/protocol is wired.
- Do not continue an obsolete implementation path after the user reframes it. If the user says “official MCP SDK,” delete or abandon custom controller scaffolding before proceeding.
- Do not claim the controller is Token-Routed if only tool metadata is routed; say the Complexity model/policy is Token-Routed and MCP executes actions.
- Preserve unrelated dirty files in the user repo and report only the files intentionally touched.
- Destructive cleanup of generated files may require explicit user approval; ask once, then perform exactly the approved deletion.

## References

- See `references/official-mcp-sdk-integration.md` for the preferred official-SDK bridge pattern, lazy import tests, real SDK verification via a local venv, and cleanup lesson.
- See `references/zero-training-zipf-tr-controller.md` for the earlier handler-based MVP shape; treat it as historical/background only, not the preferred MCP path.
