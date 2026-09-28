"""Tool schemas, validation, and a deny-listed bash tool.

Companion to Harness Engineering, Post 06 — "Tools as the agent's hands".
"""
from .bash_tool import (BASH_DESCRIPTION, BASH_SCHEMA, DENY, make_bash_tool,
                        subprocess_runner)
from .registry import Tool, ToolRegistry
from .schema import validate

__all__ = [
    "validate", "Tool", "ToolRegistry",
    "make_bash_tool", "subprocess_runner", "DENY", "BASH_SCHEMA", "BASH_DESCRIPTION",
]
