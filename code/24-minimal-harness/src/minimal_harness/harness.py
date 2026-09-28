"""Build #1: a minimal agent harness in one file.

Four things from Parts I to IV, wired together:

  * the loop           reason -> act -> observe            (Post 03)
  * tools              a schema-validated registry         (Post 06)
  * a verification gate "done" means "verified"            (Post 11)
  * layered exits      completed / max-iters / budget /
                       no-progress                          (Posts 03, 19)

Read ``run`` top to bottom. The body is small; the exits and the gate are the
point. Everything is offline: drive it with a ``ScriptedModel`` and an injected
tool runner, and no network or API key is touched.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .models import Model, ToolUse
from .tools import ToolRegistry, Workspace
from .verify import Candidate, VerifyResult, Verifier


class StopReason(str, Enum):
    COMPLETED = "completed"      # (1) a final answer that PASSED the gate
    MAX_ITERS = "max_iters"      # (2) hit the hard iteration cap
    BUDGET = "budget"            # (3) ran out of token budget
    NO_PROGRESS = "no_progress"  # (4) the same action repeated with no change


@dataclass
class Result:
    answer: Optional[str]
    stop_reason: StopReason
    verified: bool
    iterations: int
    tokens_used: int
    report: str = ""
    transcript: list[dict] = field(default_factory=list)


def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)


def run(model: Model, registry: ToolRegistry, task: str, *,
        system: Optional[str] = None, verify: Optional[Verifier] = None,
        workspace: Optional[Workspace] = None, max_iters: int = 12,
        token_budget: Optional[int] = None, no_progress_window: int = 3) -> Result:
    workspace = workspace if workspace is not None else Workspace()
    messages: list[dict] = [{"role": "user", "content": task}]
    tokens_used = 0
    recent: list[str] = []

    for step in range(1, max_iters + 1):
        # --- REASON ---------------------------------------------------------
        resp = model.respond(system, messages, registry.specs())
        tokens_used += resp.tokens
        messages.append({"role": "assistant", "content": resp.content_blocks})

        # --- the model proposes a final answer: the GATE decides ------------
        if resp.is_final():
            candidate = Candidate(resp.text, workspace)
            verdict = verify(candidate) if verify else VerifyResult(True)
            if verdict.ok:
                # stop (1): the only exit that returns verified work
                return Result(resp.text, StopReason.COMPLETED, True, step,
                              tokens_used, "", messages)
            # gate failed: feed the report back as the next observation and
            # keep going (Post 11). The failure is verbose; success is silent.
            messages.append({"role": "user",
                             "content": f"verification failed: {verdict.report}"})
            recent.clear()  # a real correction is progress; reset the detector
            # the budget governs this path too: a gate rejection is a spent
            # model call, and skipping the check here made BUDGET unreachable
            # whenever the gate kept rejecting.
            if token_budget is not None and tokens_used >= token_budget:
                return Result(None, StopReason.BUDGET, False, step, tokens_used,
                              "token budget exhausted", messages)
            continue

        # --- stop (3): a real cost ceiling, checked before spending more ----
        if token_budget is not None and tokens_used >= token_budget:
            return Result(None, StopReason.BUDGET, False, step, tokens_used,
                          "token budget exhausted", messages)

        # --- stop (4): thrashing — same tool calls, no change, N turns ------
        recent.append(_signature(resp.tool_uses))
        window = recent[-no_progress_window:]
        if len(window) == no_progress_window and len(set(window)) == 1:
            return Result(None, StopReason.NO_PROGRESS, False, step, tokens_used,
                          "no progress: identical tool calls repeating", messages)

        # --- ACT + OBSERVE --------------------------------------------------
        results = []
        for tu in resp.tool_uses:
            observation = registry.dispatch(tu.name, tu.input)
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": observation})
        messages.append({"role": "user", "content": results})

    # --- stop (2): the backstop — a loop must always be able to terminate ---
    return Result(None, StopReason.MAX_ITERS, False, max_iters, tokens_used,
                  "hit max iterations without passing the gate", messages)
