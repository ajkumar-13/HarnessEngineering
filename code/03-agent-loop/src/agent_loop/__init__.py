"""A minimal ReAct agent loop with layered stop conditions.

Companion to Harness Engineering, Post 03 — "The agent loop".
"""
from .loop import Result, StopReason, run
from .models import (AnthropicModel, Model, ModelResponse, ScriptedModel,
                     ToolUse, text_response, tool_response)
from .tools import DEFAULT_TOOLS, Tool, calculator, echo

__all__ = [
    "run", "Result", "StopReason",
    "Model", "ModelResponse", "ToolUse", "ScriptedModel", "AnthropicModel",
    "text_response", "tool_response",
    "Tool", "calculator", "echo", "DEFAULT_TOOLS",
]
