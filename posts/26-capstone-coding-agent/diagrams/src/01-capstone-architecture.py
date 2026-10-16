"""Post 26, hero: the component map of post 02 with the capstone placed on it (hrn_fig_design.md section 2).

Run from the series root:  uv run python posts/26-capstone-coding-agent/diagrams/src/01-capstone-architecture.py
Writes posts/26-capstone-coding-agent/diagrams/01-capstone-architecture.svg.

The layout is post 02's hero, drawn at full size: the loop at the centre with its three steps in their roles, the
four components that feed the model on the left, the four that govern it on the right, and the two at a larger
scale in the band below, all inside one frame. Each card adds the companion module that holds the component, or
"not shipped" when the companion leaves it as a seam; a seam is drawn with a dashed outline and no fill. The
module-to-component mapping is read from the module table of the post's first section and asserted, and the four
seams from the sentence under that table, so the figure and the body cannot drift. The module files are checked
to exist in code/26-coding-agent/. Roles as post 02: tools act; state, memory and observability state;
verification, hooks and permissions gate; context management, orchestration and long-horizon patterns neutral.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
ROOT = POST.parents[1]
BODY = (POST / "index.md").read_text(encoding="utf-8")
PKG = ROOT / "code" / "26-coding-agent" / "src" / "coding_agent"

NAMES = {"01": "Loop", "02": "Tools", "03": "State", "04": "Context management", "05": "Memory",
         "06": "Verification", "07": "Hooks", "08": "Permissions", "09": "Orchestration",
         "10": "Long-horizon patterns", "11": "Observability"}
ROLE = {"02": "act", "03": "state", "04": None, "05": "state", "06": "gate", "07": "gate", "08": "gate",
        "11": "state", "09": None, "10": None}

# module table of section 1: | `core.py` | ... | 03 state, 06 verification | ...
HOLDS = {}
for module, comps in re.findall(r"^\| `(\w+\.py)` \| [^|]+ \| ([^|]+) \|", BODY, re.M):
    for num in re.findall(r"\b(\d\d) [a-z]", comps):
        HOLDS.setdefault(num, module)
assert HOLDS == {"03": "core.py", "06": "core.py", "01": "driver.py", "04": "driver.py", "10": "driver.py",
                 "05": "memory.py", "11": "observe.py"}, HOLDS
assert re.search(r"^\| `cost\.py` \|[^|]+\| the budget exit of 01 loop \|", BODY, re.M)
SEAMS = ["02", "07", "08", "09"]
assert ("Four components have no module: 02 tools, because the generator returns a dictionary of files and makes "
        "no tool calls; 07 hooks and 08 permissions") in BODY and "and 09 orchestration, because" in BODY
assert sorted(list(HOLDS) + SEAMS) == sorted(NAMES)
for module in set(HOLDS.values()) | {"cost.py"}:
    assert (PKG / module).exists(), module

fig = Figure(
    "01-capstone-architecture", "The whole series in one machine, seams marked",
    "The component map of a harness with the capstone placed on it. At the centre, component 01, the loop, held by "
    "driver.py, its three steps reason, act and observe, and cost.py as its budget exit. On the left the four "
    "components that feed the model: 02 tools, not shipped; 03 state, held by core.py; 04 context management, held "
    "by driver.py; 05 memory, held by memory.py. On the right the four that govern it: 06 verification, held by "
    "core.py; 07 hooks and 08 permissions, not shipped; 11 observability, held by observe.py. Below, at a larger "
    "scale: 09 orchestration, not shipped, and 10 long-horizon patterns, held by driver.py. Seven components are "
    "held; the four seams are drawn dashed with no fill.",
    subtitle="Seven of the eleven components are a module of code/26-coding-agent; four are seams it names.",
    height=720, data_w=True)

frame = Box(40, 104, 880, 520)
fig.outline(frame, "rule", width=1.5, radius=8)

LEFT, RIGHT, COL_W = 64, 648, 248
MID, MID_W = 376, 208
TOP, CARD_H, STEP = 160, 64, 80


def component(x, y, w, n):
    role = ROLE[n]
    b = Box(x, y, w, CARD_H)
    seam = n in SEAMS
    if seam:
        fig.outline(b, f"{role}" if role else "ink-muted", width=1.5, dash="proj", radius=8)
    else:
        fig.fill(b, f"{role}-soft" if role else "neutral-soft", radius=8)
        fig.outline(b, f"{role}-line" if role else "border", radius=8)
    fig.text(x + 16, y + 28, n, "value", color=role if role else "ink-muted")
    fig.text(x + 48, y + 28, NAMES[n], "label")
    if seam:
        fig.text(x + 48, y + 52, "not shipped", "note")
    else:
        fig.text(x + 48, y + 52, HOLDS[n], "code")
    return b


fig.text(LEFT, 144, "Feed the model", "head")
fig.text(RIGHT, 144, "Govern it", "head")
for k, n in enumerate(["02", "03", "04", "05"]):
    component(LEFT, TOP + k * STEP, COL_W, n)
for k, n in enumerate(["06", "07", "08", "11"]):
    component(RIGHT, TOP + k * STEP, COL_W, n)

# the loop card: number, name, module, the three steps, and the budget exit
LOOP_H = 3 * STEP + CARD_H
loop = Box(MID, TOP, MID_W, LOOP_H)
fig.fill(loop, "surface", radius=8)
fig.outline(loop, "ink-muted", width=1.5, radius=8)
fig.text(MID + 16, TOP + 28, "01", "value", color="ink-muted")
fig.text(MID + 48, TOP + 28, NAMES["01"], "label", bold=True)
fig.text(MID + 48, TOP + 52, HOLDS["01"], "code")
steps = {"reason": (Box(440, 240, 80, 32), "model"),
         "act": (Box(496, 320, 72, 32), "act"),
         "observe": (Box(392, 320, 80, 32), "state")}
for word, (b, role) in steps.items():
    fig.fill(b, f"{role}-soft", radius=8)
    fig.outline(b, role, radius=8)
    fig.text(b.x + b.w / 2, b.y + 21, word, "label", anchor="middle")
fig.arrow((520, 272), (540, 320))
fig.arrow((496, 336), (472, 336))
fig.arrow((424, 320), (448, 272))
exit_box = Box(MID + 16, 384, MID_W - 32, 56)
fig.fill(exit_box, "gate-soft", radius=8)
fig.outline(exit_box, "gate-line", radius=8)
fig.text(MID + 16 + 16, 408, "budget exit (3)", "label")
fig.text(MID + 16 + 16, 428, "cost.py", "code")

mid_y = TOP + 3 * STEP / 2 + CARD_H / 2
fig.arrow((LEFT + COL_W, mid_y), (MID, mid_y), label="feed")
fig.arrow((RIGHT, mid_y), (MID + MID_W, mid_y), label="govern")

# the larger-scale band
fig.text(LEFT, 504, "At a larger scale", "head")
component(LEFT, 520, COL_W, "09")
component(MID, 520, 240, "10")
fig.legend(RIGHT, 528, [dict(color="model", label="model", mark="swatch"),
                        dict(color="state", label="state", mark="swatch")], step=32)
fig.legend(RIGHT + 128, 528, [dict(color="act", label="act", mark="swatch"),
                              dict(color="gate", label="gate", mark="swatch")], step=32)
fig.legend(RIGHT, 592, [dict(color="ink-muted", label="seam: not shipped", mark="dashed-outline")])

fig.caption("The dashed four are seams: the post says where each wires in, rather than drawing it done.")
fig.write()
