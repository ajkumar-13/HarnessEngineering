"""Example verifiers: turn ordinary Python into ground truth for the loop.

The strongest verifier is objective and executable (Post 11, section 2). Here a
candidate is a *namespace* (a dict mapping names to objects, e.g. the functions
a model "wrote"), and the verifier runs input/expected cases against it.
"""
from __future__ import annotations

from typing import Callable, Iterable, Tuple

from .loop import VerifyResult


def test_cases(
    fn_name: str,
    cases: Iterable[Tuple[tuple, object]],
) -> Callable[[dict], VerifyResult]:
    """Build a verifier from ``(args, expected)`` cases for one function.

    The returned callable takes a namespace dict, looks up ``fn_name``, runs
    every case, and returns a :class:`VerifyResult`. On failure the report names
    each failing case (a raised exception is reported, not propagated), so the
    model gets something specific to fix.
    """
    cases = list(cases)

    def verify(namespace: dict) -> VerifyResult:
        fn = namespace.get(fn_name)
        if not callable(fn):
            return VerifyResult(False, f"no callable named {fn_name!r} was defined")
        failures = []
        for args, expected in cases:
            try:
                got = fn(*args)
            except Exception as exc:  # report the failure, never crash the loop
                failures.append(f"{fn_name}{args!r} raised {type(exc).__name__}: {exc}")
                continue
            if got != expected:
                failures.append(f"{fn_name}{args!r} == {got!r}, expected {expected!r}")
        if failures:
            return VerifyResult(False, "; ".join(failures))
        return VerifyResult(True)

    return verify
