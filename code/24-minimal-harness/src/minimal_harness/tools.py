"""Tools: a schema-validated registry, a deny-listed bash tool, and a file tool.

This folds the Post 06 companion (schema validation + a deny-listed bash tool)
into Build #1. ``dispatch`` is the whole discipline in one method: validate the
input against the schema, execute only if it passes, and never let a tool crash
the loop — every outcome is returned as an observation string.

The ``Workspace`` is an in-memory filesystem the agent writes to and the
verifier reads from (Post 24, section 4). Real on-disk work and real sandboxing
of arbitrary commands are Build #2 (Posts 14, 25); here the runner is injectable
so tests stay offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable

# ---- a tiny JSON-Schema-subset validator (from the Post 06 companion) --------

_TYPES = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool, "null": type(None),
}


def _type_ok(value, expected: str) -> bool:
    if expected == "boolean":
        return isinstance(value, bool)
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    py = _TYPES.get(expected)
    return isinstance(value, py) if py is not None else True


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Return a list of validation errors; an empty list means valid."""
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


# ---- the tool + registry -----------------------------------------------------

@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    run: Callable[[dict], str]


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool] = ()):
        self._tools: dict[str, Tool] = {}
        for tool in tools:
            self.add(tool)

    def add(self, tool: Tool) -> "ToolRegistry":
        self._tools[tool.name] = tool
        return self

    def specs(self) -> list[dict]:
        """Provider-facing tool specs — what you send to the model each call."""
        return [{"name": t.name, "description": t.description,
                 "input_schema": t.input_schema} for t in self._tools.values()]

    def dispatch(self, name: str, tool_input: dict) -> str:
        """Validate, then execute. Returns an observation string; never raises."""
        tool = self._tools.get(name)
        if tool is None:
            return f"error: unknown tool '{name}'"
        problems = validate(tool_input, tool.input_schema)
        if problems:
            return "error: invalid input: " + "; ".join(problems)
        try:
            return tool.run(tool_input)
        except Exception as e:  # a tool must not crash the loop
            return f"error: {type(e).__name__}: {e}"


# ---- an in-memory workspace and the tools that use it ------------------------

@dataclass
class Workspace:
    """The files the agent has written this run; the verifier reads these."""
    files: dict[str, str] = field(default_factory=dict)


DENY = [
    r"\brm\s+-[rf]", r"\bmkfs\b", r"\bdd\s+if=", r"\bshutdown\b", r"\breboot\b",
    r"\bgit\s+push\b[^\n]*--force", r"\bsudo\b", r"\bDROP\s+TABLE\b",
]

Runner = Callable[[str, float], "tuple[str, int]"]


def subprocess_runner(command: str, timeout: float) -> "tuple[str, int]":
    import subprocess
    proc = subprocess.run(command, shell=True, capture_output=True,
                          text=True, timeout=timeout)
    return ((proc.stdout or "") + (proc.stderr or "")).strip(), proc.returncode


def make_bash_tool(runner: Runner = subprocess_runner, *, timeout: float = 10.0,
                   deny: list[str] = DENY) -> Tool:
    patterns = [re.compile(p, re.IGNORECASE) for p in deny]

    def run(args: dict) -> str:
        command = str(args.get("command", ""))
        for pattern in patterns:
            if pattern.search(command):
                return f"blocked: command matches a deny-list rule ({pattern.pattern})"
        try:
            output, code = runner(command, timeout)
        except Exception as e:
            return f"error: {type(e).__name__}: {e}"
        prefix = "" if code == 0 else f"(exit {code}) "
        return prefix + (output if output else "(no output)")

    return Tool(
        "bash",
        "Run a shell command and return its combined output. Dangerous commands "
        "are refused.",
        {"type": "object", "properties": {"command": {"type": "string"}},
         "required": ["command"], "additionalProperties": False},
        run,
    )


def make_write_file_tool(workspace: Workspace) -> Tool:
    """A tool that writes a file into the in-memory workspace."""
    def run(args: dict) -> str:
        path, content = str(args["path"]), str(args["content"])
        workspace.files[path] = content
        return f"wrote {len(content)} bytes to {path}"

    return Tool(
        "write_file",
        "Write text content to a file in the workspace, replacing any existing "
        "file at that path.",
        {"type": "object",
         "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
         "required": ["path", "content"], "additionalProperties": False},
        run,
    )
