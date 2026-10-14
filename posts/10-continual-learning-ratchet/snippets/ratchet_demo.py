"""Post 10, "Make it run": the companion Ratchet, run twice, then across sessions.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/snippets/ratchet_demo.py

Imports Ratchet and build() from code/26-coding-agent/src/coding_agent/ unchanged (memory.py and
driver.py). The generator is a scripted stand-in for a model: it writes the buggy version of a task
until a rule about that task appears in the context the driver hands it, then the correct one. Part 1
is the two-run comparison of the plan's lab: the same generator with the ratchet learning and with
learning switched off. Part 2 runs four sessions, each adding one task, with and without a memory
file read back at session start. Standard library only; every file lives in a temporary directory.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "26-coding-agent" / "src"))
from coding_agent import Ratchet, Spec, Task, Tracer, build, python_function_verifier  # noqa: E402

# Each task: a file, a function, test cases, the correct source and the buggy one.
TASKS = {
    "add": ("calc.py", "add", [((2, 3), 5), ((1, 1), 2)],
            "def add(a, b):\n    return a + b\n", "def add(a, b):\n    return a - b\n"),
    "is_even": ("parity.py", "is_even", [((4,), True), ((3,), False)],
                "def is_even(n):\n    return n % 2 == 0\n", "def is_even(n):\n    return n % 2 == 1\n"),
    "clamp": ("bounds.py", "clamp", [((5, 0, 3), 3), ((-1, 0, 3), 0)],
              "def clamp(x, lo, hi):\n    return max(lo, min(x, hi))\n",
              "def clamp(x, lo, hi):\n    return min(lo, max(x, hi))\n"),
    "mean": ("stats.py", "mean", [(([1, 2, 3],), 2), (([4],), 4)],
             "def mean(xs):\n    return sum(xs) / len(xs)\n", "def mean(xs):\n    return sum(xs) // 2\n"),
}


def task(name):
    path, fn, cases, _, _ = TASKS[name]
    return Task(name, python_function_verifier(path, fn, cases))


def generator(task, feedback, memory):
    """The scripted model: wrong until a rule about this task is in its context."""
    path, _, _, good, bad = TASKS[task.name]
    return {path: good if f"[{task.name}]" in memory else bad}


def attempts(tracer):
    """(task, attempt index, outcome) for every attempt the driver traced."""
    out, current = [], None
    for _, span in tracer.root.walk():
        if span.name == "task":
            current = span.attributes["task"]
        elif span.name == "attempt":
            out.append((current, span.attributes["index"], span.attributes["outcome"]))
    return out


def part1(tmp):
    print("Part 1: one task, the same generator, two runs (max_attempts=3)")
    rules_file = tmp / "AGENTS.rules.md"
    runs = [("run 1, the ratchet learns (learn_after=1)", Ratchet(path=str(rules_file)), 1),
            ("run 2, learning switched off (learn_after=4)", Ratchet(), 4)]
    for label, ratchet, learn_after in runs:
        tracer = Tracer()
        res = build(Spec([task("add")]), generator, ratchet=ratchet, tracer=tracer,
                    max_attempts=3, learn_after=learn_after)
        print(f"  {label}")
        for _, index, outcome in attempts(tracer):
            print(f"    attempt {index}  {outcome}")
        print(f"    stop reason: {res.stop_reason}; rules learned: {len(res.rules_learned)}")
    print(f"  the memory file after run 1, {rules_file.name}:")
    for line in rules_file.read_text(encoding="utf-8").splitlines():
        print(f"    {line}")
    print(f"  learn() on the same rule again returns {runs[0][1].learn(runs[0][1].rules[0])}")


def session(names, rules_file=None):
    """One session: a fresh driver run. With a file, the rules are read back first."""
    if rules_file is None:
        ratchet = Ratchet()                       # nothing survives the last session
    else:
        known = rules_file.read_text(encoding="utf-8").splitlines() if rules_file.exists() else []
        ratchet = Ratchet(rules=known, path=str(rules_file))
    in_force = len(ratchet.rules)
    tracer = Tracer()
    res = build(Spec([task(n) for n in names]), generator, ratchet=ratchet, tracer=tracer,
                max_attempts=3)
    failed = sum(1 for _, _, outcome in attempts(tracer) if outcome == "fail")
    return in_force, failed, res.stop_reason


def part2(tmp):
    print()
    print("Part 2: four sessions, one new task each")
    print("  session  tasks  rules read back  failed, with the file  failed, without")
    rules_file = tmp / "AGENTS.sessions.md"
    names = list(TASKS)
    totals = [0, 0]
    for k in range(1, len(names) + 1):
        rules_at_start, failed_with, stop_with = session(names[:k], rules_file)
        _, failed_without, stop_without = session(names[:k])
        assert stop_with == stop_without == "spec_complete"
        totals[0] += failed_with
        totals[1] += failed_without
        print(f"  {k:>7}  {k:>5}  {rules_at_start:>15}  {failed_with:>21}  {failed_without:>15}")
    print(f"  failed attempts over four sessions: {totals[0]} with the file, {totals[1]} without")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        part1(Path(d))
        part2(Path(d))
