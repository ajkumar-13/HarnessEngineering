"""A couple of tiny tools for the loop.

The calculator uses a safe AST evaluator, not `eval`, on purpose: this series
is about harnesses, and a tool is an execution surface. Real sandboxing of
arbitrary tools is Post 14.
"""
from __future__ import annotations

import ast
import operator
from dataclasses import dataclass, field
from typing import Callable

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


@dataclass
class Tool:
    name: str
    description: str
    run: Callable[[dict], str]
    input_schema: dict = field(default_factory=lambda: {
        "type": "object", "properties": {}, "additionalProperties": True})


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def _calculator(args: dict) -> str:
    expr = str(args.get("expression", ""))
    try:
        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as e:  # a tool returns errors as observations, it never raises
        return f"error: {e}"


def _echo(args: dict) -> str:
    return str(args.get("text", ""))


calculator = Tool(
    "calculator", "Evaluate a basic arithmetic expression.", _calculator,
    {"type": "object",
     "properties": {"expression": {"type": "string"}},
     "required": ["expression"]},
)

echo = Tool(
    "echo", "Return the given text unchanged.", _echo,
    {"type": "object",
     "properties": {"text": {"type": "string"}},
     "required": ["text"]},
)

DEFAULT_TOOLS = [calculator, echo]
