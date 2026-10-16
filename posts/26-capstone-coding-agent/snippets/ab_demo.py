"""Post 26, "Observability and harness A/B": two driver configurations, the model held fixed.

Run from the series root:  uv run python posts/26-capstone-coding-agent/snippets/ab_demo.py

Imports code/26-coding-agent/src/coding_agent/ unchanged. Both arms run the demo's two-task spec with the demo's
scripted generator (this build's "model", from __main__.py) and a fresh workspace, ratchet and cost meter; the
only knob that moves is learn_after: 1 learns a rule after every failed attempt, 99 never reaches the threshold,
so no rule is ever learned. The script prints each arm's resolved count, stop reason, spend and cost per completed
task, how many attempts handed back a candidate identical to the one before it on the same task, the paired
per-task outcomes, and a two-sided sign test on the discordant pairs (post 22's vocabulary: a difference is
callable when the test rejects at 0.05). The generator is built to obey any rule that names its task, so the
lift is designed in: the run shows the mechanism, not evidence about a model. Standard library only.
"""
import sys
from math import comb
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "26-coding-agent" / "src"))
from coding_agent import CostMeter, Ratchet, Spec, Task, Workspace, build, python_function_verifier  # noqa: E402
from coding_agent.__main__ import generator  # noqa: E402

ARMS = {1: "learn_after=1 (ratchet on)", 99: "learn_after=99 (ratchet off)"}


def mkspec():
    """The two-task spec of the companion's __main__.py."""
    return Spec([
        Task("add", python_function_verifier("calc.py", "add", [((2, 3), 5), ((0, 0), 0)])),
        Task("is_even", python_function_verifier("parity.py", "is_even", [((4,), True), ((3,), False)])),
    ])


def watch(gen, seen):
    """Record each task's candidates, so a repeat of the previous attempt's files can be counted."""
    def wrapped(task, feedback, memory):
        files = gen(task, feedback, memory)
        seen.setdefault(task.name, []).append(dict(files))
        return files
    return wrapped


def sign_test(wins_a, wins_b):
    """Two-sided p-value on the discordant pairs."""
    n, k = wins_a + wins_b, min(wins_a, wins_b)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def arms():
    """Both arms on the same spec and generator; returns {learn_after: (BuildResult, CostMeter, repeats)}."""
    results = {}
    for learn_after in (1, 99):                    # the ratchet on, then off
        cost, seen = CostMeter(budget_usd=1.00), {}
        res = build(mkspec(), watch(generator, seen), workspace=Workspace(), ratchet=Ratchet(),
                    cost=cost, learn_after=learn_after, max_attempts=3)
        repeats = sum(a == b for c in seen.values() for a, b in zip(c, c[1:]))
        results[learn_after] = (res, cost, repeats)
    return results


def main():
    results = arms()
    tasks = [t.name for t in mkspec().tasks]
    print("the model is held fixed; only learn_after moves")
    for k, (res, cost, repeats) in results.items():
        per = f"${cost.cost() / len(res.completed):.4f}" if res.completed else "none completed"
        print(f"  {ARMS[k]:<29} resolved {len(res.completed)} of {len(tasks)}; {res.stop_reason}; "
              f"completed {res.completed}; spend ${cost.cost():.4f}; per completed task {per}; "
              f"repeated candidates {repeats}")
    on, off = ([t in results[k][0].completed for t in tasks] for k in (1, 99))
    attempted_off = {s.task for s in results[99][0].commits} | {results[99][0].failed_task}
    print("per task, resolved (on/off): " + ", ".join(
        f"{t} {int(a)}/{int(b)}" + ("" if t in attempted_off else " (never attempted when off)")
        for t, a, b in zip(tasks, on, off)))
    wins_on = sum(a and not b for a, b in zip(on, off))
    wins_off = sum(b and not a for a, b in zip(on, off))
    p = sign_test(wins_off, wins_on)
    print(f"discordant pairs {wins_on + wins_off}: {wins_on} for the ratchet, {wins_off} against; "
          f"sign test p = {p:.2f}: {'callable' if p < 0.05 else 'not callable'}")
    need = next(n for n in range(1, 50) if sign_test(0, n) < 0.05)
    print(f"the fewest discordant pairs, all one way, that reach p < 0.05: {need}")


if __name__ == "__main__":
    main()
