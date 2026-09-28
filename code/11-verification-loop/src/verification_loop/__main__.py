"""Demo: a mock model converges to a correct implementation under verification.

Run:  python -m verification_loop
Offline: no API key, no network. The "model" is a canned sequence of attempts,
from buggy to correct; a real harness would call an LLM in ``generate`` and pass
it the failure ``feedback``.
"""
from __future__ import annotations

from .checks import test_cases
from .loop import solve


def make_mock_model():
    """Return a ``generate`` that proposes better ``is_prime`` implementations.

    Each call returns the next attempt. A real model would read ``feedback`` (the
    last failure report) and revise; the mock simply improves in sequence.
    """
    attempts = [
        # attempt 1: no lower bound, so is_prime(1) is wrongly True
        {"is_prime": lambda n: all(n % d for d in range(2, n))},
        # attempt 2: faster, but still no lower bound
        {"is_prime": lambda n: all(n % d for d in range(2, int(n**0.5) + 1))},
        # attempt 3: correct
        {"is_prime": lambda n: n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))},
    ]
    state = {"i": 0}

    def generate(feedback):  # feedback unused by the mock; a real model would use it
        i = min(state["i"], len(attempts) - 1)
        state["i"] += 1
        return attempts[i]

    return generate


def main() -> None:
    verify = test_cases(
        "is_prime",
        [((1,), False), ((2,), True), ((3,), True), ((4,), False),
         ((9,), False), ((13,), True), ((25,), False)],
    )
    result = solve(make_mock_model(), verify, max_attempts=5)
    status = "verified" if result.verified else "UNVERIFIED"
    print(f"{status} after {result.attempts} attempt(s)")
    if not result.verified:
        print("last failure:", result.report)


if __name__ == "__main__":
    main()
