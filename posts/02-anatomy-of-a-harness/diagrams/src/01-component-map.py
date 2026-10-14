"""Post 02, hero: the eleven components of a harness around the loop (hrn_fig_design.md section 2).

Run from the series root:  uv run python posts/02-anatomy-of-a-harness/diagrams/src/01-component-map.py
Writes posts/02-anatomy-of-a-harness/diagrams/01-component-map.svg.

The loop is at the centre with its three steps in their roles (reason model, act act, observe state); the four
components that feed the model sit on the left, the four that govern it on the right, and the two at a larger
scale sit on a frame around the whole. Each component card takes the role of the job it does: tools act;
state and memory state; verification, hooks and permissions gate; observability state (the trace store);
context management, orchestration and long-horizon patterns are neutral. The numbers and names are read from the
index table of the post's last numbered section and asserted, so the figure and the body cannot drift.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, Box  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")
TABLE = dict(re.findall(r"^\| (\d\d) \| ([A-Z][a-z -]+) \| (?:core|feeds|governs|scale) \|", BODY, re.M))
NAMES = {"01": "Loop", "02": "Tools", "03": "State", "04": "Context management", "05": "Memory",
         "06": "Verification", "07": "Hooks", "08": "Permissions", "09": "Orchestration",
         "10": "Long-horizon patterns", "11": "Observability"}
assert TABLE == NAMES, TABLE
GROUPS = {"core": ["01"], "feeds": ["02", "03", "04", "05"], "governs": ["06", "07", "08", "11"],
          "scale": ["09", "10"]}
for group, nums in GROUPS.items():
    for n in nums:
        assert re.search(rf"^\| {n} \| {NAMES[n]} \| {group} \|", BODY, re.M), (n, group)
ROLE = {"02": "act", "03": "state", "04": None, "05": "state", "06": "gate", "07": "gate", "08": "gate",
        "11": "state", "09": None, "10": None}

fig = Figure(
    "01-component-map", "Eleven components around one loop",
    "The component map of a harness. At the centre, component 01, the loop: reason in the model colour, act in "
    "the act colour and observe in the state colour, joined clockwise. On the left, the four components that feed "
    "the model: 02 tools, 03 state, 04 context management, 05 memory, with an arrow into the loop labelled feed. "
    "On the right, the four that govern it: 06 verification, 07 hooks, 08 permissions, 11 observability, with an "
    "arrow into the loop labelled govern. A frame around everything carries the two at a larger scale: "
    "09 orchestration and 10 long-horizon patterns. A legend names the four colours: model, act, state, gate.",
    subtitle="Four feed the model, four govern it, and two work at a larger scale than one running agent.",
    data_w=True)

# the frame: the scale tier around the whole
frame = Box(40, 104, 880, 372)
fig.outline(frame, "rule", width=1.5, radius=8)

COL_W, CARD_H, STEP = 240, 44, 52
LEFT, RIGHT, MID, MID_W = 72, 648, 376, 208
TOP = 152


def component(x, y, w, n):
    role = ROLE[n]
    b = Box(x, y, w, CARD_H)
    fig.fill(b, f"{role}-soft" if role else "neutral-soft", radius=8)
    fig.outline(b, f"{role}-line" if role else "border", radius=8)
    fig.text(x + 16, y + 28, n, "value", color=role if role else "ink-muted")
    fig.text(x + 48, y + 28, NAMES[n], "label")
    return b


fig.text(LEFT, 136, "Feed the model", "head")
fig.text(MID, 136, "The core", "head")
fig.text(RIGHT, 136, "Govern it", "head")
for k, n in enumerate(GROUPS["feeds"]):
    component(LEFT, TOP + k * STEP, COL_W, n)
for k, n in enumerate(GROUPS["governs"]):
    component(RIGHT, TOP + k * STEP, COL_W, n)

# the loop card, with its three steps
loop = Box(MID, TOP, MID_W, 3 * STEP + CARD_H)
fig.fill(loop, "surface", radius=8)
fig.outline(loop, "ink-muted", width=1.5, radius=8)
fig.text(MID + 16, TOP + 28, "01", "value", color="ink-muted")
fig.text(MID + 48, TOP + 28, NAMES["01"], "label", bold=True)
steps = {"reason": (Box(440, 200, 80, 32), "model"),
         "act": (Box(496, 288, 72, 32), "act"),
         "observe": (Box(392, 288, 80, 32), "state")}
for word, (b, role) in steps.items():
    fig.fill(b, f"{role}-soft", radius=8)
    fig.outline(b, role, radius=8)
    fig.text(b.x + b.w / 2, b.y + 21, word, "label", anchor="middle")
fig.arrow((520, 232), (540, 288))
fig.arrow((496, 304), (472, 304))
fig.arrow((424, 288), (448, 232))

mid_y = TOP + 3 * STEP / 2 + CARD_H / 2
fig.arrow((LEFT + COL_W, mid_y), (MID, mid_y), label="feed")
fig.arrow((RIGHT, mid_y), (MID + MID_W, mid_y), label="govern")

# the scale tier, on the frame's lower band
fig.text(LEFT, 388, "At a larger scale", "head")
component(LEFT, 404, COL_W, "09")
component(328, 404, 256, "10")
fig.legend(RIGHT, 412, [dict(color="model", label="model", mark="swatch"),
                        dict(color="state", label="state", mark="swatch")], step=32)
fig.legend(RIGHT + 128, 412, [dict(color="act", label="act", mark="swatch"),
                              dict(color="gate", label="gate", mark="swatch")], step=32)
fig.write()
