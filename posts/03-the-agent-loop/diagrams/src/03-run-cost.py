"""Post 03, section 8: the input tokens three runs re-read, turn by turn, under the same cap of 12.

Run from the series root:  uv run python posts/03-the-agent-loop/diagrams/src/03-run-cost.py
Writes posts/03-the-agent-loop/diagrams/03-run-cost.svg.
Every plotted value comes from snippets/run_cost.py: the running sum of inputs() for each run, and the totals and
dollars of table(). The sizes are illustrative (the series' running example), so every curve is dashed and the
subtitle says "illustrative" (hrn_fig_design.md section 5); the $3 per million rate is cited in the post. The three
runs are one neutral quantity, told apart by marker shape and a direct label, not by colour.
"""
import sys
from itertools import accumulate
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
from run_cost import LOG_TURN, RUNS, inputs, table  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
rows = table()
assert [(t, total, round(d, 2)) for _, t, total, d in rows] == [(6, 82_500, 0.25), (12, 276_600, 0.83),
                                                                (12, 416_600, 1.25)]
for phrase in ("answering at iteration 6 stops at 82,500", "reaches 276,600", "reaches 416,600",
               "at 3 dollars per million input tokens, the Claude Sonnet 4.6 input rate", "illustrative sizes"):
    assert phrase in BODY, phrase


def fmt(v):
    return f"{v:,.0f}"


fig = Figure(
    "03-run-cost", "The same cap of 12 covers a five-fold spread in the bill",
    "A line chart of input tokens re-read, as a running total, against turn, for three illustrative runs of one task "
    "under an iteration cap of 12, every curve dashed and ended by a hollow mark. The run that answers at iteration 6, a circle, ends at 82,500 "
    "tokens, $0.25. The run to the cap, a square, ends at 276,600, $0.83. The run to the cap with a 20,000-token log "
    "read at turn 5, a diamond, follows it to turn 5 and then pulls away, ending at 416,600, $1.25. A dotted line marks "
    "turn 5. Dollars at $3 per million input tokens.",
    subtitle="Illustrative sizes from snippets/run_cost.py; $3 per million input tokens (Claude Sonnet 4.6), October 2026.",
    data_w=True)

SHAPES = ["circle", "square", "diamond"]
series = []
for (label, turns, log), shape in zip(RUNS, SHAPES):
    xs = list(range(1, turns + 1))
    series.append(dict(xs=xs, ys=list(accumulate(inputs(turns, log))), color="ink", dash="proj", label=None,
                       points=False))
full = fig.panel(fig.row(1)[0])
body = Box(full.x, full.y, full.w - 232, full.h)         # room on the right for the three end labels
ax = fig.line_chart(
    body, series, x=(0, 12, [0, 2, 4, 6, 8, 10, 12]), y=(0, 450_000, [0, 150_000, 300_000, 450_000]),
    x_label="turn", y_label="input tokens re-read, running total", fmt_x=lambda v: f"{v:g}", fmt_y=fmt,
    ref_lines=[dict(x=LOG_TURN, label="20,000-token log read")])
NAMES = ["answers at iteration 6", "runs to the cap", "to the cap, with the log"]
for (_, turns, total, dollars), name, shape, (dx, dy) in zip(rows, NAMES, SHAPES, [(8, 28), (12, 5), (12, 5)]):
    ax.point(turns, total, shape, "ink", size=10, hollow=True)
    ax.text(turns, total, f"{name}: {fmt(total)}, ${dollars:.2f}", "value", dx=dx, dy=dy)
fig.caption("Every turn re-reads the turns before it, so one large observation is paid for on every later turn.")
fig.write()
