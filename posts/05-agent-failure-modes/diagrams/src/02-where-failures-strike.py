"""Post 05, section 4: where each failure mode shows in the loop, and where its fix installs.

Run from the series root:  uv run python posts/05-agent-failure-modes/diagrams/src/02-where-failures-strike.py
Writes posts/05-agent-failure-modes/diagrams/02-where-failures-strike.svg.
The loop is post 03's reason, act, observe cycle (hrn_fig_design.md section 1: reason blue, act orange, observe
green, clockwise). Red tags are the stages where section 4 says each mode shows; purple diamonds are gates on the
arrow each fix intercepts (section 3 of the design page); the memory file and plan are state written before the
run. Every placement is a sentence of section 4 or section 2, asserted below. No numbers.
The no-progress check sits on the arrow into act because the companion checks it there: after the model call
and before the tools run (code/03-agent-loop/src/agent_loop/loop.py, asserted below; post 03's hero agrees).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in (
    "**At reason**, where the model decides, live the *judgement* failures: victory declaration and one-shotting.",
    "**At act**, where a tool runs, lives the *blast-radius* failure: destructive action.",
    "**At observe, as the loop turns again**, live the *iteration* failures: doom loop and context anxiety.",
    "**Across turns** lives the *consistency* failure: silent drift.",
    "its fix sits on the loop's **exit**",
    "so its fix runs between turns",
    "Silent drift is fixed at session start, where the memory file is injected, and before each tool call",
    "the plan is written where a later session can read it",
):
    assert phrase in BODY, phrase
LOOP = (POST.parents[1] / "code" / "03-agent-loop" / "src" / "agent_loop" / "loop.py").read_text(encoding="utf-8")
assert LOOP.index("model.respond(") < LOOP.index("stop (4)") < LOOP.index("ACT + OBSERVE")

fig = Figure(
    "02-where-failures-strike", "Where each failure shows, and where its fix sits",
    "The agent loop as three cards turning clockwise: reason in blue, act in orange, observe in green. Red tags mark "
    "where each failure mode shows: victory declaration and one-shotting at reason, destructive action at act, doom "
    "loop and context anxiety at observe as the loop turns, and silent drift as a dashed red frame around every "
    "turn. Purple diamonds mark where fixes install: verification on the exit arrow to the final answer, the "
    "no-progress check and then the deny-list hook on the arrow into act, and context management, a note "
    "without a gate, beside the arrow back to reason. A green card, memory file and plan, feeds reason at session start.",
    subtitle="Red: where a mode shows. Purple: a gate where its fix installs. Green: state written before the run.",
    data_w=True)

# silent drift: the frame around every turn of the loop
fig.outline(Box(192, 120, 552, 328), "error", width=1.5, dash="proj", radius=8)
fig.text(468, 472, "silent drift: across every turn", "label", anchor="middle", color="error")

# the loop: reason (model), act (act), observe (state), clockwise
reason = Box(400, 160, 160, 48)
act = Box(560, 336, 160, 48)
observe = Box(224, 336, 160, 48)
fig.card(reason.x, reason.y, reason.w, reason.h, color="model")
fig.text(480, 188, "reason", "label", anchor="middle", bold=True)
fig.card(act.x, act.y, act.w, act.h, color="act")
fig.text(640, 364, "act", "label", anchor="middle", bold=True)
fig.card(observe.x, observe.y, observe.w, observe.h, color="state")
fig.text(304, 364, "observe", "label", anchor="middle", bold=True)

fig.arrow((544, 208), (608, 336))          # reason to act
fig.arrow((560, 360), (384, 360))          # act to observe
fig.arrow((352, 336), (416, 208))          # observe back to reason

# where each mode shows: red tags at the stage
fig.text(480, 144, "victory declaration, one-shotting", "label", anchor="middle", color="error")
fig.text(640, 412, "destructive action", "label", anchor="middle", color="error")
fig.text(304, 412, "doom loop, context anxiety", "label", anchor="middle", color="error")

# the exit and its gate
final = Box(784, 160, 136, 48)
fig.card(final.x, final.y, final.w, final.h, color="model")
fig.text(852, 188, "final answer", "label", anchor="middle")
fig.arrow((560, 184), (784, 184))
with fig.data():
    fig.marker(672, 184, "diamond", "gate", size=12)
    fig.marker(560, 240, "diamond", "gate", size=12)     # no-progress check, after the model call
    fig.marker(592, 304, "diamond", "gate", size=12)     # deny-list hook, as the tool is called
fig.text(672, 168, "verification", "label", anchor="middle", color="gate")
fig.text(580, 244, "no-progress check", "label", color="gate")
fig.text(612, 308, "deny-list hook", "label", color="gate")
fig.text(364, 276, "context management", "note", anchor="end")

# state written before the run, read at session start
mem = Box(40, 232, 136, 72)
fig.card(mem.x, mem.y, mem.w, mem.h, color="state")
fig.text(108, 260, "memory file", "label", anchor="middle")
fig.text(108, 284, "and plan", "label", anchor="middle")
fig.arrow((176, 252), (400, 196))
fig.text(208, 212, "session start", "note")

fig.caption("A mode shows at one stage; its fix often sits on the arrow before or after it.")
fig.write()
