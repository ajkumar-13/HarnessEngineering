"""Pre-tool hooks: deterministic gates that run before any tool executes.

The limit of asking the model nicely is that it can ignore you (Post 13). A hook
is code, not a request. Here a pre-tool hook inspects a pending ``(tool, args)``
call and either allows it or blocks it with a reason. The first block wins, so
the gate is fail-closed on a match. This is the enforcement half of the ratchet
(Post 10): a mistake seen once becomes a rule no future run can skip.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass
class Decision:
    allow: bool
    reason: str = ""


ALLOW = Decision(True)


def block(reason: str) -> Decision:
    return Decision(False, reason)


PreToolHook = Callable[[str, dict], Decision]

DEFAULT_DENY: List[Tuple[str, str]] = [
    (r"rm\s+-rf\s+(/|~|\*)",      "recursive delete of a broad path"),
    (r"git\s+push\s+--force",     "force-push"),
    (r"DROP\s+TABLE",             "destructive SQL"),
    (r":\(\)\s*\{.*\|:.*\};\s*:", "fork bomb"),
    (r"\bmkfs\b",                 "filesystem format"),
]


def deny_list(patterns: List[Tuple[str, str]] = DEFAULT_DENY) -> PreToolHook:
    """A hook that blocks any call whose serialised args match a dangerous rule."""
    compiled = [(re.compile(p, re.IGNORECASE), why) for p, why in patterns]

    def hook(tool: str, args: dict) -> Decision:
        text = f"{tool} " + json.dumps(args)
        for pattern, why in compiled:
            if pattern.search(text):
                return block(f"blocked by deny-list: {why}")
        return ALLOW

    return hook


@dataclass
class HookRegistry:
    pre_tool: List[PreToolHook]

    def __init__(self, pre_tool: "List[PreToolHook] | None" = None):
        self.pre_tool = list(pre_tool or [])

    def add_pre_tool(self, hook: PreToolHook) -> "HookRegistry":
        self.pre_tool.append(hook)
        return self

    def check(self, tool: str, args: dict) -> Decision:
        """Run every pre-tool hook; the first block wins (fail-closed)."""
        for hook in self.pre_tool:
            decision = hook(tool, args)
            if not decision.allow:
                return decision
        return ALLOW
