"""Post 11, feeding failures back: a no-progress exit for a correction loop, NOT shipped in the companion.

Run from the series root:  uv run python posts/11-verification-loops/snippets/same_report_exit.py
solve_until_stuck() is the companion's solve() plus exit (4): stop when the verifier has returned the same
report `window` times running. It runs the companion's own demo model and a model that never changes its
answer, at windows 2 and 3, and prints where each run ends. The companion's loop.py is imported, not edited.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "11-verification-loop" / "src"))

from verification_loop import Solution, VerifyResult, solve  # noqa: E402
from verification_loop.__main__ import make_mock_model  # noqa: E402
from verification_loop.checks import test_cases  # noqa: E402


def solve_until_stuck(generate, verify, *, max_attempts=5, window=3):
    feedback = None
    reports = []
    candidate, result = None, VerifyResult(ok=False, report="not attempted")
    for attempt in range(1, max_attempts + 1):
        candidate = generate(feedback)
        result = verify(candidate)
        if result.ok:
            return Solution(candidate, attempt, verified=True)
        reports.append(result.report)
        if len(reports) >= window and len(set(reports[-window:])) == 1:   # exit (4): no progress
            return Solution(candidate, attempt, verified=False, report=result.report)
        feedback = result.report
    return Solution(candidate, max_attempts, verified=False, report=result.report)


CASES = [((1,), False), ((2,), True), ((3,), True), ((4,), False), ((9,), False), ((13,), True), ((25,), False)]


def stuck_model():
    """A model that proposes its first answer every time, whatever the feedback says."""
    return lambda feedback: {"is_prime": lambda n: all(n % d for d in range(2, n))}


def show(label, sol):
    status = "verified" if sol.verified else "UNVERIFIED"
    print(f"{label:<34} {status:<10} after {sol.attempts} attempt(s)")


verify = test_cases("is_prime", CASES)
show("companion solve(), demo model", solve(make_mock_model(), verify))
show("window 2, demo model", solve_until_stuck(make_mock_model(), verify, window=2))
show("window 3, demo model", solve_until_stuck(make_mock_model(), verify, window=3))
show("companion solve(), stuck model", solve(stuck_model(), verify))
show("window 3, stuck model", solve_until_stuck(stuck_model(), verify, window=3))
