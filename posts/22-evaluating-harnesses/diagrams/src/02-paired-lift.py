"""Post 22, section 8: a real lift that sixty tasks call one time in four.

Run from the series root:  uv run python posts/22-evaluating-harnesses/diagrams/src/02-paired-lift.py
Writes posts/22-evaluating-harnesses/diagrams/02-paired-lift.svg.
Every plotted value is computed here by importing snippets/ab_runner.py and running it (its printed output is
discarded, after checking that the body quotes every line of it): the per-task paired differences, the lift, its
paired 95% t interval, the interval with runs treated as independent (the lift plus or minus 1.96 naive standard
errors), the stand-ins' true lift, and the share of fresh experiments that call the lift at 60 and at 312 tasks.
A section 5 chart of hrn_fig_design.md, marked "computed, illustrative": the two harnesses are neutral, so the
marks are ink; the true lift is ink-muted and named in words.
"""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure, num  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ab_runner", POST / "snippets" / "ab_runner.py")
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)
with contextlib.redirect_stdout(io.StringIO()) as out:
    r = ab.main()
for line in out.getvalue().splitlines():
    assert line in BODY, line                       # the body quotes the snippet's output verbatim

thirds = [round(v * ab.SEEDS) for v in r["d"]]     # B minus A, in seeds
counts = {k: thirds.count(k) for k in range(-3, 4)}
lift, low, high, truth = (round(v * 100, 1) for v in (r["lift"], r["low"], r["high"], r["truth"]))
n_low, n_high = (round((r["lift"] + s * ab.Z95 * r["naive"]) * 100, 1) for s in (-1, 1))
p60, pbig = (round(v * 100) for v in r["power"])
wins_a, wins_b = r["wins"]
assert (lift, low, high, truth, r["needed"], p60, pbig) == (6.7, -2.1, 15.5, 5.4, 312, 26, 81)
assert (wins_b, wins_a, counts[0]) == (23, 12, 25) and sum(counts.values()) == ab.TASKS

sign = lambda v: f"+{v}" if v > 0 else num(v)  # noqa: E731   a signed value with the true minus
LABEL = {-3: num(-1), -2: num(-2) + "/3", -1: num(-1) + "/3", 0: "0", 1: "+1/3", 2: "+2/3", 3: "+1"}
fig = Figure(
    "02-paired-lift", "A real 5.4-point lift that sixty tasks call one time in four",
    "Two panels computed by the post's A/B snippet, illustrative. Left, sixty tasks binned by harness B's "
    "resolved fraction minus harness A's over three seeds: "
    + ", ".join(f"{LABEL[k]}: {counts[k]}" for k in range(-3, 4))
    + f"; {wins_b} tasks favour B, {wins_a} favour A and {counts[0]} tie. Right, top: the measured lift of "
    f"{sign(lift)} points, printed beside its dot, with its paired 95 percent interval from {sign(low)} to {sign(high)}, crossing zero; the "
    f"same lift with runs treated as independent, interval {sign(n_low)} to {sign(n_high)}; and the true lift of "
    f"{sign(truth)} points the stand-ins were built with. Right, bottom: the share of 200 fresh experiments that "
    f"call the lift, {p60} percent at 60 tasks and {pbig} percent at {r['needed']} tasks.",
    subtitle="60 tasks, 3 seeds, the model held fixed; computed by snippets/ab_runner.py, illustrative.",
    height=720, data_w=True)

left, right = fig.row([5, 6])
body = fig.panel(left, "Per task: B minus A, of 3 seeds")
fig.bar_chart(Box(body.x, body.y, body.w, 392), [(LABEL[k], counts[k], "ink") for k in range(-3, 4)], 0, 30,
              [0, 10, 20, 30], label_w=64, value_w=40, axis_label="tasks")
fig.text(body.x, body.y + 452, f"{wins_b} favour B, {wins_a} favour A, {counts[0]} tie;", "note")
fig.text(body.x, body.y + 472, f"sign test p = {ab.sign_test(wins_a, wins_b):.2f}.", "note")

body = fig.panel(right, "Lift of B over A, in points")
ax = fig.dot_plot(Box(body.x, body.y, body.w, 232),
                  [("paired by task", [lift], ["ink"]), ("runs independent", [lift], ["ink"]),
                   ("true lift", [truth], ["ink-muted"])],
                  -10, 20, [-10, -5, 0, 5, 10, 15, 20], label_w=144, connect=None, fmt=lambda v: sign(int(v)),
                  ref_lines=[dict(x=0, label="no lift")])
with fig.data():
    for row, (a, b) in enumerate(((low, high), (n_low, n_high))):
        y0 = ax.sy(row)
        fig.edge((ax.sx(a), y0), (ax.sx(b), y0), color="ink", width=1.5)
        for v in (a, b):
            fig.edge((ax.sx(v), y0 - 8), (ax.sx(v), y0 + 8), color="ink", width=1.5)
    fig.text(ax.sx(truth) + 12, ax.sy(2) + 5, sign(truth), "value", color="ink-muted")
    fig.text(ax.sx(lift), ax.sy(0) - 16, sign(lift), "value", anchor="middle")

fig.text(body.x, body.y + 296, "Fresh experiments that call the lift", "head")
fig.bar_chart(Box(body.x, body.y + 312, body.w, 136),
              [(f"{ab.TASKS} tasks", p60, "ink"), (f"{r['needed']} tasks", pbig, "ink")], 0, 100,
              [0, 25, 50, 75, 100], label_w=144, value_w=56, fmt=lambda v: f"{int(v)}%")
fig.text(body.x, body.y + 492, f"Verdict at {ab.TASKS} tasks: not callable.", "note")

fig.caption("The interval, not the lift, carries the verdict: pair by task, then size the set before running it.")
fig.write()
