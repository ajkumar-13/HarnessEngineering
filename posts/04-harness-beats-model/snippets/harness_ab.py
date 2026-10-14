"""A paired A/B of two harness configurations on one fixed task set, with the model the same in both.

The outcomes below are illustrative, not a measurement: 100 tasks, where configuration A resolves 50 and
configuration B fixes 5 of A's failures and breaks 3 of A's successes. The point is what the paired counts
show that the mean does not.

Run from the series root:  uv run python posts/04-harness-beats-model/snippets/harness_ab.py
"""


def harness_ab(tasks, run_a, run_b):
    """Paired A/B of two harness configs. run_x(task) -> True if resolved."""
    wins_a = wins_b = ties = 0
    resolved_a = resolved_b = 0
    for task in tasks:                      # fixed, versioned set
        a, b = run_a(task), run_b(task)     # same model inside both
        resolved_a += a
        resolved_b += b
        if a and not b:   wins_a += 1
        elif b and not a: wins_b += 1
        else:             ties += 1
    n = len(tasks)
    return {"resolved_a": resolved_a / n, "resolved_b": resolved_b / n,
            "delta": (resolved_b - resolved_a) / n,
            "wins_a": wins_a, "wins_b": wins_b, "ties": ties}


TASKS = list(range(100))                     # illustrative task ids
A_RESOLVES = set(range(50))                  # A resolves tasks 0 to 49
B_RESOLVES = (A_RESOLVES - {0, 1, 2}) | {50, 51, 52, 53, 54}   # B breaks 3 and fixes 5


if __name__ == "__main__":
    r = harness_ab(TASKS, lambda t: t in A_RESOLVES, lambda t: t in B_RESOLVES)
    print(f"resolved: A {r['resolved_a']:.0%}, B {r['resolved_b']:.0%}, delta {r['delta']:+.0%}")
    print(f"paired:   B fixed {r['wins_b']}, B broke {r['wins_a']}, unchanged {r['ties']}")
