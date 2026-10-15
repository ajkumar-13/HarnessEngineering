"""Post 11, the economics of an unverified run, on the series' illustrative twelve-iteration example.

Run from the series root:  uv run python posts/11-verification-loops/snippets/unverified_cost.py
The run is post 23's running example, illustrative rather than measured: the first request sends 6,000 input
tokens and each turn adds 3,100, so iteration k sends 6,000 + 3,100 * (k - 1). An error enters at iteration 2.
Without a gate it is caught at the end and iterations 2 to 12 are forfeit; with a gate on every step it fails
its check at iteration 2 and only that iteration is forfeit. A judge reading a 12,000-token candidate is priced
at one call per step and at three checkpoints.
"""
ITERATIONS, FIRST, GROWTH, ERROR_AT = 12, 6_000, 3_100, 2
JUDGE_READS, CHECKPOINTS = 12_000, 3

tokens = [FIRST + GROWTH * (k - 1) for k in range(1, ITERATIONS + 1)]


def run_total():
    return sum(tokens)


def forfeited(caught_at):
    """Input tokens of the iterations from the error's entry up to the one where it is caught."""
    return sum(tokens[ERROR_AT - 1:caught_at])


if __name__ == "__main__":
    total = run_total()
    print("input tokens per iteration:", ", ".join(f"{t:,}" for t in tokens))
    print(f"run total: {total:,}")
    for label, caught in [("no gate", ITERATIONS), ("gate on every step", ERROR_AT)]:
        lost = forfeited(caught)
        span = f"iteration {caught}" if caught == ERROR_AT else f"iterations {ERROR_AT} to {caught}"
        print(f"{label}: caught at iteration {caught}, {span} forfeit, {lost:,} tokens ({lost / total:.1%})")
    for label, calls in [("judge on every step", ITERATIONS), ("judge at checkpoints", CHECKPOINTS)]:
        extra = calls * JUDGE_READS
        print(f"{label}: {calls} x {JUDGE_READS:,} = {extra:,} tokens (+{extra / total:.1%})")
