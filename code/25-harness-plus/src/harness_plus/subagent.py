"""One sub-agent, exposed to the parent as a tool (Post 16).

Orchestration is over-used, and the right default is a single agent. But one
bounded sub-agent earns its place: it runs a delegated sub-task in its own fresh
context and returns only the answer, so the parent's window is not polluted by
the sub-task's chatter. That context isolation is the whole point.

``make_delegate_tool`` wraps any ``spawn(subtask) -> str`` callable as a
``delegate`` tool. In the demo and tests, ``spawn`` runs a child harness loop.
"""
from __future__ import annotations

from typing import Callable

from .tools import Tool

Spawn = Callable[[str], str]


def make_delegate_tool(spawn: Spawn) -> Tool:
    def run(args: dict) -> str:
        subtask = str(args["subtask"])
        answer = spawn(subtask)
        return f"sub-agent result: {answer}"

    return Tool(
        "delegate",
        "Delegate a self-contained sub-task to a sub-agent that runs in its own "
        "context and returns only its final answer.",
        {"type": "object", "properties": {"subtask": {"type": "string"}},
         "required": ["subtask"], "additionalProperties": False},
        run,
    )
