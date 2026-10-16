"""Post 25, section 10: three defects beside a green suite (hrn_fig_design.md section 3).

Run from the series root:  uv run python posts/25-build-harness-plus/diagrams/src/03-what-tests-miss.py
Writes posts/25-build-harness-plus/diagrams/03-what-tests-miss.svg.

One row per defect the section tells: the layer, what the suite asserted (a gate, purple: it passed), the defect
in the neighbouring property (red), and the gap. The words are the post's. The two facts the figure states about
the code are asserted against the companion: the runner takes an argv list with shell=False, the dispatcher tags
a sandbox refusal "refused", and the default deny-list still lets the respelled commands through.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, Box  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "code" / "25-harness-plus" / "src" / "harness_plus"
sys.path.insert(0, str(SRC.parent))
from harness_plus import deny_list  # noqa: E402

assert "shell=False" in (SRC / "sandbox.py").read_text(encoding="utf-8")
assert 'outcome = "refused" if observation.startswith("blocked:")' in (SRC / "harness.py").read_text(encoding="utf-8")
hook = deny_list()
for cmd in ("rm -fr /", "git push -f origin main"):
    assert hook("bash", {"command": cmd}).allow, cmd

ROWS = [
    ("sandbox allow-list", "fixed", ["refusals and allowances", "it was meant to make"],
     ["a shell ran the raw string,", "so one echo ran two commands"], ["expected traffic only"]),
    ("tracer", "fixed", ["the shape of the", "span tree"],
     ["every sandbox refusal", "was tagged ok"], ["shape, never contents"]),
    ("deny-list hook", "still in the code", ["the phrases the patterns", "were written from"],
     ["rm -fr / and git push -f", "walk past it"], ["its own source"]),
]

fig = Figure(
    "03-what-tests-miss", "Each test passed; each defect sat next door",
    "Three rows, one per defect, with four columns: the layer, what the suite asserted and passed, the defect in "
    "the neighbouring property, and the gap. Sandbox allow-list, fixed: the tests asserted refusals and "
    "allowances; a shell ran the raw string, so one echo ran two commands; expected traffic only. "
    "Tracer, fixed: the tests asserted the shape of the span tree; every sandbox refusal was tagged ok; shape, "
    "never contents. Deny-list hook, still in the code: the tests sent the phrases the patterns were written "
    "from; rm -fr / and git push -f walk past it; its own source.",
    subtitle="The three defects of code/25-harness-plus that a green suite could not see.",
    data_w=True)

COLS = [(40, 176), (232, 232), (480, 248), (744, 176)]
HEADS = ["layer", "the suite asserted", "the defect next to it", "the gap"]
for (x, _), head in zip(COLS, HEADS):
    fig.text(x, 132, head, "head")
for k, (layer, status, asserted, defect, gap) in enumerate(ROWS):
    y = 152 + k * 104
    fig.text(COLS[0][0], y + 32, layer, "label", bold=True)
    fig.text(COLS[0][0], y + 56, status, "note")
    for (x, w), lines, role in ((COLS[1], asserted, "gate"), (COLS[2], defect, "error")):
        b = Box(x, y, w, 80)
        fig.fill(b, f"{role}-soft", radius=8)
        fig.outline(b, f"{role}-line" if role == "gate" else role, radius=8)
        for i, line in enumerate(lines):
            fig.text(x + 16, y + 32 + 24 * i, line, "label")
    fig.text(COLS[3][0], y + 44, gap[0], "label")
fig.caption("A test written from the same text as the code can only confirm the text was copied.")
fig.write()
