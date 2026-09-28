"""Build #2 — the minimal harness hardened.

Companion to Harness Engineering, Post 25. Adds hooks, a sandbox, a sub-agent,
an approval gate, and tracing to Build #1, each a small bounded addition.
"""
from .approval import ApprovalGate, always_approve, always_deny
from .harness import Result, StopReason, run
from .hooks import ALLOW, Decision, HookRegistry, deny_list
from .models import (Model, ModelResponse, ScriptedModel, ToolUse,
                     text_response, tool_response)
from .observe import Span, Tracer
from .sandbox import Sandbox, subprocess_runner
from .subagent import make_delegate_tool
from .tools import (Tool, ToolRegistry, Workspace, make_write_file_tool,
                    validate)

__all__ = [
    "run", "Result", "StopReason",
    "Model", "ModelResponse", "ToolUse", "ScriptedModel",
    "text_response", "tool_response",
    "Tool", "ToolRegistry", "Workspace", "make_write_file_tool", "validate",
    "HookRegistry", "Decision", "ALLOW", "deny_list",
    "Sandbox", "subprocess_runner",
    "ApprovalGate", "always_approve", "always_deny",
    "make_delegate_tool",
    "Tracer", "Span",
]
