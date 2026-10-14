"""What a doom loop costs in tokens, under each exit that could stop it.

Runs the loop of harness_loop.py against its scripted doom loop (the same failing edit from
turn 3 on) with one exit enabled at a time, and prints the tokens each run reads and writes.
The sizes are illustrative: a 4,000-token stable prefix, 1,200 tokens appended per turn,
400 written per turn.

Run from the series root:  python posts/01-from-context-to-harness/snippets/exit_cost.py
"""
from harness_loop import ScriptedModel, run_loop

TASK = "Fix the failing test in app.py."
RUNS = [
    ("iteration cap of 12, nothing else", {"max_iters": 12}),
    ("token budget of 40,000", {"max_iters": 1_000, "token_budget": 40_000}),
    ("no progress, window of 3", {"max_iters": 1_000, "window": 3}),
]


def table(runs=RUNS):
    rows = []
    for label, kwargs in runs:
        r = run_loop(ScriptedModel(), TASK, **kwargs)
        rows.append((label, r["exit"], r["turn"], r["read"], r["written"], r["read"] + r["written"]))
    return rows


if __name__ == "__main__":
    rows = table()
    print(f"{'exit enabled':36}{'fires':>14}{'turn':>6}{'read':>10}{'written':>9}{'total':>10}")
    for label, fired, turn, read, written, total in rows:
        print(f"{label:36}{fired:>14}{turn:>6}{read:>10,}{written:>9,}{total:>10,}")
    cap24 = table([("iteration cap of 24, nothing else", {"max_iters": 24})])[0]
    print(f"{cap24[0]:36}{cap24[1]:>14}{cap24[2]:>6}{cap24[3]:>10,}{cap24[4]:>9,}{cap24[5]:>10,}")
    print(f"cap of 12 / no progress: {rows[0][5] / rows[2][5]:.2f} times")
    print(f"cap of 24 / cap of 12:   {cap24[5] / rows[0][5]:.2f} times")
