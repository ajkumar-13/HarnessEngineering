"""Build #1 — a minimal agent harness from scratch.

Companion to Harness Engineering, Post 24. Loop + tools + a verification gate +
layered stop conditions, assembled from the Part I to III primitives.
"""
from .harness import Result, StopReason, run
from .models import (AnthropicModel, Model, ModelResponse, ScriptedModel,
                     ToolUse, text_response, tool_response)
from .tools import (DENY, Tool, ToolRegistry, Workspace, make_bash_tool,
                    make_write_file_tool, subprocess_runner, validate)
from .verify import Candidate, VerifyResult, Verifier, python_function_tests

__all__ = [
    "run", "Result", "StopReason",
    "Model", "ModelResponse", "ToolUse", "ScriptedModel", "AnthropicModel",
    "text_response", "tool_response",
    "Tool", "ToolRegistry", "Workspace", "validate", "DENY",
    "make_bash_tool", "make_write_file_tool", "subprocess_runner",
    "Candidate", "VerifyResult", "Verifier", "python_function_tests",
]
