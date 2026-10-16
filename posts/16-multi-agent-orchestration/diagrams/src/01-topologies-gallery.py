"""Post 16, hero: the four topologies, each panel naming who writes the control flow.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/diagrams/src/01-topologies-gallery.py
Writes posts/16-multi-agent-orchestration/diagrams/01-topologies-gallery.svg.
A section 3 form of hrn_fig_design.md, four panels in the order of the post's list: an agent that owns the task is
a neutral card (an agent as a whole is neither the model's output nor an action); a sub-task or a worker the
harness dispatches is an action (act, orange), and so is a peer's claim on the repository; the shared repository
is state (green). The "who writes the control flow" line of each panel is the second column of the post's table,
asserted against the body below. There are no numbers in this figure.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for row in ("| Single agent | The model, inside one owning loop |",
            "| Pipeline | The engineer, fixed at design time |",
            "| Orchestrator-worker, lead splits | The engineer writes dispatch and merge; the lead model chooses the "
            "split |",
            "| Swarm | Nobody centrally; the repository |"):
    assert row in BODY, row

fig = Figure(
    "01-topologies-gallery", "Four shapes, and who writes the control flow",
    "Four panels. Single agent: one agent card, its own loop, sends three sub-tasks out and runs them itself; "
    "control flow: the model, in one loop. Orchestrator-worker: a lead dispatches four workers, whose results "
    "return to the lead to merge; control flow: the engineer's dispatch and merge, the lead's split. Pipeline: "
    "one draft passes through draft, edit and fact-check stages in order; control flow: the engineer, at design "
    "time. Swarm: four peer agents claim work from a shared repository of task files, with no lead; control "
    "flow: nobody centrally, the repository.",
    subtitle="Orange: work dispatched or claimed; green: shared state. The first shape is the default.",
    height=720, data_w=True)


def panel(x, y, w, h, title):
    fig.outline(Box(x, y, w, h), "border", width=1, radius=8)
    fig.text(x + 16, y + 32, title, "head")


def card(x, y, w, h, label, color=None):
    fig.card(x, y, w, h, color=color)
    fig.text(x + w // 2, y + h // 2 + 4 + (h // 2) % 4, label, "label", anchor="middle")
    return Box(x, y, w, h)


def control(x, y, words):
    fig.text(x + 16, y, "control flow:", "note")
    fig.text(x + 120, y, words, "label")


L, R, W = 40, 496, 424
T1, T2, PH = 112, 392, 260

# 1. single agent: the agent runs its own sub-tasks
panel(L, T1, W, PH, "Single agent")
card(64, 212, 136, 48, "one agent", None)
for y in (164, 216, 268):
    card(296, y, 136, 40, "sub-task", "act")
    fig.arrow((200, 236), (296, y + 20), color="act")
control(L, T1 + PH - 16, "the model, in one loop")

# 2. orchestrator-worker: a lead dispatches, workers return, the lead merges
panel(R, T1, W, PH, "Orchestrator-worker")
card(512, 156, 392, 32, "lead splits the task and dispatches", None)
for x in (512, 616, 720, 824):
    card(x, 220, 80, 36, "worker", "act")
    fig.arrow((x + 40, 188), (x + 40, 220), color="act")
    fig.arrow((x + 40, 256), (x + 40, 288))
card(512, 288, 392, 32, "lead merges the results", None)
control(R, T1 + PH - 16, "engineer's code, lead's split")

# 3. pipeline: one draft through three ordered stages
panel(L, T2, W, PH, "Pipeline")
stages = [card(x, 488, 112, 48, name, None) for x, name in ((56, "draft"), (200, "edit"), (344, "fact-check"))]
fig.chain(stages, labels=None)
fig.text(252, 580, "one draft, three stages in a fixed order", "note", anchor="middle")
control(L, T2 + PH - 16, "the engineer, at design time")

# 4. swarm: peers claim work from the shared repository, no lead
panel(R, T2, W, PH, "Swarm")
fig.card(632, 468, 152, 72, color="state")
fig.text(708, 498, "shared repository", "label", anchor="middle")
fig.text(708, 522, "task files", "note", anchor="middle")
for x, y in ((512, 444), (512, 524), (816, 444), (816, 524)):
    card(x, y, 88, 40, "agent", None)
    if x < 632:
        fig.arrow((600, y + 20), (632, 496 if y < 500 else 512), color="act")
    else:
        fig.arrow((816, y + 20), (784, 496 if y < 500 else 512), color="act")
control(R, T2 + PH - 16, "nobody centrally")

fig.caption("The shapes differ in who decides what runs next: the model, the engineer, or nobody.")
fig.write()
