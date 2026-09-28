"""The long-horizon driver: the Ralph loop that runs the whole build (Post 18).

For each task in the spec the driver runs a fresh context — plan, generate,
evaluate, commit — and only the durable state crosses between tasks: the
workspace (git-like commits) and the ratchet's learned rules (Post 08, Post 10).
Roles are separated (Post 12): the *generator* proposes, an *independent
evaluator* (the task's verifier) judges. Every step is traced (Post 21) and
metered against a cost ceiling (Posts 19, 23).

    plan(spec) -> tasks
      for each task, fresh context:
        attempt: generate -> evaluate -> (commit | learn a rule and retry)
      stop when the spec is complete, a task is unfixable, or the budget is spent
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Iterator, List, Optional

from .core import Spec, Task, Workspace
from .cost import CostMeter
from .memory import Ratchet
from .observe import Span, Tracer

# A generator proposes files for a task, given the last failure report and the
# learned-rules context. It is deliberately separate from the evaluator.
Generator = Callable[[Task, Optional[str], str], dict]


@dataclass
class Commit:
    task: str
    files: dict


@dataclass
class BuildResult:
    succeeded: bool
    completed: List[str]
    commits: List[Commit]
    rules_learned: List[str]
    cost: CostMeter
    stop_reason: str
    failed_task: Optional[str] = None
    trace: Optional[Span] = None


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


def plan(spec: Spec) -> List[Task]:
    """The planner. Here it preserves order; a real planner would decompose and
    sequence. Separated out so the role is explicit (Post 12)."""
    return list(spec.tasks)


def _default_rule(task: Task, report: str) -> str:
    return f"[{task.name}] previously failed: {report}"


def build(spec: Spec, generator: Generator, *,
          workspace: Optional[Workspace] = None,
          ratchet: Optional[Ratchet] = None,
          cost: Optional[CostMeter] = None,
          tracer: Optional[Tracer] = None,
          max_attempts: int = 3,
          learn_after: int = 1,
          rule_from: Callable[[Task, str], str] = _default_rule,
          tokens_per_attempt: tuple = (2000, 1500, 300),  # (input, cached, output)
          seconds_per_attempt: float = 1.5) -> BuildResult:
    workspace = workspace if workspace is not None else Workspace()
    ratchet = ratchet if ratchet is not None else Ratchet()
    cost = cost if cost is not None else CostMeter()
    commits: List[Commit] = []
    completed: List[str] = []
    in_tok, cached_tok, out_tok = tokens_per_attempt

    with _maybe_span(tracer, "build.run", spec_tasks=len(spec.tasks)) as run_span:
        for task in plan(spec):
            with _maybe_span(tracer, "task", task=task.name) as task_span:
                feedback: Optional[str] = None
                passed = False

                for attempt in range(1, max_attempts + 1):
                    # budget is an economic stop condition, checked before spend
                    if cost.over_budget():
                        run_span.set("stop.reason", "budget")
                        return BuildResult(False, completed, commits, ratchet.rules,
                                           cost, "budget", task.name, tracer.root if tracer else None)

                    with _maybe_span(tracer, "attempt", index=attempt) as att:
                        with _maybe_span(tracer, "generate"):
                            files = generator(task, feedback, ratchet.as_context())
                            workspace.files.update(files)
                            cost.add(input_tokens=in_tok, cached_tokens=cached_tok,
                                     output_tokens=out_tok, seconds=seconds_per_attempt)

                        with _maybe_span(tracer, "evaluate") as ev:
                            verdict = task.verify(workspace)
                            ev.set("ok", verdict.ok)

                        if verdict.ok:
                            att.set("outcome", "pass")
                            commits.append(Commit(task.name, workspace.snapshot()))
                            completed.append(task.name)
                            passed = True
                            break

                        att.set("outcome", "fail")
                        feedback = verdict.report
                        if attempt >= learn_after:
                            ratchet.learn(rule_from(task, verdict.report))

                task_span.set("passed", passed)
                if not passed:
                    run_span.set("stop.reason", "task_failed")
                    return BuildResult(False, completed, commits, ratchet.rules,
                                       cost, "task_failed", task.name,
                                       tracer.root if tracer else None)

        run_span.set("stop.reason", "spec_complete")
    return BuildResult(True, completed, commits, ratchet.rules, cost,
                       "spec_complete", None, tracer.root if tracer else None)
