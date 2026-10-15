"""Post 11, the economics of an unverified run: the same error with no gate and with a gate on every step.

Run from the series root:  uv run python posts/11-verification-loops/diagrams/src/02-compounding-vs-failfast.py
Writes posts/11-verification-loops/diagrams/02-compounding-vs-failfast.svg.
Every plotted value is computed here by importing snippets/unverified_cost.py, which builds post 23's illustrative
twelve-iteration run (6,000 input tokens on the first request, 3,100 more on each turn); the values are asserted
against the snippet output the body quotes. Marked "computed, illustrative": a model of a run, not a measurement.
Roles: forfeited tokens are error (red); the run itself is ink.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, num  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("unverified_cost", POST / "snippets" / "unverified_cost.py")
cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost)

tokens = cost.tokens
total = cost.run_total()
no_gate = cost.forfeited(cost.ITERATIONS)
gate = cost.forfeited(cost.ERROR_AT)
judge_all, judge_three = cost.ITERATIONS * cost.JUDGE_READS, cost.CHECKPOINTS * cost.JUDGE_READS
assert (tokens[0], tokens[-1], total, no_gate, gate) == (6_000, 40_100, 276_600, 270_600, 9_100)
assert (judge_all, judge_three) == (144_000, 36_000)
for phrase in ["run total: 276,600", "270,600 tokens (97.8%)", "9,100 tokens (3.3%)",
               "= 144,000 tokens (+52.1%)", "= 36,000 tokens (+13.0%)", "6,000, 9,100, 12,200"]:
    assert phrase in BODY, phrase

fig = Figure(
    "02-compounding-vs-failfast", "Without a gate, one early error costs 98% of the run",
    "Two panels computed by the post's snippet on post 23's illustrative twelve-iteration run. Left, input tokens "
    "per iteration rise in a straight line from 6,000 at iteration 1 to 40,100 at iteration 12, with a reference "
    "line where the error enters, at iteration 2, and iterations 2 to 12 shaded red as forfeit without a gate. Right, input tokens forfeit on one scale: with no gate, caught at "
    "iteration 12, 270,600 of the run's 276,600; with a gate on every step, caught at iteration 2, 9,100.",
    subtitle="Computed by snippets/unverified_cost.py on post 23's running example; illustrative, not measured.",
    data_w=True)

left, right = fig.row(2)
body = fig.panel(left, "Input tokens per iteration")
ks = list(range(1, cost.ITERATIONS + 1))
ax = fig.line_chart(
    body, [dict(xs=ks, ys=tokens, color="ink", label=None, shape="circle")],
    x=(1, 12, [1, 4, 8, 12]), y=(0, 45_000, [0, 15_000, 30_000, 45_000]),
    x_label="iteration", y_label="input tokens", label_w=16,
    bands=[(cost.ERROR_AT, cost.ITERATIONS, "error")], ref_lines=[dict(x=cost.ERROR_AT, label="error enters")])
ax.text(7, 3_000, "forfeit without a gate", "label", anchor="middle", color="error")

body = fig.panel(right, "Input tokens forfeit")
fig.bar_chart(
    body, [("no gate", no_gate, "error"), ("gate on every step", gate, "error")],
    0, 300_000, [0, 100_000, 200_000, 300_000], label_w=136, value_w=72, axis_label="tokens",
    fmt=lambda v: num(v), ref_lines=[dict(x=total, label=f"whole run, {num(total)}")])

fig.caption(f"A judge on every step would add {num(judge_all)} tokens; at three checkpoints, {num(judge_three)}.")
fig.write()
