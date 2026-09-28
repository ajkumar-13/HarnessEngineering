"""Models the harness can drive.

The message format is Anthropic-native on purpose: the harness's ``messages``
list is exactly what you would send to the Messages API, so the real adapter is
a thin pass-through. ``ScriptedModel`` fakes responses so the whole test suite
and the demo run offline, with no API key. This is the same model layer as the
Post 03 companion, reused verbatim so Build #1 stands on the loop you already
have.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence, runtime_checkable


@dataclass
class ToolUse:
    """One tool call the model asked for."""
    id: str
    name: str
    input: dict


@dataclass
class ModelResponse:
    """One turn's output, normalised across providers.

    ``content_blocks`` is what to append to the transcript as the assistant
    message. ``tool_uses`` is the same calls parsed out. ``is_final()`` is true
    when the model asked for no tools; that is a *candidate* final answer, which
    the verification gate still has to approve (Post 24, section 4).
    """
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
    """A deterministic model for tests and demos: replays a fixed list of
    responses in order. Ignores ``messages`` — the point is reproducibility.
    Once the script is exhausted it returns a final answer so no loop hangs."""
    script: list[ModelResponse]
    _i: int = 0

    def respond(self, system, messages, tools) -> ModelResponse:
        if self._i >= len(self.script):
            return text_response("(script exhausted)", tokens=1)
        resp = self.script[self._i]
        self._i += 1
        return resp


@dataclass
class AnthropicModel:
    """Real adapter over the Anthropic Messages API.

    Requires ``pip install .[anthropic]`` and an ``ANTHROPIC_API_KEY``. Not
    covered by the offline test suite. The message format the harness maintains
    is already Anthropic-native, so this simply forwards it.
    """
    model: str = "claude-sonnet-5"
    max_tokens: int = 1024
    _client: object = None

    def respond(self, system, messages, tools) -> ModelResponse:
        if self._client is None:
            import anthropic  # optional dependency
            self._client = anthropic.Anthropic()
        api_tools = [{"name": s["name"], "description": s["description"],
                      "input_schema": s["input_schema"]} for s in tools]
        kwargs: dict = {"model": self.model, "max_tokens": self.max_tokens,
                        "messages": messages}
        if system:
            kwargs["system"] = system
        if api_tools:
            kwargs["tools"] = api_tools
        resp = self._client.messages.create(**kwargs)
        blocks = [b.model_dump() for b in resp.content]
        tool_uses = [ToolUse(b["id"], b["name"], b["input"])
                     for b in blocks if b.get("type") == "tool_use"]
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        usage = getattr(resp, "usage", None)
        tokens = (usage.input_tokens + usage.output_tokens) if usage else 0
        return ModelResponse(blocks, tool_uses, text, tokens)
