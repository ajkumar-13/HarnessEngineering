"""The agent loop: reason -> act -> observe, with four layered stop conditions.

This is the whole engine from Post 03. The loop body is small; the four exits
are the point. Read `run` top to bottom.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from .models import Model, ToolUse
from .tools import Tool


class StopReason(str, Enum):
    COMPLETED = "completed"      # (1) the model returned a final answer
    MAX_ITERS = "max_iters"      # (2) hit the hard iteration cap
    BUDGET = "budget"            # (3) ran out of token budget
    NO_PROGRESS = "no_progress"  # (4) the same action repeated with no change


@dataclass
class Result:
    answer: str | None
    stop_reason: StopReason
    iterations: int
    tokens_used: int
    transcript: list[dict] = field(default_factory=list)


def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps(
        [[tu.name, tu.input] for tu in tool_uses], sort_keys=True)


def run(model: Model, tools: Sequence[Tool], task: str, *,
        system: str | None = None, max_iters: int = 12,
        token_budget: int | None = None, no_progress_window: int = 3) -> Result:
    tool_map = {t.name: t for t in tools}
    messages: list[dict] = [{"role": "user", "content": task}]
    tokens_used = 0
    recent: list[str] = []

    for step in range(1, max_iters + 1):
        # --- REASON ---------------------------------------------------------
        resp = model.respond(system, messages, tools)
        tokens_used += resp.tokens
        messages.append({"role": "assistant", "content": resp.content_blocks})

        # --- stop (1): a final answer is the exit we want -------------------
        if resp.is_final():
            return Result(resp.text, StopReason.COMPLETED, step, tokens_used, messages)

        # --- stop (3): a real cost ceiling, checked before we spend more ----
        if token_budget is not None and tokens_used >= token_budget:
            return Result(None, StopReason.BUDGET, step, tokens_used, messages)

        # --- stop (4): thrashing — same action, no change, N turns running --
        recent.append(_signature(resp.tool_uses))
        window = recent[-no_progress_window:]
        if len(window) == no_progress_window and len(set(window)) == 1:
            return Result(None, StopReason.NO_PROGRESS, step, tokens_used, messages)

        # --- ACT + OBSERVE --------------------------------------------------
        results = []
        for tu in resp.tool_uses:
            tool = tool_map.get(tu.name)
            output = tool.run(tu.input) if tool else f"error: unknown tool '{tu.name}'"
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": output})
        messages.append({"role": "user", "content": results})

    # --- stop (2): the backstop — a loop must always be able to terminate ---
    return Result(None, StopReason.MAX_ITERS, max_iters, tokens_used, messages)
