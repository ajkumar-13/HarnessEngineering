"""Build #2: the minimal harness, hardened.

The loop is the same reason -> act -> observe engine as Build #1. What is new is
what happens *around* each tool call, in order:

  1. a pre-tool HOOK can block it outright        (Post 13)
  2. a sensitive call pauses for human APPROVAL   (Post 15)
  3. the bash tool executes inside a SANDBOX      (Post 14)
  4. a `delegate` tool can spawn a SUB-AGENT       (Post 16)

and the whole run is wrapped in a TRACER that emits nested spans (Post 21). Each
addition is small and bounded; together they turn the minimal harness into one
you would let run unattended. Everything stays offline.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, Optional

from .approval import ApprovalGate
from .hooks import HookRegistry
from .models import Model, ToolUse
from .observe import Span, Tracer
from .tools import ToolRegistry


class StopReason(str, Enum):
    COMPLETED = "completed"
    MAX_ITERS = "max_iters"
    BUDGET = "budget"
    NO_PROGRESS = "no_progress"


@dataclass
class Result:
    answer: Optional[str]
    stop_reason: StopReason
    iterations: int
    tokens_used: int
    transcript: list[dict] = field(default_factory=list)
    trace: Optional[Span] = None
    blocked: list[tuple] = field(default_factory=list)   # (tool, reason)
    denied: list[tuple] = field(default_factory=list)    # (tool, reason)


class _NullSpan:
    def set(self, *_a, **_k):
        return self


@contextmanager
def _maybe_span(tracer: Optional[Tracer], name: str, **attrs) -> Iterator:
    if tracer is None:
        yield _NullSpan()
    else:
        with tracer.span(name, **attrs) as span:
            yield span


def _signature(tool_uses: list[ToolUse]) -> str:
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)


def run(model: Model, registry: ToolRegistry, task: str, *,
        system: Optional[str] = None, hooks: Optional[HookRegistry] = None,
        approval: Optional[ApprovalGate] = None, tracer: Optional[Tracer] = None,
        max_iters: int = 12, token_budget: Optional[int] = None,
        no_progress_window: int = 3, span_name: str = "agent.run") -> Result:
    messages: list[dict] = [{"role": "user", "content": task}]
    tokens_used = 0
    recent: list[str] = []
    blocked: list[tuple] = []
    denied: list[tuple] = []

    with _maybe_span(tracer, span_name, task=task) as run_span:
        for step in range(1, max_iters + 1):
            with _maybe_span(tracer, "iteration", index=step):
                # --- REASON -------------------------------------------------
                with _maybe_span(tracer, "model.call") as m:
                    resp = model.respond(system, messages, registry.specs())
                    m.set("tokens", resp.tokens)
                tokens_used += resp.tokens
                messages.append({"role": "assistant", "content": resp.content_blocks})

                if resp.is_final():
                    run_span.set("stop.reason", StopReason.COMPLETED.value)
                    return Result(resp.text, StopReason.COMPLETED, step,
                                  tokens_used, messages, tracer.root if tracer else None,
                                  blocked, denied)

                if token_budget is not None and tokens_used >= token_budget:
                    run_span.set("stop.reason", StopReason.BUDGET.value)
                    return Result(None, StopReason.BUDGET, step, tokens_used,
                                  messages, tracer.root if tracer else None,
                                  blocked, denied)

                recent.append(_signature(resp.tool_uses))
                window = recent[-no_progress_window:]
                if len(window) == no_progress_window and len(set(window)) == 1:
                    run_span.set("stop.reason", StopReason.NO_PROGRESS.value)
                    return Result(None, StopReason.NO_PROGRESS, step, tokens_used,
                                  messages, tracer.root if tracer else None,
                                  blocked, denied)

                # --- ACT + OBSERVE, gated per tool call ---------------------
                results = []
                for tu in resp.tool_uses:
                    observation = _gated_dispatch(
                        tu, registry, hooks, approval, tracer, blocked, denied)
                    results.append({"type": "tool_result",
                                    "tool_use_id": tu.id, "content": observation})
                messages.append({"role": "user", "content": results})

        run_span.set("stop.reason", StopReason.MAX_ITERS.value)
    return Result(None, StopReason.MAX_ITERS, max_iters, tokens_used, messages,
                  tracer.root if tracer else None, blocked, denied)


def _gated_dispatch(tu: ToolUse, registry: ToolRegistry,
                    hooks: Optional[HookRegistry], approval: Optional[ApprovalGate],
                    tracer: Optional[Tracer], blocked: list, denied: list) -> str:
    with _maybe_span(tracer, f"tool.{tu.name}", args=tu.input) as span:
        # (1) pre-tool hook — a deterministic block, checked before anything runs
        if hooks is not None:
            decision = hooks.check(tu.name, tu.input)
            if not decision.allow:
                blocked.append((tu.name, decision.reason))
                span.set("outcome", "blocked")
                return decision.reason

        # (2) approval — a sensitive call pauses for a human
        tool = registry.get(tu.name)
        if approval is not None and tool is not None:
            if approval.needs_approval(tu.name, tool.sensitive, tu.input):
                ok, message = approval.review(tu.name, tu.input)
                if not ok:
                    denied.append((tu.name, message))
                    span.set("outcome", "denied")
                    return message

        # (3) execute (the bash tool's own sandbox enforces the jail)
        observation = registry.dispatch(tu.name, tu.input)
        # The sandbox refuses inside the tool, so its refusal arrives here as an
        # ordinary return value. Tagging it "ok" would make the third gate the
        # one layer of the four you cannot see fire, which defeats the point of
        # tracing the gates at all.
        outcome = "refused" if observation.startswith("blocked:") else "ok"
        span.set("outcome", outcome)
        return observation
