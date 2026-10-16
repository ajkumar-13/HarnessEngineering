"""Post 22, section 10: the staged production funnel for two harnesses, one illustrative week.

Run from the series root:  uv run python posts/22-evaluating-harnesses/diagrams/src/03-production-funnel.py
Writes posts/22-evaluating-harnesses/diagrams/03-production-funnel.svg.
A section 3 form of hrn_fig_design.md: three neutral stages narrowing left to right (runs attempted, accepted,
shipped), with a gate (purple) on each arrow between them, human review and the later revert, each labelled with
the metric it yields. Every count, rate and dollar figure is computed here by importing snippets/funnel.py and
asserted against the body's table; the week is illustrative, and the figure says so.
"""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("funnel", POST / "snippets" / "funnel.py")
fn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fn)
with contextlib.redirect_stdout(io.StringIO()):
    out = fn.main()
WA, WB = fn.WEEK["A"], fn.WEEK["B (heavier verification)"]
A, B = out["A"], out["B (heavier verification)"]
for cell in (f"| {A['shipped']} | {B['shipped']} |", f"**${A['per_merged']:.2f}**", f"**${B['per_merged']:.2f}**",
             f"${A['human']:,.0f}", f"${B['human']:,.0f}", f"{A['escape']:.1%} escape", f"{B['escape']:.1%} escape"):
    assert cell in BODY, cell
pct = lambda v: f"{v:.0%}"  # noqa: E731

fig = Figure(
    "03-production-funnel", "B wins the first pass and loses the ledger",
    f"Three stages narrowing from left to right for one illustrative week of two harnesses: runs attempted, A "
    f"{WA['runs']} and B {WB['runs']}; results accepted without rework, A {WA['accepted']} and B {WB['accepted']}; "
    f"work shipped, A {A['shipped']} and B {B['shipped']}. A purple gate sits on each arrow: human review, giving "
    f"first-pass success of {pct(A['first_pass'])} against {pct(B['first_pass'])}, and the later revert, giving "
    f"defect escape of {A['escape']:.1%} against {B['escape']:.1%}. A ledger below: model spend ${A['model']:,.0f} "
    f"and ${B['model']:,.0f}, human time ${A['human']:,.0f} and ${B['human']:,.0f}, dollars per merged pull "
    f"request {A['per_merged']:.2f} for A and {B['per_merged']:.2f} for B. B's nine extra merges cost about 119 "
    f"dollars each.",
    subtitle="One illustrative week, 200 runs each; computed by snippets/funnel.py, human time at $120 an hour.",
    data_w=True)

MID = 220
STAGES = [(40, 200, 168, "runs attempted", WA["runs"], WB["runs"]),
          (360, 200, 136, "accepted", WA["accepted"], WB["accepted"]),
          (680, 240, 104, "shipped", A["shipped"], B["shipped"])]
for x, w, h, name, a, b in STAGES:
    y = MID - h // 2
    fig.card(x, y, w, h)
    fig.text(x + 16, MID - 20, name, "head")
    fig.text(x + 16, MID + 12, "A", "label")
    fig.text(x + w - 16, MID + 12, str(a), "value", anchor="end")
    fig.text(x + 16, MID + 40, "B", "label")
    fig.text(x + w - 16, MID + 40, str(b), "value", anchor="end")

GATES = [(300, "human review", "first-pass", f"{pct(A['first_pass'])} against {pct(B['first_pass'])}"),
         (620, "later revert", "defect escape", f"{A['escape']:.1%} against {B['escape']:.1%}")]
for gx, gate, metric, values in GATES:
    fig.arrow((gx - 60, MID), (gx + 60, MID))
    fig.fill(Box(gx - 4, MID - 32, 8, 64), "gate", radius=2)
    fig.text(gx, MID - 48, gate, "label", anchor="middle", color="gate-ink")
    fig.text(gx, MID + 96, metric, "note", anchor="middle")
    fig.text(gx, MID + 116, values, "label", anchor="middle")

rows = [["", "model spend", "human time", "shipped", "per merged PR"],
        ["A", f"${A['model']:,.0f}", f"${A['human']:,.0f}", str(A["shipped"]), f"${A['per_merged']:.2f}"],
        ["B, heavier verification", f"${B['model']:,.0f}", f"${B['human']:,.0f}", str(B["shipped"]),
         f"${B['per_merged']:.2f}"]]
fig.table(40, 368, rows, [232, 152, 152, 144, 200], col_align=["start", "end", "end", "end", "end"])

extra = (B["model"] + B["human"] - A["model"] - A["human"]) / (B["shipped"] - A["shipped"])
assert round(extra) == 119
fig.caption(f"B's {B['shipped'] - A['shipped']} extra merges cost ${extra:.0f} each, more than twice A's price per merge.")
fig.write()
