"""Tools and a schema-validated registry (from the Post 06 / Post 24 companions).

Build #2 keeps the registry but no longer trusts a bare deny-list for
execution: the bash tool here runs inside a :mod:`sandbox` (Post 14, allow-list
+ jail + timeout). The registry still validates every call against its schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

_TYPES = {"object": dict, "array": list, "string": str,
          "number": (int, float), "integer": int, "boolean": bool,
          "null": type(None)}


def _type_ok(value, expected: str) -> bool:
    if expected == "boolean":
        return isinstance(value, bool)
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    py = _TYPES.get(expected)
    return isinstance(value, py) if py is not None else True


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected and not _type_ok(instance, expected):
        return [f"{path}: expected {expected}"]
    if expected == "object" and isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, value in instance.items():
            if key in props:
                errors += validate(value, props[key], f"{path}.{key}")
    return errors


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    run: Callable[[dict], str]
    sensitive: bool = False  # if True, a call needs approval (Post 15)


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool] = ()):
        self._tools: dict[str, Tool] = {}
        for tool in tools:
            self.add(tool)

    def add(self, tool: Tool) -> "ToolRegistry":
        self._tools[tool.name] = tool
        return self

    def get(self, name: str) -> "Tool | None":
        return self._tools.get(name)

    def specs(self) -> list[dict]:
        return [{"name": t.name, "description": t.description,
                 "input_schema": t.input_schema} for t in self._tools.values()]

    def dispatch(self, name: str, tool_input: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"error: unknown tool '{name}'"
        problems = validate(tool_input, tool.input_schema)
        if problems:
            return "error: invalid input: " + "; ".join(problems)
        try:
            return tool.run(tool_input)
        except Exception as e:
            return f"error: {type(e).__name__}: {e}"


@dataclass
class Workspace:
    files: dict[str, str] = field(default_factory=dict)


def make_write_file_tool(workspace: Workspace, *, sensitive: bool = False) -> Tool:
    def run(args: dict) -> str:
        path, content = str(args["path"]), str(args["content"])
        workspace.files[path] = content
        return f"wrote {len(content)} bytes to {path}"

    return Tool(
        "write_file",
        "Write text content to a file in the workspace.",
        {"type": "object",
         "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
         "required": ["path", "content"], "additionalProperties": False},
        run, sensitive=sensitive,
    )
