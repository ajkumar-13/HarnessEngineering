"""What one task's re-sent history is billed, for three runs under the same iteration cap of 12.

Illustrative sizes, the series' running example (post 23): the first request sends 6,000 input tokens and each
turn appends 3,100 more, so request n sends 6,000 + 3,100 * (n - 1) and the twelfth sends 40,100. In the third run
a 20,000-token log is read at turn 5: it enters the history with that turn's result and is re-sent on every turn
after it. The rate is $3 per million input tokens, the Claude Sonnet 4.6 input rate on Anthropic's pricing page
(consulted October 2026); output tokens are left out.

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/run_cost.py
"""
FIRST, GROWTH, LOG, LOG_TURN, RATE = 6_000, 3_100, 20_000, 5, 3.00   # tokens, tokens, tokens, turn, $ per million


def inputs(turns, log_turn=None):
    """Input tokens of each request, turn 1 to turns."""
    return [FIRST + GROWTH * (n - 1) + (LOG if log_turn and n > log_turn else 0) for n in range(1, turns + 1)]


RUNS = [
    ("answers at iteration 6", 6, None),
    ("runs to the cap", 12, None),
    ("runs to the cap, one 20,000-token log at turn 5", 12, LOG_TURN),
]


def table():
    return [(label, turns, sum(inputs(turns, log)), sum(inputs(turns, log)) * RATE / 1e6) for label, turns, log in RUNS]


if __name__ == "__main__":
    print(f"{'run, max_iters=12':49}{'turns':>6}{'input re-read':>15}{'at $3/M':>9}")
    rows = table()
    for label, turns, total, dollars in rows:
        print(f"{label:49}{turns:>6}{total:>15,}{dollars:>9.2f}")
    print(f"request 1: {inputs(12)[0]:,}  request 12: {inputs(12)[-1]:,}  log re-sent on {12 - LOG_TURN} turns: "
          f"+{LOG * (12 - LOG_TURN):,}")
    print(f"row 3 / row 2: {rows[2][2] / rows[1][2]:.2f}   row 3 / row 1: {rows[2][2] / rows[0][2]:.2f}")
