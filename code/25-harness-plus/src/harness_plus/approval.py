"""A human approval gate for irreversible or sensitive tool calls (Post 15).

Full autonomy is rarely the goal. Some calls should pause for a human before
they run. The gate is two parts: a *policy* that decides which calls need
approval, and a *decider* that returns the human's verdict. The decider is a
plain callable, so tests pass an auto-approve or auto-deny function and the
whole thing runs without a prompt.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# A decider takes (tool, args, reason) and returns True to approve, False to deny.
Decider = Callable[[str, dict, str], bool]


def always_approve(tool: str, args: dict, reason: str) -> bool:
    return True


def always_deny(tool: str, args: dict, reason: str) -> bool:
    return False


@dataclass
class ApprovalGate:
    """Pauses a flagged call and resumes on the decider's verdict.

    ``needs_approval`` decides which calls are gated. By default a call is gated
    when its tool is marked ``sensitive`` (see :class:`~harness_plus.tools.Tool`).
    """
    decide: Decider = always_approve

    def needs_approval(self, tool_name: str, sensitive: bool, args: dict) -> bool:
        return sensitive

    def review(self, tool_name: str, args: dict,
               reason: str = "sensitive tool call") -> "tuple[bool, str]":
        approved = self.decide(tool_name, args, reason)
        if approved:
            return True, "approved"
        return False, f"denied by approver: {reason}"
