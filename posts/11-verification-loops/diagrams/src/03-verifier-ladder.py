"""Post 11, tests as ground truth: the verifier ladder, cheapest to dearest, with the line between fact and opinion.

Run from the series root:  uv run python posts/11-verification-loops/diagrams/src/03-verifier-ladder.py
Writes posts/11-verification-loops/diagrams/03-verifier-ladder.svg.
A hrn_fig_design.md section 3 form: a ruled table, the three verifiers that can gate an exit on their own shaded
gate (purple), the judge and self-critique unshaded below a dashed line. Every row is the post's own wording
(the list of section 2 and the self-critique of section 3), asserted against the body. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ["- **Schema validation.**", "- **A compiler or a type checker.**", "- **A test suite.**",
               "- **An independent judge.**", "From cheapest to dearest:", "It proves the *shape* of an answer",
               "skew positive", "first, cheap pass"]:
    assert phrase in BODY, phrase

ROWS = [
    ["verifier", "a pass proves", "cost", "can it be wrong?", "run it"],
    ["schema validation", "the result has the right shape", "near zero", "no", "each structured result"],
    ["compiler or type checker", "it builds; the types line up", "seconds", "only by false alarm", "every step"],
    ["test suite", "what the tests assert", "seconds to minutes", "no, unless flaky", "touched tests per step"],
    ["independent judge", "a rubric score: an opinion", "a model call", "yes", "at checkpoints"],
    ["self-critique", "the author's own opinion", "a model call", "yes; skews positive", "a first pass only"],
]
fig = Figure(
    "03-verifier-ladder", "Above the line a failure is a fact; below it, an opinion",
    "A table of five verifiers from cheapest to dearest, with what a pass proves, the cost, whether it can be wrong "
    "and when to run it. Schema validation: the result has the right shape, near zero, no, each structured result. "
    "Compiler or type checker: it builds and the types line up, seconds, only by false alarm, every step. Test "
    "suite: what the tests assert, seconds to minutes, no unless flaky, touched tests per step. These three are shaded "
    "purple. Below a dashed line, an independent judge: a rubric score, an opinion, a model call, yes, at "
    "checkpoints; and self-critique: the author's own opinion, a model call, yes and skews positive, a first pass "
    "only.",
    subtitle="Five verifiers, cheapest first; the shaded rows can gate the loop's exit on their own.",
    data_w=True)

X, Y, RH = 40, 120, 56
WIDTHS = [200, 224, 144, 152, 160]
assert sum(WIDTHS) == 880
fig.table(X, Y, ROWS, WIDTHS, row_h=RH, highlight_row={1: "gate", 2: "gate", 3: "gate"})
LINE = Y + 4 * RH
fig.edge((X, LINE), (X + sum(WIDTHS), LINE), color="ink-muted", width=1.5, dash="proj")
fig.caption("Reach for the cheapest deterministic check that covers the risk; escalate only when none will do.")
fig.write()
