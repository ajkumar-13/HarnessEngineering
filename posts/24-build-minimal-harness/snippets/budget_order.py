"""Post 24, the exercise: where the budget check sits in Build #1's loop, and what it lets through.

Run from the series root:  uv run python posts/24-build-minimal-harness/snippets/budget_order.py

Imports run() from code/24-minimal-harness unchanged and drives it with ScriptedModel, whose per-response token
counts are set by hand, so every number below is computed from the companion and illustrative of the mechanism,
not a measured price. It prints, in order: where the checks sit inside run(); the budget exit on the tool-call path;
the budget exit on the gate-rejection path at three turn sizes (the table in the post); and the one path with no
budget check, a final answer that passes the gate.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "24-minimal-harness" / "src"))
from minimal_harness import (ScriptedModel, ToolRegistry, VerifyResult, make_bash_tool, run,  # noqa: E402
                             text_response, tool_response)

BUDGET = 2000


def check_order():
    """The line of harness.py on which each decision of run() sits."""
    source, first = inspect.getsourcelines(run)
    lines = [line.rstrip() for line in source]
    marks = [("model call counted", "tokens_used += resp.tokens"),
             ("final-answer branch: the gate", "if resp.is_final():"),
             ("budget check, gate-rejection path", "if token_budget is not None"),
             ("budget check, tool-call path", "if token_budget is not None"),
             ("no-progress check", "if len(window) == no_progress_window"),
             ("tools run", "registry.dispatch(")]
    found, start = [], 0
    for label, text in marks:
        n = next(i for i in range(start, len(lines)) if text in lines[i])
        found.append((first + n, label))
        start = n + 1
    return found


def show(label, result):
    print(f"{label}: exit {result.stop_reason.value}, iteration {result.iterations}, "
          f"{result.tokens_used:,} tokens, verified {result.verified}")
    return result


def main():
    print("inside run() in harness.py, in the order each turn meets them:")
    for line, label in check_order():
        print(f"  line {line:3}: {label}")

    tools = ToolRegistry([make_bash_tool(runner=lambda command, timeout: ("ok", 0))])
    calls = [tool_response("bash", {"command": f"echo {i}"}, id=f"b{i}", tokens=50) for i in range(100)]
    show("\ntool-call path, 50 tokens a turn, token_budget=120",
         run(ScriptedModel(calls), tools, "spend", max_iters=100, token_budget=120))

    always_reject = lambda candidate: VerifyResult(False, "still wrong")  # noqa: E731
    print(f"\ngate-rejection path, an always-rejecting gate, token_budget={BUDGET:,}, max_iters=40:")
    rows = []
    for per_turn in (600, 1500, 2500):
        model = ScriptedModel([text_response("done", tokens=per_turn)] * 100)
        r = run(model, ToolRegistry([]), "loop", verify=always_reject, max_iters=40, token_budget=BUDGET)
        over = (r.tokens_used - BUDGET) / BUDGET
        rows.append((per_turn, r.stop_reason.value, r.iterations, r.tokens_used, over))
        print(f"  {per_turn:5,} tokens a turn: exit {r.stop_reason.value} at iteration {r.iterations}, "
              f"{r.tokens_used:,} tokens spent, {over:.0%} over the ceiling")

    passing = lambda candidate: VerifyResult(True)  # noqa: E731
    model = ScriptedModel([tool_response("bash", {"command": "echo build"}, tokens=1500),
                           text_response("done", tokens=1000)])
    final = show(f"\na final answer that passes the gate, token_budget={BUDGET:,}",
                 run(model, tools, "finish", verify=passing, max_iters=40, token_budget=BUDGET))
    return dict(order=check_order(), rows=rows, final=final)


if __name__ == "__main__":
    main()
