"""A small hook system: a pre-tool deny-list and post-edit checks that gate a run.

Companion to Harness Engineering Post 13. Offline by design: hooks are plain
callables, so the whole thing runs with no API key and no network.

    pre-tool hook:  (tool: str, args: str) -> Decision
    post-edit hook: (path: str, content: str) -> str | None   # None = ok, str = problem
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


@dataclass
class Decision:
    """The result of a pre-tool hook: allow the call, or block it with a reason."""

    allow: bool
    reason: str = ""


ALLOW = Decision(allow=True)


def block(reason: str) -> Decision:
    return Decision(allow=False, reason=reason)


DEFAULT_DENY: List[Tuple[str, str]] = [
    (r"rm\s+-rf\s+(/|~|\*)",       "recursive delete of a broad path"),
    (r"git\s+push\s+--force",      "force-push"),
    (r"DROP\s+TABLE",              "destructive SQL"),
    (r":\(\)\s*\{.*\|:.*\};\s*:",  "fork bomb"),
    (r"\bmkfs\b",                  "filesystem format"),
]


def deny_list(
    patterns: List[Tuple[str, str]] = DEFAULT_DENY,
) -> Callable[[str, str], Decision]:
    """Build a pre-tool hook that blocks any command matching a dangerous pattern."""
    compiled = [(re.compile(p, re.IGNORECASE), why) for p, why in patterns]

    def hook(tool: str, args: str) -> Decision:
        text = f"{tool} {args}"
        for pattern, why in compiled:
            if pattern.search(text):
                return block(f"blocked: {why}")
        return ALLOW

    return hook


def post_edit_tests(
    run_tests: Callable[[], Tuple[bool, str]],
) -> Callable[[str, str], Optional[str]]:
    """Build a post-edit hook that runs tests after a Python file changes.

    ``run_tests`` returns ``(ok, report)``. The hook only fires on ``.py`` files
    and returns a problem string on failure, ``None`` when clean.
    """

    def hook(path: str, content: str) -> Optional[str]:
        if not path.endswith(".py"):
            return None
        ok, report = run_tests()
        return None if ok else f"tests failed after editing {path}: {report}"

    return hook


@dataclass
class HookRegistry:
    """Holds the hooks for a run and applies them at the lifecycle points."""

    pre_tool: List[Callable[[str, str], Decision]] = field(default_factory=list)
    post_edit: List[Callable[[str, str], Optional[str]]] = field(default_factory=list)

    def add_pre_tool(self, hook: Callable[[str, str], Decision]) -> "HookRegistry":
        self.pre_tool.append(hook)
        return self

    def add_post_edit(self, hook: Callable[[str, str], Optional[str]]) -> "HookRegistry":
        self.post_edit.append(hook)
        return self

    def check_tool(self, tool: str, args: str) -> Decision:
        """Run every pre-tool hook; the first block wins (fail-closed on a match)."""
        for hook in self.pre_tool:
            decision = hook(tool, args)
            if not decision.allow:
                return decision
        return ALLOW

    def after_edit(self, path: str, content: str) -> List[str]:
        """Run every post-edit hook; return the problems (empty list means clean)."""
        problems = []
        for hook in self.post_edit:
            problem = hook(path, content)
            if problem:
                problems.append(problem)
        return problems


def gated_call(
    registry: HookRegistry,
    tool: str,
    args: str,
    execute: Callable[[str, str], str],
) -> str:
    """Run pre-tool hooks, then execute only if allowed. A blocked call never runs."""
    decision = registry.check_tool(tool, args)
    if not decision.allow:
        return decision.reason  # deterministic observation; execute is never called
    return execute(tool, args)
