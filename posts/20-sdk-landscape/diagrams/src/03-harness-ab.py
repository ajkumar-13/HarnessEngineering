"""Post 20, section 7: the small A/B that does not settle the choice.

Run from the series root:  uv run python posts/20-sdk-landscape/diagrams/src/03-harness-ab.py
Writes posts/20-sdk-landscape/diagrams/03-harness-ab.svg.
Every plotted value is computed here by importing snippets/harness_ab.py and running it (its printed output is
discarded): the per-task resolved counts of both arms, the lift, its paired 95% interval, the stand-in's true lift and
the task count for 80% power. The values are asserted against the snippet output the body quotes. Marked "computed,
illustrative" on the figure: a model of an experiment, not a measurement. Roles: the two harnesses are neutral, so
the marks are ink; the measured lift is ink and the true lift ink-muted, named in words beside each.
"""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, num  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("harness_ab", POST / "snippets" / "harness_ab.py")
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)
with contextlib.redirect_stdout(io.StringIO()) as out:
    r = ab.main()
printed = out.getvalue()
for line in printed.splitlines():
    assert line in BODY, line                       # the body quotes the snippet's output verbatim

diffs = [b - a for a, b in zip(r["per_task"]["A"], r["per_task"]["B"])]
lift, low, high, truth = (round(v * 100, 1) for v in (r["lift"], r["low"], r["high"], r["truth"]))
assert (lift, low, high, truth, r["needed"]) == (1.0, -8.3, 10.3, 6.2, 83)
assert (sum(d > 0 for d in diffs), sum(d < 0 for d in diffs), sum(d == 0 for d in diffs)) == (5, 5, 10)
solved = {arm: sum(r["per_task"][arm]) for arm in "AB"}
assert solved == {"A": 66, "B": 67}

sign = lambda v: f"+{v}" if v > 0 else num(v)  # noqa: E731   a signed value with the true minus
fig = Figure(
    "03-harness-ab", "A real lift of 6.2 points, measured as 1.0",
    "Two panels computed by the post's A/B snippet, illustrative. Left, twenty tasks as rows, each a dot at harness "
    "B's resolved count minus harness A's, out of five seeds, on an axis from minus 3 to plus 3 with a line at no "
    f"difference: {', '.join(f't{i:02d} {sign(d)}' for i, d in enumerate(diffs))}; five rows favour B, five favour A "
    f"and ten tie. Right, the measured lift of {sign(lift)} points with its 95 percent interval from {sign(low)} to "
    f"{sign(high)} points, crossing zero, and the true lift of {sign(truth)} points the stand-in was built with. "
    f"Below: A resolved {solved['A']} of 100 runs and B {solved['B']}; about {r['needed']} tasks would detect the "
    "true lift four times in five.",
    subtitle="Twenty tasks, five seeds each, one model held fixed; computed by snippets/harness_ab.py, illustrative.",
    height=720, data_w=True)

left, right = fig.row([1, 1])
body = fig.panel(left, "Per task: B minus A, resolved of 5")
fig.dot_plot(body, [(f"t{i:02d}", [d]) for i, d in enumerate(diffs)], -3, 3, [-3, -2, -1, 0, 1, 2, 3],
             colors=("ink",), shapes=("circle",), label_w=48, connect=None, fmt=lambda v: sign(int(v)),
             ref_lines=[dict(x=0, label="no difference")], axis_label="resolved by B minus resolved by A")

body = fig.panel(right, "Lift of B over A, in points")
top = body.__class__(body.x, body.y, body.w, 216)
ax = fig.dot_plot(top, [("measured lift", [lift], ["ink"]), ("true lift", [truth], ["ink-muted"])], -15, 15,
                  [-15, -10, -5, 0, 5, 10, 15], label_w=112, connect=None, fmt=lambda v: sign(int(v)),
                  ref_lines=[dict(x=0, label="no lift")])
y0 = ax.sy(0)
with fig.data():
    fig.edge((ax.sx(low), y0), (ax.sx(high), y0), color="ink", width=1.5)
    for v in (low, high):
        fig.edge((ax.sx(v), y0 - 8), (ax.sx(v), y0 + 8), color="ink", width=1.5)
    fig.text(ax.sx(truth) + 12, ax.sy(1) + 5, sign(truth), "value", color="ink-muted")

rows = [["", "A", "B"],
        ["resolved, of 100 runs", str(solved["A"]), str(solved["B"])],
        ["cost per resolved task", "$0.00260", "$0.00286"],
        ["simulated seconds per run", "4.1", "4.5"]]
for cell in ("$0.00260", "$0.00286", "4.1", "4.5"):
    assert cell in BODY, cell
fig.table(body.x, body.y + 248, rows, [232, 96, 96], col_align=["start", "end", "end"])
fig.text(body.x, body.y + 408, f"Measured {sign(lift)}, 95% interval {sign(low)} to {sign(high)};", "note")
fig.text(body.x, body.y + 428, "the true lift is set by the stand-in's definition.", "note")
fig.text(body.x, body.y + 456, "Sign test on the ten discordant tasks: p = 1.00.", "note")
fig.text(body.x, body.y + 484, f"About {r['needed']} tasks would detect the true lift", "note")
fig.text(body.x, body.y + 504, "four times in five.", "note")

fig.caption("Every A-only win on the left is noise: the stand-in makes B at least as good on every task.")
fig.write()
