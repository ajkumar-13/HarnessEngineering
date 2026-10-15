"""Post 11, the lab: the same four-step task run with a verification gate on every step and with none.

Run from the series root:  uv run python posts/11-verification-loops/snippets/gate_vs_no_gate.py
The companion (code/11-verification-loop) is imported unchanged: solve(), test_cases() and its demo model,
whose first two is_prime candidates fail the case is_prime(1) == False. Steps 2 to 4 build on is_prime.
With the gate, each step runs through solve() against its own test cases and retries to green. Without it,
the gate is removed (a verify that always passes), every first candidate is accepted, and the same tests
run once at the end. The "model" is scripted, so the counts are illustrative: they count model calls in a
toy, not tokens in a real run.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "11-verification-loop" / "src"))

from verification_loop import VerifyResult, solve  # noqa: E402
from verification_loop.__main__ import make_mock_model  # noqa: E402
from verification_loop.checks import test_cases  # noqa: E402


def scripted(*attempts):
    """A scripted model: one candidate per call, the last one repeated if the loop asks again."""
    calls = []

    def generate(feedback):
        calls.append(feedback)
        return attempts[min(len(calls), len(attempts)) - 1]
    return generate


def steps(ns):
    """The task: four functions, each later one calling the ones before it through the namespace `ns`."""
    return [
        ("is_prime", make_mock_model(),
         [((1,), False), ((2,), True), ((3,), True), ((4,), False), ((9,), False), ((13,), True), ((25,), False)]),
        ("primes_below", scripted({"primes_below": lambda n: [k for k in range(n) if ns["is_prime"](k)]}),
         [((10,), [2, 3, 5, 7]), ((2,), [])]),
        ("count_primes", scripted({"count_primes": lambda n: len(ns["primes_below"](n))}),
         [((30,), 10), ((10,), 4)]),
        ("twin_primes_below", scripted({"twin_primes_below": lambda n: [
            (p, p + 2) for p in ns["primes_below"](n) if p + 2 < n and ns["is_prime"](p + 2)]}),
         [((10,), [(3, 5), (5, 7)]), ((20,), [(3, 5), (5, 7), (11, 13), (17, 19)])]),
    ]


def gated():
    ns, calls = {}, 0
    print("with a gate on every step")
    attempt, unverified = {}, []
    for k, (name, generate, cases) in enumerate(steps(ns), start=1):
        check = test_cases(name, cases)

        def verify(candidate, check=check, k=k, name=name):
            result = check({**ns, **candidate})
            attempt[k] = attempt.get(k, 0) + 1
            verdict = "pass" if result.ok else "FAIL  " + result.report
            print(f"  step {k} {name:<17} attempt {attempt[k]}  {verdict}")
            return result
        sol = solve(generate, verify, max_attempts=5)
        ns.update(sol.candidate)
        calls += sol.attempts
        if not sol.verified:
            unverified.append(name)
    status = f"left unverified: {', '.join(unverified)}" if unverified else "each step verified before the next one began"
    print(f"  model calls: {calls}; {status}")
    return calls


def ungated():
    ns, calls = {}, 0
    print("without the gate")
    for name, generate, _ in steps(ns):
        sol = solve(generate, lambda candidate: VerifyResult(True), max_attempts=5)   # the gate removed
        ns.update(sol.candidate)
        calls += sol.attempts
    print(f"  model calls: {calls}; solve() reported verified on every step")
    failing = []
    for name, _, cases in steps(ns):
        result = test_cases(name, cases)(ns)
        if not result.ok:
            failing.append(name)
            print(f"  checked at the end: {name:<17} FAIL  {result.report.split('; ')[0]}")
    downstream = [name for name in failing if name != "is_prime"]
    print(f"  steps failing at the end: {len(failing)} of 4, {len(downstream)} of them built on the error in step 1")
    return calls, len(failing)


if __name__ == "__main__":
    with_gate = gated()
    without_gate, failing = ungated()
    print(f"without the gate {without_gate} calls are wasted; redoing the task with the gate makes it "
          f"{without_gate} + {with_gate} = {without_gate + with_gate} calls against {with_gate}")
