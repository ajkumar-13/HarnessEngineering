"""Post 15, section 3: the anatomy of an approval gate, two halves, four outcomes, one record.

Run from the series root:  uv run python posts/15-human-in-the-loop/diagrams/src/03-anatomy-of-a-gate.py
Writes posts/15-human-in-the-loop/diagrams/03-anatomy-of-a-gate.svg.
A boundary-and-gate form (hrn_fig_design.md section 3). The policy and the decider are the companion's
ApprovalGate.needs_approval and its Decider (code/25-harness-plus/src/harness_plus/approval.py, read here and
asserted); the no-answer defaults are section 8's and the snippet's; the five record fields are section 10's.
Roles: the tool call and the outcomes that run are orange (act), the policy, the decider and the no-answer default
are purple (gates), a denial is red, the record is green (state). No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
ROOT = POST.parents[1]
BODY = (POST / "index.md").read_text(encoding="utf-8")
APPROVAL = (ROOT / "code" / "25-harness-plus" / "src" / "harness_plus" / "approval.py").read_text(encoding="utf-8")
for phrase in ("def needs_approval(self, tool_name: str, sensitive: bool, args: dict) -> bool:",
               "Decider = Callable[[str, dict, str], bool]",
               'return False, f"denied by approver: {reason}"'):
    assert phrase in APPROVAL, phrase
for phrase in (
    "`needs_approval` is a **policy**: code that decides which calls are gated",
    "The **decider** returns the verdict: a human, or something standing in for one",
    "For anything irreversible the default on expiry is **deny**",
    "For a reversible action the default can be to proceed and note that nobody looked",
    "Every decision should record the call and its arguments, why it was gated, who decided, what they decided, "
    "and how long the request sat",
    "`Result.denied` is a list of tool-and-message pairs",
):
    assert phrase in BODY, phrase

fig = Figure(
    "03-anatomy-of-a-gate", "Two halves, four outcomes, one record",
    "A tool call goes to the policy, needs_approval, ordinary code that decides which calls are gated. A call it "
    "does not gate runs. A gated call goes to the decider: a human, a classifier, or a stub in a test. Three "
    "outcomes leave the decider: approved, the call runs; denied, the reason returns to the agent as an "
    "observation; no answer, the call is denied if it is irreversible and runs with a note if it is reversible. "
    "Under all of it, the record each decision leaves: the call and its arguments, why it was gated, who decided, "
    "the verdict, and how long it waited.",
    subtitle="The policy is code a test can assert against; the decider is a seam a test can stub.",
    data_w=True)

# the call
call = fig.card(40, 128, 160, 64, color="act")
fig.text(56, 156, "a tool call", "head", color="act")
fig.text(56, 180, "deploy production", "label")

# the policy, then the decider
PX, PW = 240, 200
fig.card(PX, 112, PW, 96, color="gate")
fig.text(PX + 16, 140, "policy", "head", color="gate")
fig.text(PX + 16, 164, "needs_approval", "code")
fig.text(PX + 16, 188, "code: which calls wait", "note")
fig.card(PX, 264, PW, 96, color="gate")
fig.text(PX + 16, 292, "decider", "head", color="gate")
fig.text(PX + 16, 316, "a human, a classifier,", "label")
fig.text(PX + 16, 340, "or a stub in a test", "label")

fig.arrow((200, 160), (PX, 160))
fig.arrow((PX + PW // 2, 208), (PX + PW // 2, 264), label="gated", side="right")

# the four outcomes
OX, OW, OH = 528, 392, 48
OUT = [
    (112, "act", "not gated", "the call runs"),
    (176, "act", "approved", "the call runs"),
    (240, "error", "denied", "the reason returns as an observation"),
    (304, "gate", "no answer", "irreversible: deny; reversible: run, noted"),
]
for y, role, head, line in OUT:
    fig.card(OX, y, OW, OH, color=role)
    fig.text(OX + 16, y + 30, head, "head", color=role)
    fig.text(OX + 120, y + 30, line, "label")
fig.arrow((PX + PW, 136), (OX, 136))
for y in (176, 240, 304):
    fig.arrow((PX + PW, 312), (OX, y + OH // 2))

# the record
fig.card(40, 400, 880, 72, color="state")
fig.text(56, 428, "the record of every decision", "head", color="state")
fig.text(56, 452, "the call and its arguments, why it was gated, who decided, the verdict, how long it waited",
         "label")

fig.caption("The companion's Result keeps only a (tool, message) pair, and only for refused calls.")
fig.write()
