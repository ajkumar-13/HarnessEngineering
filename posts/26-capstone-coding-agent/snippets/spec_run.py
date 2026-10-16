"""Post 26, "Make it run": the capstone's two-task spec, run to completion across fresh contexts.

Run from the series root:  uv run python posts/26-capstone-coding-agent/snippets/spec_run.py

Imports code/26-coding-agent/src/coding_agent/ unchanged: build(), Ratchet, CostMeter, Tracer, and the demo's
scripted generator from __main__.py, which writes a buggy add() until a rule about add is in the context the
driver hands it. Part 1 runs the demo's spec and prints one line per generator call (what the call was handed,
the evaluator's verdict, the commit), the rules learned, the cost meter and the stop reason with the series exit
it maps to, then the trace tree. Part 2 runs the build three times against one rules file in a temporary
directory: a first process, a restart that constructs Ratchet(path=...) again, and a restart that reads the file
back into Ratchet(rules=..., path=...). Standard library only; no network, no model.
"""
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "26-coding-agent" / "src"))
from coding_agent import CostMeter, Ratchet, Spec, Task, Tracer, Workspace, build, python_function_verifier  # noqa: E402
from coding_agent.__main__ import generator  # noqa: E402

EXIT = {"spec_complete": "exit (1), completed", "task_failed": "exit (2), the per-task attempt cap",
        "budget": "exit (3), budget"}


def demo_spec():
    """The two-task spec of the companion's __main__.py, case for case."""
    return Spec([
        Task("add", python_function_verifier("calc.py", "add", [((2, 3), 5), ((0, 0), 0)])),
        Task("is_even", python_function_verifier("parity.py", "is_even", [((4,), True), ((3,), False)])),
    ])


def recording(gen, calls):
    """Wrap a generator to record what each call was handed: the driver builds every call's context afresh."""
    def wrapped(task, feedback, memory):
        rules = [line for line in memory.splitlines() if line.startswith("- ")]
        files = gen(task, feedback, memory)
        calls.append({"task": task.name, "feedback": feedback, "rules": len(rules), "files": sorted(files)})
        return files
    return wrapped


def money(cost):
    return f"${cost.cost():.4f}"


def part1():
    calls, tracer, ratchet = [], Tracer(), Ratchet()
    cost = CostMeter(budget_usd=1.00)
    ws = Workspace()
    res = build(demo_spec(), recording(generator, calls), workspace=ws, ratchet=ratchet,
                cost=cost, tracer=tracer, max_attempts=3)
    attempts = [s for _, s in tracer.root.walk() if s.name == "attempt"]
    print("Part 1: the demo's spec, one line per generator call")
    commits = 0
    for n, (call, att) in enumerate(zip(calls, attempts), 1):
        handed = "no report" if call["feedback"] is None else "last report"
        verdict = att.attributes["outcome"]
        if verdict == "pass":
            commits += 1
        print(f"  call {n}: task {call['task']:<8} handed {handed}, {call['rules']} rule(s); "
              f"wrote {', '.join(call['files'])}; verdict {verdict}; commits {commits}")
    print(f"rules learned: {res.rules_learned}")
    print(f"commits: {[c.task for c in res.commits]}; files in the last commit: {sorted(res.commits[-1].files)}")
    print(f"cost: {money(cost)}, {cost.input_tokens} in ({cost.cached_tokens} cached), "
          f"{cost.output_tokens} out, {cost.seconds:.1f} s")
    print(f"stop reason: {res.stop_reason} -> {EXIT[res.stop_reason]}")
    print()
    print(tracer.render())
    return res, calls


def part2():
    print()
    print("Part 2: one rules file, three processes")
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "rules.txt"
        rows = []
        for label in ("first process", "restart, Ratchet(path=...)", "restart, rules read back"):
            if label.endswith("read back"):
                lines = path.read_text(encoding="utf-8").splitlines()
                ratchet = Ratchet(rules=list(dict.fromkeys(lines)), path=str(path))  # read back, de-duplicated
            else:
                ratchet = Ratchet(path=str(path))
            start = len(ratchet.rules)
            tracer = Tracer()
            build(demo_spec(), generator, ratchet=ratchet, tracer=tracer, max_attempts=3)
            failed = sum(1 for _, s in tracer.root.walk()
                         if s.name == "attempt" and s.attributes["outcome"] == "fail")
            lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
            rows.append((label, start, failed, len(lines), len(set(lines))))
            print(f"  {label:<27} rules at start {start}; failed attempts {failed}; "
                  f"lines in the file {len(lines)} ({len(set(lines))} distinct)")
    return rows


if __name__ == "__main__":
    part1()
    part2()
