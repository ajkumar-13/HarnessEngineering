"""Post 18, section 8: the honest run of the driver, window by window and commit by commit.

Run from the series root:  uv run python posts/18-long-horizon-ralph/diagrams/src/04-multi-context-run.py
Writes posts/18-long-horizon-ralph/diagrams/04-multi-context-run.svg.
Every plotted value is computed here by running snippets/ralph_driver.py's honest scenario (a fresh process per
iteration in a temporary git repository): per iteration, the tokens of the context at re-entry and at the end of
the iteration, the commit count from git rev-list, and the criteria the gate passed. The single-context line is the
snippet's own sum: the frozen prefix once plus every iteration's volatile part and work. The token counts are the
toy's tiktoken counts, so the subtitle says illustrative. The Ralph windows are ink, the single context muted and
dashed; commits are act (orange), criteria passing the gate (purple).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import ralph_driver as rd  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
rows, it, reason = rd.scenario("honest", quiet=True)
assert (it, reason) == (4, "completed")
F = rows[0]["frozen"]
starts = [F + r["volatile"] for r in rows]
ends = [F + r["volatile"] + r["work"] for r in rows]
single = [F]
for r in rows:
    single.append(single[-1] + r["volatile"] + r["work"])
commits = [1] + [r["total"] for r in rows]
passing = [0] + [r["passing"] for r in rows]
assert starts == [236, 315, 338, 345] and ends == [307, 401, 423, 449] and single[-1] == 956
assert commits == [1, 2, 3, 4, 5] and passing == [0, 1, 1, 2, 3]
for s, e in zip(starts, ends):
    assert f"= {s} -> {e}" in BODY, (s, e)
assert "one context carrying all 4 iterations: 956 tokens" in BODY

def steps(vals):
    xs, ys = [0], [vals[0]]
    for k, v in enumerate(vals[1:], start=1):
        xs += [k, k]
        ys += [ys[-1], v]
    return xs, ys


fig = Figure(
    "04-multi-context-run", "The window resets; the work only climbs",
    "Two computed charts of the snippet's honest run over four iterations. Top, tokens in the window: each iteration "
    f"rises from its re-entry context, {starts[0]}, {starts[1]}, {starts[2]} and {starts[3]} tokens, to its end, "
    f"{ends[0]}, {ends[1]}, {ends[2]} and {ends[3]}, and the window is discarded at the reset; a dotted line marks "
    f"the {F}-token frozen prefix every re-entry starts from; a dashed muted line shows one context carrying every iteration, growing to {single[-1]}. Bottom, "
    "two staircases: commits rise by one every iteration from 1 to 5, while criteria passing the gate go 0, 1, 1, 2, 3, "
    "flat at iteration 2 where the agent's claim failed the gate.",
    subtitle="Computed by snippets/ralph_driver.py, a toy build of three criteria; token counts are illustrative.",
    height=720, data_w=True)

top = fig.panel(Box(40, 128, 880, 260), "Tokens in the window, one fresh window per iteration")
teeth = [dict(xs=[k, k + 1], ys=[s, e], color="ink", points=False, label=None)
         for k, (s, e) in enumerate(zip(starts, ends))]
ax = fig.line_chart(
    top, [dict(xs=list(range(5)), ys=single, color="ink-muted", dash="proj", points=False, label=None)] + teeth,
    x=(0, 4, [0, 1, 2, 3, 4]), y=(0, 1000, [0, 250, 500, 750, 1000]),
    x_label="iterations completed", y_label="tokens", fmt_x=lambda v: f"{v:g}", fmt_y=lambda v: f"{v:,.0f}",
    label_w=176, ref_lines=[dict(y=F, label=f"frozen prefix, {F}", at="right")])
for k, s in enumerate(starts):
    ax.point(k, s, "circle", "ink", size=8)
ax.text(4, single[-1], f"one context: {single[-1]}", "label", dx=8, dy=5)
ax.text(4, ends[-1], f"Ralph window: {ends[-1]}", "label", dx=8, dy=5)
ax.text(2, 120, "each dot is a new window at re-entry", "note", anchor="middle", dy=5)

bottom = fig.panel(Box(40, 448, 880, 200), "On disk")
cx, cy = steps(commits)
px, py = steps(passing)
ax2 = fig.line_chart(
    bottom, [dict(xs=cx, ys=cy, color="act", points=False, label=None),
             dict(xs=px, ys=py, color="gate", points=False, label=None)],
    x=(0, 4, [0, 1, 2, 3, 4]), y=(0, 5, [0, 1, 2, 3, 4, 5]),
    x_label="iterations completed", y_label="count", fmt_x=lambda v: f"{v:g}", fmt_y=lambda v: f"{v:g}",
    label_w=176)
ax2.text(4, commits[-1], f"commits: {commits[-1]}", "label", color="act", dx=8, dy=5)
ax2.text(4, passing[-1], f"criteria passing: {passing[-1]}", "label", color="gate", dx=8, dy=5)
ax2.text(2, 0.5, "claim failed the gate", "note", anchor="middle", dy=5, color="gate")

fig.caption("A commit is not progress until the gate agrees: at iteration 2 commits rise and passes do not.")
fig.write()
