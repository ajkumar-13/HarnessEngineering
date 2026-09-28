"""Tool + ToolRegistry: validate the model's tool call, then dispatch it.

`dispatch` is the whole discipline of Post 06 §4 in one method: validate the
input against the schema, execute only if it passes, and never let a tool crash
the loop — every outcome is returned as an observation string.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .schema import validate


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

    def add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def names(self) -> list[str]:
        return list(self._tools)

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
