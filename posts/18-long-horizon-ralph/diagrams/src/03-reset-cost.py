"""Post 18, section 4: the frozen prefix's cost over fifty resets, by cache tier and gap, re-entry alone and with calls.

Run from the series root:  uv run python posts/18-long-horizon-ralph/diagrams/src/03-reset-cost.py
Writes posts/18-long-horizon-ralph/diagrams/03-reset-cost.svg.
Every bar is computed by importing snippets/reset_cost.py (Claude Sonnet 4.6 at $3 per million input tokens, cache
writes 1.25x and 2x, reads 0.1x, Anthropic pricing and prompt-caching pages consulted October 2026) and asserted
against the table the post quotes. The prefix size, iteration count and calls per iteration are illustrative, as
the subtitle says. The cold row, a write on every re-entry, is the error (red); the other rows are ink.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("reset_cost", POST / "snippets" / "reset_cost.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

rows = rc.table()
reentry = [round(r[2][0], 2) for r in rows]
inside = [round(r[3][0], 2) for r in rows]
assert reentry == [1.80, 0.22, 2.25, 0.25] and inside == [36.00, 3.64, 5.67, 3.67]
assert (rc.PREFIX, rc.ITERS, rc.CALLS) == (12_000, 50, 20)
for v in reentry + inside:
    assert f"${v:.2f}" in BODY, v

LABELS = ["no cache", "five-minute tier, warm", "five-minute tier, cold", "one-hour tier"]
COLORS = ["ink-muted", "ink", "error", "ink"]
money = lambda v: f"${v:.2f}"  # noqa: E731

fig = Figure(
    "03-reset-cost", "A cold re-entry pays a write and collects no read",
    "Two computed bar charts of what a 12,000-token frozen prefix costs over 50 iterations at $3 per million input "
    "tokens. Left, the re-entry call of each iteration only: no cache $1.80; five-minute tier with reads under five "
    "minutes apart, warm, $0.22; five-minute tier with about eight minutes between reads, cold, $2.25, in red; "
    "one-hour tier $0.25. Right, with 20 calls inside each iteration: $36.00, $3.64, $5.67 and $3.67.",
    subtitle="Computed by snippets/reset_cost.py at Claude Sonnet 4.6's rate (October 2026); sizes illustrative.",
    data_w=True)

left, right = fig.row([3, 2])
body = fig.panel(left, "Re-entry call only")
fig.bar_chart(body, [(l, v, c) for l, v, c in zip(LABELS, reentry, COLORS)], 0, 2.5, [0, 1, 2],
              label_w=176, value_w=64, fmt_tick=lambda v: f"${v:g}", fmt_value=money,
              axis_label="dollars over 50 iterations")
body = fig.panel(right, "With 20 calls inside")
fig.bar_chart(body, [("", v, c) for v, c in zip(inside, COLORS)], 0, 40, [0, 20, 40],
              label_w=16, value_w=72, fmt_tick=lambda v: f"${v:g}", fmt_value=money,
              axis_label="dollars over 50 iterations")

fig.caption("Cold means more than five minutes since the last read; the one-hour tier stays warm for one 2x write.")
fig.write()
