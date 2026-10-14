"""Post 04, section 9: a harness fix is paid once, a model upgrade on every run, so the upgrade's cost crosses it.

Run from the series root:  uv run python posts/04-harness-beats-model/diagrams/src/04-buy-once-rent-forever.py
Writes posts/04-harness-beats-model/diagrams/04-buy-once-rent-forever.svg.
Every plotted value is computed by the post's snippet snippets/upgrade_cost.py (cumulative() and
break_even_runs()) from its illustrative sizes, so both lines are dashed and labelled "illustrative"
(hrn_fig_design.md section 5). The upgrade is the model's cost, blue (model); the harness fix is ink.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
from upgrade_cost import FIX_IN_RUNS, PRICE_MULTIPLE, RUNS_PER_DAY, break_even_runs, cumulative  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
runs = list(range(0, 1_001, 100))
fix = [cumulative(n)[0] for n in runs]
upgrade = [cumulative(n)[1] for n in runs]
cross = break_even_runs()
assert cross == 500 and cumulative(cross) == (1_000, 1_000) and upgrade[-1] == 2_000
assert (PRICE_MULTIPLE, FIX_IN_RUNS, RUNS_PER_DAY) == (3, 1_000, 200)
for phrase in ("an extra $2C$ on every run", "worth 1,000 runs at today's price",
               "break-even after 500 runs, 2.5 days at 200 runs a day", "$1{,}000 / 2 = 500$ runs",
               "All of these sizes are illustrative"):
    assert phrase in BODY, phrase


def fmt(v):
    return f"{v:,.0f}"


fig = Figure(
    "04-buy-once-rent-forever", "A fix is paid once; an upgrade is paid on every run",
    "A line chart of extra spend, in units of C, one run's price today, against the number of runs from 0 to "
    "1,000, with illustrative sizes. The harness fix is a flat dashed ink line at 1,000, paid once. The model upgrade, "
    "which triples the price per token, is a dashed blue line rising by 2 a run from 0 to 2,000. They cross at 500 "
    "runs, marked, which is 2.5 days at 200 runs a day. Computed by snippets/upgrade_cost.py.",
    subtitle="Extra spend in units of C, one run's price today. Illustrative sizes, from snippets/upgrade_cost.py.",
    data_w=True)

body = fig.panel(fig.row(1)[0])
ax = fig.line_chart(
    body,
    [dict(xs=runs, ys=fix, color="ink", dash="proj", label="harness fix", points=False),
     dict(xs=runs, ys=upgrade, color="model", dash="proj", label="model upgrade", points=False)],
    x=(0, 1_000, [0, 250, 500, 750, 1_000]), y=(0, 2_000, [0, 500, 1_000, 1_500, 2_000]),
    x_label="runs", y_label="extra spend, in units of C", fmt_x=fmt, fmt_y=fmt, label_w=136)
ax.point(cross, FIX_IN_RUNS, "diamond", "ink", size=10)
ax.text(cross, FIX_IN_RUNS, f"break-even: {cross:,.0f} runs", "value", dx=14, dy=28)
ax.text(cross, FIX_IN_RUNS, f"{cross / RUNS_PER_DAY:g} days at {RUNS_PER_DAY} runs a day", "note", dx=14, dy=48)
fig.legend(ax.x + 24, ax.y + 24, [dict(color="ink", label="illustrative sizes", mark="dash")], direction="row")
fig.caption("A constant against a rate: real numbers move the crossing, never the shape.")
fig.write()
