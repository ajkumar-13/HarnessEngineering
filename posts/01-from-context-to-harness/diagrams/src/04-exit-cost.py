"""Post 01, section 6: the running token total of one stuck run, and where each exit would stop it.

Run from the series root:  uv run python posts/01-from-context-to-harness/diagrams/src/04-exit-cost.py
Writes posts/01-from-context-to-harness/diagrams/04-exit-cost.svg.
Every plotted value is computed by the post's snippets: the curve is run_loop() of snippets/harness_loop.py
against its scripted doom loop with the cap set to 1, 2, ... 12 (the total each shorter run pays is the running
total after that turn), and the three exit marks are the rows snippets/exit_cost.py prints. The sizes are
illustrative, so the curve is dashed and labelled "illustrative" (hrn_fig_design.md section 5); the exits are
gates, so their marks are gate-coloured diamonds.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
from harness_loop import ScriptedModel, run_loop  # noqa: E402
from exit_cost import table  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
TASK = "Fix the failing test in app.py."
turns = list(range(1, 13))
totals = []
for k in turns:
    r = run_loop(ScriptedModel(), TASK, max_iters=k)
    totals.append(r["read"] + r["written"])
rows = {fired: (turn, total) for _, fired, turn, _, _, total in table()}
assert totals[0] == 4_400 and totals[-1] == 132_000
assert rows == {"max_iters": (12, 132_000), "budget": (6, 44_400), "no_progress": (5, 34_000)}
assert totals[4] == 34_000 and totals[5] == 44_400          # each exit's total lies on the curve
for phrase in ("from 4,400 on turn 1 to 132,000 on turn 12", "no progress on turn 5 at 34,000",
               "the budget on turn 6 at 44,400", "token budget of 40,000", "illustrative sizes, not measurements"):
    assert phrase in BODY, phrase


def fmt(v):
    return f"{v:,.0f}"


fig = Figure(
    "04-exit-cost", "The later the exit fires, the more the stuck run costs",
    "A line chart of cumulative tokens, read plus written, against turn for one scripted doom loop with "
    "illustrative sizes. The curve is dashed and bends upward from 4,400 tokens on turn 1 to 132,000 on turn 12. "
    "Three gate-coloured diamonds mark where each exit stops the run: no progress, window of 3, on turn 5 at "
    "34,000 tokens; the 40,000-token budget on turn 6 at 44,400; the iteration cap of 12 on turn 12 at 132,000. "
    "A dotted line marks the 40,000-token budget. Values computed by the post's snippets.",
    subtitle="One scripted doom loop, illustrative sizes. Computed by snippets/harness_loop.py and exit_cost.py.",
    data_w=True)

body = fig.panel(fig.row(1)[0])
ax = fig.line_chart(
    body,
    [dict(xs=turns, ys=totals, color="ink", dash="proj", label=None, points=False)],
    x=(0, 12, [0, 2, 4, 6, 8, 10, 12]), y=(0, 140_000, [0, 40_000, 80_000, 120_000]),
    x_label="turn", y_label="tokens, running total", fmt_x=lambda v: f"{v:g}", fmt_y=fmt,
    ref_lines=[dict(y=40_000, label="budget", at="left")])
MARKS = [("no_progress", "no progress: 34,000", "end", -10, -26),
         ("budget", "budget: 44,400", "start", 14, 24),
         ("max_iters", "cap of 12: 132,000", "end", -14, 5)]
for fired, label, anchor, dx, dy in MARKS:
    turn, total = rows[fired]
    ax.point(turn, total, "diamond", "gate", size=10)
    ax.text(turn, total, label, "value", anchor=anchor, color="gate", dx=dx, dy=dy)
fig.legend(body, [dict(color="ink", label="illustrative total", mark="dash"),
                  dict(color="gate", label="an exit fires", mark="diamond")], direction="row")
fig.write()
