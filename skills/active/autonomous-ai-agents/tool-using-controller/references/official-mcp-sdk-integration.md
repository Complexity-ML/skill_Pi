# Official MCP SDK Integration Notes

Session lesson: when connecting Complexity lexical / Token-Routed models to tools, prefer the official MCP SDK and existing MCP servers over custom controller/tool registries. The user's intended framing is “Complexity enters MCP,” not “build a generic agent framework.”

## Preferred repo shape

```text
complexity/mcp/
  __init__.py
  client.py
```

Expose small wrappers only:

- `OfficialMCPStdioConfig(command, args=(), env=None, cwd=None)`
- `OfficialMCPStdioClient(config)`
- `MCPTool(name, description, input_schema, raw=None)`
- `MCPToolResult(content, is_error=False, raw=None)`

Keep the SDK dependency optional:

```toml
[project.optional-dependencies]
tools = [
    "mcp>=1.0.0; python_version >= '3.10'",
]
```

Import the SDK lazily inside the methods that need it so `import complexity.mcp` works even when `mcp` is not installed.

## Official stdio pattern

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", workspace])
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("tool.name", arguments={...})
```

Normalize tool schemas but preserve raw SDK objects:

- tool name: `tool.name`
- description: `tool.description` or empty string
- input schema: prefer `inputSchema`, fallback to `input_schema`, fallback to `{ "type": "object" }`
- result content: `result.content`
- error flag: `result.isError` if present

## Tests that caught the right behavior

Use both unit tests and a real SDK import check:

1. `import complexity.mcp` succeeds without the SDK installed.
2. `pyproject.toml` includes the optional `tools` extra with `mcp>=...`.
3. Unit tests fake the official SDK modules via `sys.modules`:
   - `mcp.ClientSession`
   - `mcp.StdioServerParameters`
   - `mcp.client.stdio.stdio_client`
4. Verify `OfficialMCPStdioClient.list_tools()` normalizes fake tools.
5. Verify `OfficialMCPStdioClient.call_tool()` delegates to the fake session and normalizes content/error.
6. Add a real SDK import test guarded by `pytest.importorskip("mcp")` so it runs when the official package is installed but skips in lean CI:

```python
def test_real_official_mcp_sdk_imports_when_installed():
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    assert ClientSession is not None
    assert StdioServerParameters is not None
    assert stdio_client is not None
```

## Installing/verifying the official SDK locally

On PEP 668-managed macOS/Homebrew Python, do not force a global install. Use a project-local venv for the SDK probe:

```bash
python3.13 -m venv .venv-mcp
.venv-mcp/bin/python -m pip install --upgrade pip
.venv-mcp/bin/python -m pip install mcp pytest
```

If that venv does not have the project’s heavy ML dependencies (for example Torch) but the system/project Python does, make the SDK package visible to the project Python only for the verification command:

```bash
MCP_SITE=$(.venv-mcp/bin/python - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)
PYTHONPATH="$MCP_SITE:$PYTHONPATH" python3.13 -m pytest tests/test_mcp_official.py -q
```

This verifies against the real official SDK without installing Torch into the MCP probe venv or breaking the managed Python. Report clearly which tests used the fake SDK unit path and which used the real SDK import path.

## Cleanup lesson

If a previous custom controller scaffold exists (`complexity/tools/`, handler-based `ToolController`, etc.) and the user chooses official MCP SDK, delete the scaffold after explicit approval before adding the MCP bridge. Do not leave both APIs around; it confuses the architecture and can accidentally make the package look like a generic agent framework.
