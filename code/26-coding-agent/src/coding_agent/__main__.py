"""Offline demo: ``python -m coding_agent``.

A two-task build. The generator gets ``add`` wrong on the first attempt; the
evaluator rejects it; the ratchet learns a rule; the next attempt reads that
rule and fixes it. The second task passes first try. The run prints the commits,
the learned rules, the metered cost, and the whole trace tree.
"""
from .core import Spec, Task, Workspace, python_function_verifier
from .cost import CostMeter
from .driver import build
from .memory import Ratchet
from .observe import Tracer

ADD_OK = "def add(a, b):\n    return a + b\n"
ADD_BUG = "def add(a, b):\n    return a - b  # bug: subtracts\n"
IS_EVEN = "def is_even(n):\n    return n % 2 == 0\n"


def generator(task: Task, feedback, memory: str) -> dict:
    """A scripted stand-in for a model. It behaves better once the ratchet has
    taught it something about this task (the rule shows up in ``memory``)."""
    if task.name == "add":
        return {"calc.py": ADD_OK if "[add]" in memory else ADD_BUG}
    if task.name == "is_even":
        return {"parity.py": IS_EVEN}
    return {}


def main() -> None:
    spec = Spec([
        Task("add", python_function_verifier("calc.py", "add",
                                             [((2, 3), 5), ((0, 0), 0)])),
        Task("is_even", python_function_verifier("parity.py", "is_even",
                                                 [((4,), True), ((3,), False)])),
    ])
    tracer, ratchet = Tracer(), Ratchet()
    cost = CostMeter(budget_usd=1.00)

    result = build(spec, generator, workspace=Workspace(), ratchet=ratchet,
                   cost=cost, tracer=tracer, max_attempts=3)

    print(f"succeeded    : {result.succeeded}  ({result.stop_reason})")
    print(f"completed    : {result.completed}")
    print(f"commits      : {[c.task for c in result.commits]}")
    print(f"rules learned: {result.rules_learned}")
    print(f"cost         : {cost.summary()}")
    print("\n== trace ==")
    print(tracer.render())


if __name__ == "__main__":
    main()
