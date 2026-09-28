"""The verification loop: generate, verify, retry on failure until green or capped.

Companion to Harness Engineering Post 11. Offline by design: ``generate`` and
``verify`` are plain callables, so the whole loop runs with no API key and no
network. Swap in an LLM for ``generate`` and a test runner for ``verify`` to
make it live.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class VerifyResult:
    """The verdict from a check.

    ``report`` is empty on success and verbose on failure: the failing test,
    the assertion, the diff — whatever the model needs to correct against.
    """

    ok: bool
    report: str = ""


@dataclass
class Solution:
    """The outcome of a verification loop."""

    candidate: object
    attempts: int
    verified: bool
    report: str = ""


def solve(
    generate: Callable[[Optional[str]], object],
    verify: Callable[[object], VerifyResult],
    *,
    max_attempts: int = 5,
) -> Solution:
    """Generate a candidate, verify it, and retry on failure until green or capped.

    ``generate(feedback)`` receives the previous failure report (or ``None`` on
    the first attempt) and returns a candidate. ``verify(candidate)`` returns a
    :class:`VerifyResult`. Success is silent (the candidate is returned as soon
    as a check passes); failure is verbose (its report is fed back into
    ``generate``). The ``max_attempts`` cap is the no-progress stop condition
    (Post 03, exit 4) applied to correction: a fix-it loop with no cap is a
    doom loop.

    The returned :class:`Solution` carries ``verified``; a caller that must not
    ship unverified work should check it before using ``candidate``.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    feedback: Optional[str] = None
    result = VerifyResult(ok=False, report="not attempted")
    candidate: object = None
    for attempt in range(1, max_attempts + 1):
        candidate = generate(feedback)          # the model proposes, given the last report
        result = verify(candidate)              # ground truth: tests, a schema, a judge
        if result.ok:
            return Solution(candidate, attempt, verified=True)
        feedback = result.report                # failure is verbose: feed it back in
    return Solution(candidate, max_attempts, verified=False, report=result.report)
