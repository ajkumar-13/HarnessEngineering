"""The model layer, reused from Build #1 so Build #2 stands on the same loop.

``ScriptedModel`` keeps the whole suite and demo offline. See the Post 03 and
Post 24 companions for the full commentary; this is the same shape.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence, runtime_checkable


@dataclass
class ToolUse:
    id: str
    name: str
    input: dict


@dataclass
class ModelResponse:
    content_blocks: list[dict]
    tool_uses: list[ToolUse] = field(default_factory=list)
    text: str = ""
    tokens: int = 0

    def is_final(self) -> bool:
        return not self.tool_uses


@runtime_checkable
class Model(Protocol):
    def respond(self, system: str | None, messages: list[dict],
                tools: Sequence) -> ModelResponse: ...


def text_response(text: str, *, tokens: int = 1) -> ModelResponse:
    return ModelResponse([{"type": "text", "text": text}], [], text, tokens)


def tool_response(name: str, tool_input: dict, *, id: str = "tu_1",
                  text: str = "", tokens: int = 1) -> ModelResponse:
    blocks: list[dict] = []
    if text:
        blocks.append({"type": "text", "text": text})
    blocks.append({"type": "tool_use", "id": id, "name": name, "input": tool_input})
    return ModelResponse(blocks, [ToolUse(id, name, tool_input)], text, tokens)


@dataclass
class ScriptedModel:
    script: list[ModelResponse]
    _i: int = 0

    def respond(self, system, messages, tools) -> ModelResponse:
        if self._i >= len(self.script):
            return text_response("(script exhausted)", tokens=1)
        resp = self.script[self._i]
        self._i += 1
        return resp
