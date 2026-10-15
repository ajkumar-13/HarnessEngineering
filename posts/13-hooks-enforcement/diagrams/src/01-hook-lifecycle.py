"""Post 13, the hero: the loop of post 03 with the four hook points attached, the two that can block as gates.

Run from the series root:  uv run python posts/13-hooks-enforcement/diagrams/src/01-hook-lifecycle.py
Writes posts/13-hooks-enforcement/diagrams/01-hook-lifecycle.svg.
hrn_fig_design.md section 1 (reason blue, act orange, observe green) with section 3's marks on the arrows: a
gate-coloured diamond where a hook can block, a rule-grey square where it can only supply or report. The four
points and what each can do are section 2's bullets, asserted against the body; there are no numbers to source.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("- **Session start.**", "It cannot block; it *supplies*.", "- **Pre-tool.**", "can **block** it",
               "- **Post-edit.**", "it can only report", "- **Pre-commit.**", "one layer below the agent",
               "Two of the four can block"):
    assert phrase in BODY, phrase

fig = Figure(
    "01-hook-lifecycle", "Only the two points in front of an action can block",
    "The agent loop as three cards: reason, the model call, in blue; act, a tool runs, in orange; observe, results "
    "return, in green; arrows run reason to act, act to observe, and observe back to reason for the next turn, "
    "inside a frame labelled the loop. A green memory file card outside the frame feeds reason through a grey "
    "square marked session start, supplies. On the arrow from reason to act a purple diamond marks pre-tool, "
    "blocks the call. On the arrow from act to observe a grey square marks post-edit, reports only. An arrow "
    "from act leaves the frame to a green git commit card through a purple diamond marked pre-commit, blocks "
    "the commit, with a note that it is git's own hook, one layer below the agent. A legend says a diamond can block and a square cannot.",
    subtitle="The four points of Osmani's list on the loop; purple can block, grey supplies or reports.",
    height=720, data_w=True)

W, H = 176, 84
MEM, REASON, ACT, OBSERVE = (40, 176), (328, 176), (640, 176), (328, 400)
GIT = (640, 600)
ROW = REASON[1] + H // 2                                   # 218: the reason and act row

# the loop, as a neutral frame around the three steps
fig.outline(Box(304, 128, 560, 400), "border", width=1, radius=8)
fig.text(320, 156, "the loop", "note")

fig.card(*MEM, 144, H, heading="memory file", lines=["rules, config"], color="state")
for (x, y), name, what, role in [(REASON, "reason", "the model call", "model"),
                                 (ACT, "act", "a tool runs", "act"),
                                 (OBSERVE, "observe", "results return", "state")]:
    fig.card(x, y, W, H, heading=name, lines=[what], color=role)
fig.card(*GIT, W, 56, heading="git commit", color="state")

# session start: memory file -> reason, a grey square (supplies)
SX = 244
fig.arrow((MEM[0] + 144, ROW), (REASON[0], ROW))
fig.marker(SX, ROW, "square", "rule", size=16)
fig.text(SX, ROW - 20, "session start", "label", anchor="middle", bold=True)
fig.text(SX, ROW + 32, "supplies", "note", anchor="middle")

# pre-tool: reason -> act, a purple diamond (blocks)
PX = (REASON[0] + W + ACT[0]) // 2                         # 572
fig.arrow((REASON[0] + W, ROW), (ACT[0], ROW))
fig.marker(PX, ROW, "diamond", "gate", size=24)
fig.text(PX, ROW - 24, "pre-tool", "label", anchor="middle", bold=True, color="gate")
fig.text(PX, ROW + 36, "blocks the call", "note", anchor="middle", color="gate")

# post-edit: act -> observe, a grey square on the way down (reports)
AX = ACT[0] + 48                                           # 688
OY = OBSERVE[1] + H // 2                                   # 442
fig.arrow((AX, ACT[1] + H), (OBSERVE[0] + W, OY), via=[(AX, OY)])
fig.marker(AX, 344, "square", "rule", size=16)
fig.text(AX - 20, 340, "post-edit", "label", anchor="end", bold=True)
fig.text(AX - 20, 360, "reports only", "note", anchor="end")

# observe -> reason: the next turn
fig.arrow((REASON[0] + 88, OBSERVE[1]), (REASON[0] + 88, REASON[1] + H), label="next turn")

# pre-commit: act -> git, leaving the loop, a purple diamond (blocks the commit, one layer below)
CX = ACT[0] + 136                                          # 776
fig.arrow((CX, ACT[1] + H), (CX, GIT[1]))
fig.marker(CX, 560, "diamond", "gate", size=24)
fig.text(CX + 24, 556, "pre-commit", "label", bold=True, color="gate")
fig.text(CX + 24, 576, "blocks the commit", "note", color="gate")
fig.text(GIT[0] - 16, GIT[1] + 32, "git's own hook, one layer below the agent", "note", anchor="end")

fig.legend(40, 440, [dict(color="gate", label="can block", mark="diamond"),
                     dict(color="rule", label="cannot block", mark="square")])
fig.caption("Session start and post-edit never stop anything: one brings a rule in, the other reports a break.")
fig.write()
