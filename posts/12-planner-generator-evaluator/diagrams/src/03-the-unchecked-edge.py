"""Post 12, section 8: the edge nothing checks, the contract against the task, and where the missing check goes.

Run from the series root:  uv run python posts/12-planner-generator-evaluator/diagrams/src/03-the-unchecked-edge.py
Writes posts/12-planner-generator-evaluator/diagrams/03-the-unchecked-edge.svg.
A section 3 form of hrn_fig_design.md: the pipeline as five cards (the task neutral, the planner's output blue, the
contract state green, the generator act orange, the evaluator a purple gate), a purple bracket for the edge the
evaluator checks, a red bracket for the edge nothing checks, and the human as a neutral card whose approval is a
gate on the contract. The example gap is the snippet's own: no criterion of its contract mentions a negative
amount, asserted below. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure  # noqa: E402
import three_roles as tr  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
kept, _ = tr.review(tr.plan(tr.TASK))
assert not any("negative" in c.text for c in kept)
for phrase in ("nothing in it says what `parse()` should do with a negative amount",
               "**A human reads the contract, not the work.**",
               "nothing checks the contract against the task"):
    assert phrase in BODY, phrase

fig = Figure(
    "03-the-unchecked-edge", "The evaluator checks the work; nothing checks the contract",
    "Five cards in a row: the task, the planner, the contract, the generator and the evaluator. A purple bracket "
    "below, from the contract to the evaluator, is labelled checked: the evaluator grades the work against the "
    "contract. A red bracket above, from the task to the contract, is labelled not checked: nothing grades the "
    "contract against the task. Below the contract, a human card with a purple approval arrow up to the contract: "
    "a person reads the criteria, the one point where a missing requirement is still cheap to add. A note gives "
    "the example from this post's run: no criterion says what parse() does with a negative amount.",
    subtitle="A planner's missing requirement passes every gate downstream of it.",
    data_w=True)

W, GAP, Y, H = 144, 40, 168, 64
CARDS = [("task", None), ("planner", "model"), ("contract", "state"), ("generator", "act"), ("evaluator", "gate")]
boxes = []
for i, (name, role) in enumerate(CARDS):
    x = 40 + i * (W + GAP)
    boxes.append(fig.card(x, Y, W, H, color=role))
    fig.text(x + W // 2, Y + 38, name, "head", anchor="middle", color=role)
for i in range(4):
    x0 = 40 + i * (W + GAP) + W
    fig.arrow((x0, Y + H // 2), (x0 + GAP, Y + H // 2))


def centre(i):
    return 40 + i * (W + GAP) + W // 2


fig.brace(centre(0), centre(2), Y - 16, label="not checked: the contract against the task", side="above",
          kind="bracket", color="error")
fig.brace(centre(2), centre(4), Y + H + 16, label="checked: the work against the contract", side="below",
          kind="bracket", color="gate")

# the missing check: a person reads the contract
HX, HY, HW = 304, 320, 288
fig.card(HX, HY, HW, 72)
fig.text(HX + 16, HY + 30, "human", "head")
fig.text(HX + 16, HY + 56, "reads the criteria, not the work", "label")
fig.arrow((432, HY), (432, Y + H), label="approval", side="right", color="gate")
fig.text(40, 432, "Example from this post's run: no criterion says what parse() does with a negative amount,",
         "note")
fig.text(40, 456, "so no attempt is checked for it, and PASS would still be honest about the contract.", "note")

fig.caption("Every check pushes trust somewhere else; here it lands on the contract.")
fig.write()
