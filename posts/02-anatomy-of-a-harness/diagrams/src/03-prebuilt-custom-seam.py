"""Post 02, section 9: the seam between the prebuilt harness and the custom layer (hrn_fig_design.md section 4,
a comparison as cards side by side; section 2 colours, each card in the role of its component's job).

Run from the series root:  uv run python posts/02-anatomy-of-a-harness/diagrams/src/03-prebuilt-custom-seam.py
Writes posts/02-anatomy-of-a-harness/diagrams/03-prebuilt-custom-seam.svg.

Left, the mechanism a tool or SDK ships; right, the policy a team writes. The three components that appear on
both sides (tools, hooks, permissions) are the top three rows, joined across a dashed seam. Every item is a
phrase of the section, asserted against the body; there are no numbers other than component numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, Box  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")
for phrase in ("ship a loop, tool dispatch, context management, a hook system, a permission model and some form of "
               "trace", "its conventions in a memory file, its own tools, its evaluations, its enforcement hooks, "
               "its sandbox policy", "An SDK gives a team a *hook system*, and the team writes the *hooks*",
               "it gives *tool dispatch*, and the team writes the *tools*", "Evaluations sit on the custom side alone"):
    assert phrase in BODY, phrase

# (number, prebuilt mechanism, custom policy, role); None where a side has no counterpart
ROWS = [("02", "Tool dispatch", "The team's tools", "act"),
        ("07", "Hook system", "The team's hooks", "gate"),
        ("08", "Permission model", "Sandbox policy", "gate"),
        ("01", "Loop", None, None),
        ("04", "Context management", None, None),
        ("11", "Trace format", None, "state")]
CUSTOM_ONLY = [("05", "Memory file", "state"), ("", "Evaluations, post 22", None)]

fig = Figure(
    "03-prebuilt-custom-seam", "The SDK ships the mechanism; the team writes the policy",
    "Two columns of cards split by a dashed vertical seam. Left, prebuilt, the mechanism a tool or SDK ships: "
    "02 tool dispatch, 07 hook system, 08 permission model, 01 loop, 04 context management, 11 trace format. "
    "Right, custom, the policy a team writes: the team's tools (02), the team's hooks (07), sandbox policy (08), "
    "a memory file (05), and evaluations, which are post 22 rather than a component. Arrows cross the seam from "
    "tool dispatch, the hook system and the permission model to their custom counterparts: same component, two "
    "owners.",
    subtitle="Tools, hooks and permissions appear on both sides of the seam: same component, two owners.",
    data_w=True)

LX, RX, W, H, STEP, TOP = 40, 560, 360, 44, 52, 136
SEAM = 480


def card(x, y, n, name, role):
    b = Box(x, y, W, H)
    fig.fill(b, f"{role}-soft" if role else "neutral-soft", radius=8)
    fig.outline(b, f"{role}-line" if role else "border", radius=8)
    if n:
        fig.text(x + 16, y + 28, n, "value", color=role if role else "ink-muted")
    fig.text(x + 48 if n else x + 16, y + 28, name, "label")
    return b


fig.text(LX, 120, "Prebuilt: what the SDK ships", "head")
fig.text(RX, 120, "Custom: what the team writes", "head")
with fig.data():
    fig.edge((SEAM, 104), (SEAM, TOP + 6 * STEP - 4), color="ink-muted", dash="lead")
for k, (n, left, right, role) in enumerate(ROWS):
    y = TOP + k * STEP
    a = card(LX, y, n, left, role)
    if right:
        b = card(RX, y, n, right, role)
        fig.arrow((a.right, y + H / 2), (b.x, y + H / 2))
for k, (n, name, role) in enumerate(CUSTOM_ONLY):
    card(RX, TOP + (3 + k) * STEP, n, name, role)
fig.text(LX, TOP + 6 * STEP + 20, "The mechanism is inherited.", "note")
fig.text(RX, TOP + 6 * STEP + 20, "The policy is the team's.", "note")
fig.write()
