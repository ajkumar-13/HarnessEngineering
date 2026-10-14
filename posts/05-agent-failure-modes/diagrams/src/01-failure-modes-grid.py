"""Post 05, hero: the six failure modes, each with its symptom and the component that fixes it.

Run from the series root:  uv run python posts/05-agent-failure-modes/diagrams/src/01-failure-modes-grid.py
Writes posts/05-agent-failure-modes/diagrams/01-failure-modes-grid.svg.
The names, symptoms and fixes are the post's (section 2 and the triage table of section 8), in the order and
with the component names of notation_guide.md; the script asserts each against the body. A failure mode is
red (error role, hrn_fig_design.md section 0); the fix is ink, named by its component; the one safety failure
carries the figure's single emphasis outline.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")

# (mode, symptom in two short lines, fix component, where it is taught, phrase the body must contain)
MODES = [
    ("Victory declaration", ("says the task is done;", "a later check fails"), "verification", "post 11",
     "*Fix:* **verification**"),
    ("Context anxiety", ("wraps up early as the", "window fills"), "context management", "post 09",
     "*Fix:* active **context management**"),
    ("One-shotting", ("the whole task in one", "large, undocumented change"), "a planner split", "post 12",
     "*Fix:* a **planner, generator, evaluator split**"),
    ("Doom loop", ("the same call, turn after", "turn, and no progress"), "the no-progress exit", "post 03",
     "*Fix:* the loop's **no-progress exit**"),
    ("Silent drift", ("ignores the conventions,", "run after run"), "memory and hooks", "posts 10 and 13",
     "*Fix:* the **ratchet**"),
    ("Destructive action", ("runs rm -rf, a force-push", "or DROP TABLE"), "hooks and permissions",
     "posts 13 and 14", "hooks and permissions. This is the only mode"),
]
for *_, phrase in MODES:
    assert phrase in BODY, phrase
assert "**Five of the six are performance failures**" in BODY and "**One, destructive action, is a safety failure**" in BODY

fig = Figure(
    "01-failure-modes-grid", "Six failure modes, each with a harness fix",
    "A grid of six cards, one per agent failure mode, numbered as in section 2. Each card names the mode in red, "
    "its symptom, and the component that fixes it with the post that teaches it: 1 victory declaration, says the "
    "task is done while a later check fails, fixed by verification, post 11; 2 context anxiety, wraps up early as "
    "the window fills, context management, post 09; 3 one-shotting, the whole task in one large undocumented "
    "change, a planner split, post 12; 4 doom loop, the same call turn after turn, the no-progress exit, post 03; "
    "5 silent drift, ignores the conventions run after run, memory and hooks, posts 10 and 13; 6 destructive "
    "action, runs rm -rf, a force-push or DROP TABLE, hooks and permissions, posts 13 and 14. The sixth card has a "
    "red emphasis outline and is marked the one safety failure.",
    subtitle="Five are performance failures a re-run recovers; destructive action is a safety failure.",
    data_w=True)

X0, W, GAP = 40, 280, 20
Y0, H, VGAP = 104, 176, 16
for k, (mode, symptom, fix, where, _) in enumerate(MODES):
    col, row = k % 3, k // 3
    x, y = X0 + col * (W + GAP), Y0 + row * (H + VGAP)
    fig.card(x, y, W, H)
    if k == 5:
        fig.outline(Box(x, y, W, H), "error", width=2.5, radius=8)
        fig.text(x + W - 16, y + 32, "safety", "note", anchor="end", color="error")
    fig.text(x + 16, y + 32, f"{k + 1}  {mode}", "head", color="error")
    fig.text(x + 16, y + 64, symptom[0], "label")
    fig.text(x + 16, y + 84, symptom[1], "label")
    fig.edge((x + 16, y + 104), (x + W - 16, y + 104), color="border", width=1)
    fig.text(x + 16, y + 132, "fix", "note")
    fig.text(x + 48, y + 132, fix, "label", bold=True)
    fig.text(x + 16, y + 156, where, "note")

fig.caption("The fix is a named piece of machinery; only destructive action needs it before the act.")
fig.write()
