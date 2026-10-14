"""Post 08, the hero: the loop turns inside the context window; its state lives on disk, and git makes it reversible.

Run from the series root:  uv run python posts/08-state-filesystem-git/diagrams/src/01-filesystem-durable-state.py
Writes posts/08-state-filesystem-git/diagrams/01-filesystem-durable-state.svg.
The loop is the series' compact loop (hrn_fig_design.md section 1: reason blue, act orange, observe green,
clockwise) inside a neutral frame for the window; files and commits are state cards (section 4), the bad step is
red. Every file name and role is a phrase of the post's body, asserted below. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
FILES = [("plan.md", "rewritten each step"), ("scratch/build.log", "offloaded output"),
         ("output.json", "the artefact"), ("handoff.md", "survives a reset")]
for phrase in ("**the window is for what the model needs to think about *now*; disk is for everything else.**",
               "A `plan.md` or `task.md` that the agent writes early", "Write them to `scratch/build.log`",
               "generated code, a report, `output.json`", "lets the work survive a context reset",
               "**checkpoint after each verified step; revert on error.**", "rewritten, not appended"):
    assert phrase in BODY, phrase

fig = Figure(
    "01-filesystem-durable-state", "The loop thinks in the window; its state lives on disk",
    "Two regions. On the left, a neutral frame for the context window holds the agent loop: reason in blue, act in "
    "orange, observe in green, turning clockwise; the window is re-sent on every call and wiped at a reset. On the "
    "right, a green frame for disk holds four files, plan.md rewritten each step, scratch/build.log the offloaded "
    "output, output.json the artefact, and handoff.md which survives a reset, and a git history of two "
    "checkpoints and a bad step in red, with an arrow resetting the bad step to the last checkpoint. An arrow "
    "from the window to disk reads write, offload; one back reads read on demand.",
    subtitle="Act writes and offloads to disk; observe reads back on demand; git makes the disk side reversible.",
    data_w=True)

# the window: the loop, clockwise
win = Box(40, 120, 344, 352)
fig.outline(win, "ink-muted", width=1.5, radius=8)
fig.text(56, 148, "context window: this turn", "head")
reason, act, observe = Box(144, 184, 136, 48), Box(232, 360, 136, 48), Box(56, 360, 136, 48)
for b, name, role in ((reason, "reason", "model"), (act, "act", "act"), (observe, "observe", "state")):
    fig.card(b.x, b.y, b.w, b.h, color=role)
    fig.text(b.x + b.w // 2, b.y + 28, name, "label", anchor="middle", bold=True)
fig.arrow((256, 232), (300, 360))
fig.arrow((232, 384), (192, 384))
fig.arrow((96, 360), (168, 232))
fig.text(56, 448, "re-sent every call; wiped at a reset", "note")

# disk: files and git
disk = Box(496, 120, 424, 352)
fig.outline(disk, "state", width=1.5, radius=8)
fig.text(512, 148, "disk: durable", "head", color="state")
for k, (path, role) in enumerate(FILES):
    x, y = 512 + (k % 2) * 200, 168 + (k // 2) * 72
    fig.card(x, y, 192, 64, color="state")
    fig.text(x + 16, y + 26, path, "code")
    fig.text(x + 16, y + 50, role, "note")
fig.text(512, 340, "git", "head")
commits = [Box(512, 356, 120, 48), Box(664, 356, 120, 48), Box(816, 356, 88, 48)]
for b, label, role in zip(commits, ("checkpoint", "checkpoint", "bad step"), ("state", "state", "error")):
    fig.card(b.x, b.y, b.w, b.h, color=role)
    fig.text(b.x + b.w // 2, b.y + 28, label, "label", anchor="middle")
fig.chain(commits)
fig.arrow((860, 404), (724, 404), via=((860, 424), (724, 424)))
fig.text(792, 448, "rollback: reset to the last checkpoint", "label", anchor="middle")

# between them
fig.arrow((384, 232), (496, 232), label="write, offload")
fig.arrow((496, 296), (384, 296), label="read on demand")

fig.caption("What the model needs this turn and every turn rides in the window; everything else goes to disk.")
fig.write()
