"""The verification gate: turn the workspace into pass/fail ground truth.

A harness that exits on the model *saying* it is done is a victory declaration
waiting to happen (Post 05). The gate makes "done" mean "verified": before the
loop is allowed to stop on a final answer, a verifier checks the work against
something objective (Post 11). Here the verifier runs test cases against a
function the agent wrote into the workspace.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Tuple

from .tools import Workspace


@dataclass
class Candidate:
    """What the gate judges: the model's final text plus the work it produced."""
    answer: str | None
    workspace: Workspace


@dataclass
class VerifyResult:
    """The verdict. ``report`` is empty on success and verbose on failure, so a
    rejected candidate gives the model something specific to fix."""
    ok: bool
    report: str = ""


Verifier = Callable[[Candidate], VerifyResult]


def python_function_tests(
    path: str,
    fn_name: str,
    cases: Iterable[Tuple[tuple, object]],
) -> Verifier:
    """Build a verifier that execs a workspace file and runs cases against a
    function it defines. A raised exception is reported, never propagated, so a
    failing candidate produces a report rather than crashing the gate.

    Exec-ing model code is exactly the blast radius Build #2 sandboxes (Post 14);
    Build #1 keeps it simple and in-process, as the Post 11 companion did.
    """
    cases = list(cases)

    def verify(candidate: Candidate) -> VerifyResult:
        source = candidate.workspace.files.get(path)
        if source is None:
            return VerifyResult(False, f"no file was written at {path!r}")
        namespace: dict = {}
        try:
            exec(compile(source, path, "exec"), namespace)
        except Exception as exc:
            return VerifyResult(False, f"{path} failed to import: "
                                       f"{type(exc).__name__}: {exc}")
        fn = namespace.get(fn_name)
        if not callable(fn):
            return VerifyResult(False, f"no callable named {fn_name!r} in {path}")
        failures = []
        for args, expected in cases:
            try:
                got = fn(*args)
            except Exception as exc:
                failures.append(f"{fn_name}{args!r} raised {type(exc).__name__}: {exc}")
                continue
            if got != expected:
                failures.append(f"{fn_name}{args!r} == {got!r}, expected {expected!r}")
        if failures:
            return VerifyResult(False, "; ".join(failures))
        return VerifyResult(True)

    return verify
