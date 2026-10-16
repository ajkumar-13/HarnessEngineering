"""Post 22, hero: an output eval scores one answer; a trajectory and outcome eval scores one run.

Run from the series root:  uv run python posts/22-evaluating-harnesses/diagrams/src/01-output-vs-trajectory.py
Writes posts/22-evaluating-harnesses/diagrams/01-output-vs-trajectory.svg.
A section 3 form of hrn_fig_design.md beside the turn-by-turn run of its section 1: each turn is a column of
reason (model, blue), act (act, orange) and observe (state, green); the failed test at turn 3 is red, the
verification gate before exit (1) is purple, and the workspace the run leaves is state (green). The run is a
schematic of the post's first section, not a measurement, so it carries no numbers; the exit is named in the
series' vocabulary (exit (1), completed), asserted against the body.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("A **trajectory eval** scores what happened during the run", "An **outcome eval** scores the end state",
               "exit (1) `completed`"):
    assert phrase in BODY, phrase

fig = Figure(
    "01-output-vs-trajectory", "An output eval scores an answer; a harness eval, a run",
    "Two panels. Left, an output eval: a prompt leads to one completion, in blue, which a rubric or a judge "
    "scores; the score is blind to how the answer was reached. Right, one agent run drawn as five turns, each a "
    "column of reason in blue, act in orange and observe in green; the observation of turn 3 is red, a test that "
    "fails, and the run recovers. After turn 5 a purple verification gate passes and the run takes exit (1), "
    "completed. A brace over the turns reads: the trajectory eval reads the path, its turns, tokens, gate fires "
    "and stop reason. Below the run, a green card for the workspace the run left, tests pass, and an arrow from "
    "the outcome eval, which reads it.",
    subtitle="The trajectory eval reads the path the run took; the outcome eval reads the world it left behind.",
    data_w=True)

# left: the output eval
LX, LW = 40, 224
fig.text(LX, 136, "Output eval: one answer", "head")
fig.card(LX, 160, LW, 48)
fig.text(LX + 16, 190, "prompt", "label")
fig.card(LX, 248, LW, 48, color="model")
fig.text(LX + 16, 278, "one completion", "label")
fig.card(LX, 336, LW, 48)
fig.text(LX + 16, 366, "score: rubric or judge", "label")
fig.arrow((LX + 112, 208), (LX + 112, 248))
fig.arrow((LX + 112, 296), (LX + 112, 336))
fig.text(LX, 420, "Blind to how the answer", "note")
fig.text(LX, 440, "was reached.", "note")

# right: one run, five turns
RX = 320
fig.text(RX, 136, "Trajectory and outcome eval: one run", "head")
COL_W, STEP, TOP = 80, 96, 216
fig.brace(RX, RX + 4 * STEP + COL_W, 172, label="trajectory eval: turns, tokens, gate fires, stop reason",
          side="above")
for i in range(5):
    x = RX + i * STEP
    fig.text(x + COL_W // 2, 204, f"turn {i + 1}", "note", anchor="middle")
    cells = [("reason", "model"), ("act", "act"), ("test fails" if i == 2 else "observe", "error" if i == 2 else "state")]
    for j, (word, role) in enumerate(cells):
        y = TOP + 40 * j
        fig.fill(Box(x, y, COL_W, 32), f"{role}-soft", radius=4)
        fig.outline(Box(x, y, COL_W, 32), f"{role}-line", width=1, radius=4)
        fig.text(x + COL_W // 2, y + 21, word, "label", anchor="middle", color=f"{role}-ink" if role == "error" else None)
    if i < 4:
        fig.arrow((x + COL_W, TOP + 56), (x + STEP, TOP + 56))

# the gate and the exit
GX = RX + 5 * STEP
fig.arrow((RX + 4 * STEP + COL_W, TOP + 56), (GX, TOP + 56))
fig.fill(Box(GX, TOP + 40, 120, 32), "gate-soft", radius=4)
fig.outline(Box(GX, TOP + 40, 120, 32), "gate", width=1.5, radius=4)
fig.text(GX + 60, TOP + 61, "verify: pass", "label", anchor="middle", color="gate-ink")
fig.arrow((GX + 60, TOP + 72), (GX + 60, TOP + 104))
fig.text(GX + 60, TOP + 124, "exit (1)", "label", anchor="middle")
fig.text(GX + 60, TOP + 144, "completed", "code", anchor="middle")

# the world the run leaves
fig.card(RX, 376, 384, 56, color="state")
fig.text(RX + 16, 410, "workspace after the run: tests pass", "label")
fig.arrow((GX - 16, 404), (RX + 384, 404))
fig.text(GX, 400, "outcome eval", "label")
fig.text(GX, 420, "reads the world", "label")

fig.caption("The outcome decides the verdict; the trajectory explains it.")
fig.write()
