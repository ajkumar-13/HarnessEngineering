"""Post 01, section 4: the four layers of the vocabulary as concentric rings, with what each holds and who
engineers it.

Run from the series root:  uv run python posts/01-from-context-to-harness/diagrams/src/02-nested-rings.py
Writes posts/01-from-context-to-harness/diagrams/02-nested-rings.svg.
The rings are the one nesting the series teaches and are drawn once, here (hrn_fig_design.md section 4). The
model is the only ring in a role colour (model, blue); the scaffold, the harness and orchestration are neutral,
told apart by alternating neutral fills and by their names. The words in the table are section 4's definitions,
shortened; each is asserted against the body. No numbers are drawn.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, Box  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# ring, what it holds (section 4), who engineers it (sections 3, 4 and 7), phrases the body must contain
RINGS = [
    ("orchestration", "several agents as units", "this series, Part IV",
     ("coordinates several agents as units", "Multi-agent systems (Part IV) are an orchestration concern")),
    ("harness", "the loop that drives the model", "harness engineering",
     ("the runtime that drives the model", "**Harness engineering.** The discipline")),
    ("scaffold", "what the model sees", "context engineering",
     ("shapes *what the model sees", "Context engineering works on the scaffold ring")),
    ("model", "text in, text out", "outside this series",
     ("text in, text out", "**The model is outside it.**")),
]
for _, _, _, phrases in RINGS:
    for phrase in phrases:
        assert phrase in BODY, phrase

fig = Figure(
    "02-nested-rings", "Each layer wraps the one inside it",
    "Four concentric rings: the model at the centre in blue, then the scaffold, the harness and orchestration in "
    "alternating neutral fills, each named in its band. A table beside them gives each ring, what it holds and "
    "who engineers it: orchestration, several agents as units, this series in Part IV; harness, the loop that drives the model, "
    "harness engineering; scaffold, what the model sees, context engineering; model, text in, text out, outside "
    "this series. The caption: a harness drives one model through its loop; an orchestrator manages many agents.",
    subtitle="The four layers of section 4, from the outside in, and the discipline that engineers each.",
    data_w=True)

CX, CY = 224, 292
RADII = [184, 140, 96, 52]
FILLS = ["neutral-soft", "surface", "neutral-soft", "model-soft"]
LINES = ["rule", "rule", "rule", "model"]
for r, f, line in zip(RADII, FILLS, LINES):
    b = Box(CX - r, CY - r, 2 * r, 2 * r)
    fig.fill(b, f, radius=r)
    fig.outline(b, line, width=1.5 if line == "model" else 1, radius=r)
for (name, *_), r in zip(RINGS[:3], RADII[:3]):
    fig.text(CX, CY - r + 28, name, "label", anchor="middle", bold=True)
fig.text(CX, CY + 5, "model", "label", anchor="middle", bold=True)

rows = [["Ring", "What it holds", "Engineered by"]] + [[n, h, e] for n, h, e, _ in RINGS]
fig.table(440, CY - 120, rows, [112, 208, 160], row_h=48)

assert "A harness drives one model through its loop; an orchestrator manages many agents." in BODY
fig.caption("A harness drives one model through its loop; an orchestrator manages many agents.")
fig.write()
