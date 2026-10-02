# Zero-Training Zipf TR Controller MVP

Session-derived reference for building a minimal tool-use controller aligned with Complexity's Zipf Token-Routed framing.

## Product distinction

- This is runtime/orchestration, not training.
- It can run with any callable model now, and later with a Token-Routed policy model.
- It should not be branded as full MCP until it has actual MCP transport/client integration.
- It should not be branded as a neural TR layer; it exposes a Zipf/TR-structured tool space to the policy.

## MVP files from the session

Example target layout used:

```text
complexity/tools/__init__.py
complexity/tools/controller.py
tests/test_tool_controller.py
```

Avoid placing the runtime under `complexity/training/`.

## Required behavior tests

A compact test suite should cover:

1. `ToolController` executes a tool call and then returns a final answer.
2. Model actions can be dicts or JSON strings.
3. Tool exceptions become `ToolResult(ok=False, error=...)` observations, allowing a second repair call.
4. Required JSON-schema-like fields are validated before handler execution.
5. `max_steps` raises instead of looping forever.
6. `complexity.tools` exports public types.
7. Tool schemas given to the model include Zipf/TR metadata:

```json
{
  "routing": {
    "strategy": "zipf_token_routed",
    "expert_id": 0,
    "num_experts": 8
  }
}
```

8. `ZipfToolRouter` balances high-frequency tools across experts.

## Implementation sketch

Core data classes:

```python
@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: Any = None
    error: str | None = None

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: Mapping[str, Any]
    handler: Callable[[Mapping[str, Any]], Any]
```

Controller action shapes:

```json
{"tool": "name", "arguments": {...}}
{"final": "answer"}
```

Zipf routing:

```python
ordered = sorted(tool_names, key=lambda name: (-frequency(name), name))
for name in ordered:
    expert = least_loaded_expert()
    assignments[name] = expert
    loads[expert] += frequency(name)
```

Default frequency when no usage stats exist: stable Zipf prior by lexical rank (`1 / rank`).

## Verification commands

Use the repo's Python that has project dependencies available. In the session this was `python3.13`:

```bash
python3.13 -m pytest tests/test_tool_controller.py tests/test_imports.py -q
python3.13 -m py_compile complexity/tools/__init__.py complexity/tools/controller.py tests/test_tool_controller.py
git diff --check -- complexity/tools/__init__.py complexity/tools/controller.py tests/test_tool_controller.py
```

## Reporting checklist

When done, report:

- exact new/modified files,
- test counts and commands,
- that unrelated dirty files were not touched,
- whether the result is real MCP or only MCP-style/adapter-ready,
- whether it is neural TR or a Zipf/TR tool-space for a future TR policy.
