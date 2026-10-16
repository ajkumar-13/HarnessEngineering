"""Post 19, the hero: the loop with its four layered exits, in the order the post's controller checks them.

Run from the series root:  uv run python posts/19-loop-engineering/diagrams/src/01-layered-exits.py
Writes posts/19-loop-engineering/diagrams/01-layered-exits.svg.
The loop of hrn_fig_design.md section 1 laid out as one turn from left to right: before the model call the turn
bound (exit (2), the `for` statement) and the reserve check (exit (3), this post's change); after it the check the
companion makes, exit (1) through a verification gate, then exit (4). Reason blue, act orange, observe green, every
exit and check purple (gate); the red dashed path is where a doom loop goes without exit (4): on to the cap. The
companion's defaults are read from code/03-agent-loop and asserted; the exit names, the order and what each exit
leaves behind are asserted against the body and the snippet.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "03-agent-loop" / "src"))
from figkit import Box, Figure  # noqa: E402
from agent_loop import StopReason, run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
SNIPPET = (POST / "snippets" / "layered_loop.py").read_text(encoding="utf-8")
DEFAULTS = {k: v.default for k, v in inspect.signature(run).parameters.items() if v.default is not inspect._empty}
assert DEFAULTS["max_iters"] == 12 and DEFAULTS["no_progress_window"] == 3
assert [s.value for s in StopReason] == ["completed", "max_iters", "budget", "no_progress"]
assert "exit (3), reserved: stop BEFORE the call that would breach it" in SNIPPET
for phrase in ["The companion of post 03 checks (1), (3) and (4) after each model call, in that order, and takes (2) "
               "when its `for` statement runs out of turns.",
               "Section 4 moves (3) in front of the call",
               "**the intended exit returns a result; a guard exit returns a result and a resumable position.**",
               "| (4) no progress | the chosen stall signal repeats |"]:
    assert phrase in BODY, phrase

fig = Figure(
    "01-layered-exits", "Four layered exits: one intended, three guards",
    "One turn of the agent loop from left to right. Before the model call, two purple checks: turns left, whose "
    "exit is (2), iteration cap, and the reserve check, whose exit is (3), budget, taken when the next call would "
    "cross the ceiling. Then reason, the model call, in blue. After the call a purple check leads to (1), final "
    "answer, which a verification gate must confirm, and to (4), no progress, the same calls 3 turns running; "
    "otherwise the turn goes on to act in orange and observe in green, and the next call carries the whole "
    "history back to the start. Exit (1) leaves the result; exits (2), (3) and (4) each leave a handoff to resume "
    "from. A red dashed path shows a doom loop without exit (4) running on to the iteration cap.",
    subtitle="Checked in this order every turn: the cap and the reserve before the model call, (1) and (4) after it.",
    height=720, data_w=True)

ROW = 232                                      # the centre line of the turn
A, B, C = (144, ROW), (248, ROW), (520, ROW)    # turns left, reserve, after the call
CW, CH = 136, 72
REASON = (288, ROW - CH // 2)
ACT = (584, ROW - CH // 2)
OBSERVE = (776, ROW - CH // 2)

for (x, y), name, what, role in [(REASON, "reason", "the model call", "model"),
                                 (ACT, "act", "run the tools", "act"),
                                 (OBSERVE, "observe", "append results", "state")]:
    fig.card(x, y, CW, CH, heading=name, lines=[what], style="note", color=role)
for (x, y), label in [(A, "turns left?"), (B, "reserve"), (C, "after the call")]:
    fig.marker(x, y, "diamond", "gate", size=24)
    fig.text(x, y - 24, label, "label", anchor="middle", color="gate")

# the turn, left to right, and the next call back to the start, above the row
fig.arrow((A[0] + 16, ROW), (B[0] - 16, ROW))
fig.arrow((B[0] + 16, ROW), (REASON[0], ROW))
fig.arrow((REASON[0] + CW, ROW), (C[0] - 16, ROW))
fig.arrow((C[0] + 16, ROW), (ACT[0], ROW))
fig.arrow((ACT[0] + CW, ROW), (OBSERVE[0], ROW))
TOP, LX = 144, 56
fig.edge((OBSERVE[0] + CW // 2, OBSERVE[1]), (OBSERVE[0] + CW // 2, TOP), color="arrow", width=1.5)
fig.edge((OBSERVE[0] + CW // 2, TOP), (LX, TOP), color="arrow", width=1.5)
fig.edge((LX, TOP), (LX, ROW), color="arrow", width=1.5)
fig.arrow((LX, ROW), (A[0] - 16, ROW))
fig.text((LX + OBSERVE[0] + CW // 2) // 2, TOP - 12, "next call, whole history", "note", anchor="middle")

# the four exit cards, in the order they are checked
EW, EH, EY = 208, 108, 440
xs = [40 + k * (EW + 16) for k in range(4)]
EXITS = [("(2) iteration cap", "no turns left", "leaves a handoff"),
         ("(3) budget", "next call would cross", "leaves a handoff"),
         ("(1) final answer", "verified by a gate", "leaves the result"),
         ("(4) no progress", "same calls, 3 turns", "leaves a handoff")]
for x, (head, fires, leaves) in zip(xs, EXITS):
    fig.card(x, EY, EW, EH, heading=head, lines=[fires, leaves], style="note", color="gate")
mid = [x + EW // 2 for x in xs]

# each check down to its exit: A to (2), B to (3), C to (1) and (4) along one bus
B1, B2 = 336, 376                              # the two bus heights
fig.edge((A[0], A[1] + 16), (A[0], B1), color="gate", width=1.5)
fig.edge((A[0], B1), (mid[0], B1), color="gate", width=1.5)
fig.arrow((mid[0], B1), (mid[0], EY), color="gate")
fig.edge((B[0], B[1] + 16), (B[0], B2), color="gate", width=1.5)
fig.edge((B[0], B2), (mid[1], B2), color="gate", width=1.5)
fig.arrow((mid[1], B2), (mid[1], EY), color="gate")
fig.edge((C[0], C[1] + 16), (C[0], B2), color="gate", width=1.5)
fig.edge((C[0], B2), (mid[3], B2), color="gate", width=1.5)
fig.arrow((mid[2], B2), (mid[2], EY), color="gate")
fig.arrow((mid[3], B2), (mid[3], EY), color="gate")
fig.outline(Box(xs[2], EY, EW, EH), "gate", width=2.5, radius=8)   # the intended exit

# without exit (4): a doom loop repeats the same call until the cap stops it
RY = EY + EH + 56
fig.edge((mid[3], EY + EH), (mid[3], RY), color="error", width=1.5, dash="proj")
fig.edge((mid[3], RY), (mid[0], RY), color="error", width=1.5, dash="proj")
fig.arrow((mid[0], RY), (mid[0], EY + EH), color="error", dash="proj")
fig.text((mid[0] + mid[3]) // 2, RY + 28, "without (4), a doom loop repeats the same call until (2) stops it",
         "label", anchor="middle", color="error")

fig.caption("Only (1) means the work is done; a run caught by (2), (3) or (4) leaves a handoff to resume from.")
fig.write()
