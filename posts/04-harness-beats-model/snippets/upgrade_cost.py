"""Buy a harness fix once, or rent a model upgrade on every run: the arithmetic behind the order of moves.

Every size here is illustrative. The run is post 23's running example: twelve iterations, the first request
sends 6,000 tokens and each turn appends 3,100 more. The upgrade triples the price per token; the harness fix
costs one engineer-day, taken to be worth 1,000 runs at today's price; the system makes 200 runs a day.

Run from the series root:  uv run python posts/04-harness-beats-model/snippets/upgrade_cost.py
"""
ITERS, FIRST, GROWTH = 12, 6_000, 3_100      # post 23's running example (illustrative)
PRICE_MULTIPLE = 3                            # the upgrade triples the price per token
FIX_IN_RUNS = 1_000                           # one engineer-day, priced in runs at today's cost C
RUNS_PER_DAY = 200


def input_tokens(iters=ITERS, first=FIRST, growth=GROWTH):
    """Total input of one run: every request re-reads all the history before it."""
    return sum(first + growth * (i - 1) for i in range(1, iters + 1))


def break_even_runs(multiple=PRICE_MULTIPLE, fix=FIX_IN_RUNS):
    """Runs after which the upgrade's extra cost, (multiple - 1) C per run, passes the one-off fix."""
    return fix / (multiple - 1)


def cumulative(runs, multiple=PRICE_MULTIPLE, fix=FIX_IN_RUNS):
    """Extra spend in units of C after a number of runs: (fix, upgrade)."""
    return fix, (multiple - 1) * runs


if __name__ == "__main__":
    grown, flat = input_tokens(), ITERS * FIRST
    runs = break_even_runs()
    print(f"one run reads {grown:,} input tokens; a context that never grew would read {flat:,}")
    print(f"growth multiplies the input by {grown / flat:.2f}")
    print(f"upgrade: {PRICE_MULTIPLE}C a run, {PRICE_MULTIPLE - 1}C extra on every run")
    print(f"fix: {FIX_IN_RUNS:,}C once; break-even after {runs:,.0f} runs, "
          f"{runs / RUNS_PER_DAY:.1f} days at {RUNS_PER_DAY} runs a day")
