"""Core types: the workspace, a verdict, a task, and a spec.

The spec is the source of truth a long-horizon run converges on (Post 18): an
ordered list of tasks, each with an objective verifier. The workspace is the
code produced so far. Nothing here needs a model or a network.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List


@dataclass
class Workspace:
    """The files produced so far — the durable state a run commits (Post 08)."""
    files: dict[str, str] = field(default_factory=dict)

    def snapshot(self) -> dict[str, str]:
        return dict(self.files)


@dataclass
class VerifyResult:
    """Objective ground truth for one task. Verbose on failure (Post 11)."""
    ok: bool
    report: str = ""


# A verifier turns a workspace into a verdict — the evaluator's ground truth.
Verifier = Callable[[Workspace], VerifyResult]


@dataclass
class Task:
    """One unit of the build: a name and the check that says it is done."""
    name: str
    verify: Verifier


@dataclass
class Spec:
    """The whole build, as an ordered list of tasks. This is what the run
    converges on; when every task verifies, the run is complete."""
    tasks: List[Task] = field(default_factory=list)


def python_function_verifier(path: str, fn_name: str, cases) -> Verifier:
    """Build a verifier that execs a workspace file and runs cases against a
    function it defines. Exceptions are reported, never propagated."""
    cases = list(cases)

    def verify(ws: Workspace) -> VerifyResult:
        source = ws.files.get(path)
        if source is None:
            return VerifyResult(False, f"no file at {path!r}")
        ns: dict = {}
        try:
            exec(compile(source, path, "exec"), ns)
        except Exception as exc:
            return VerifyResult(False, f"{path} import error: {type(exc).__name__}: {exc}")
        fn = ns.get(fn_name)
        if not callable(fn):
            return VerifyResult(False, f"no callable {fn_name!r} in {path}")
        for args, expected in cases:
            try:
                got = fn(*args)
            except Exception as exc:
                return VerifyResult(False, f"{fn_name}{args!r} raised {type(exc).__name__}")
            if got != expected:
                return VerifyResult(False, f"{fn_name}{args!r} == {got!r}, expected {expected!r}")
        return VerifyResult(True)

    return verify
