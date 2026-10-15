"""Post 15, section 10: the measured cost of asking, drawn from the cited numbers only.

Run from the series root:  uv run python posts/15-human-in-the-loop/diagrams/src/04-cost-of-asking.py
Writes posts/15-human-in-the-loop/diagrams/04-cost-of-asking.svg.
A chart in the form of hrn_fig_design.md section 5: every value is cited, so every bar is hollow and carries the
word "cited". Source, one table below, each value asserted against the body's quotation: Anthropic, "Auto mode is
now the default in Claude Code for Pro, Max, and Team plans", 7 August 2026 (REFERENCES.md, post 15). The study
gives no number for the classifier's within-session rate, only that it "stayed flat", so none is drawn.
Roles: none; these are neutral quantities about people and a classifier, drawn in ink.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")

CITED = {   # value in percent: the body's quotation of the source
    "humans caught": (13.6, "just 13.6% of the time (143 of 1,053)"),
    "classifier blocked": (89, "blocked 89% of the same commands (937 of 1,053)"),
    "early in a session": (17, "blocked about 17% of dangerous commands early in a session"),
    "after 50+ prior prompts": (5, "dropping to about 5% after 50 or more prior prompts"),
}
for _, (v, quote) in CITED.items():
    assert quote in BODY, quote
assert "auto mode's block rate stayed flat regardless of session length" in BODY
assert round(143 / 1053 * 100, 1) == 13.6 and round(937 / 1053 * 100) == 89

fig = Figure(
    "04-cost-of-asking", "Asked often enough, people stop catching it",
    "Two panels of cited values, drawn as hollow bars. Left, the same 1,053 planted dangerous commands: human "
    "testers caught 13.6 percent, 143 of them, and the classifier blocked 89 percent, 937. Right, the human block "
    "rate on dangerous commands: about 17 percent early in a session and about 5 percent after 50 or more prior "
    "prompts; the classifier's rate stayed flat, and the study gives no number for it.",
    subtitle="Cited: Anthropic, \"Auto mode is now the default in Claude Code\", 7 August 2026; the vendor's own study.",
    data_w=True)

def panel(x0, w, heading, rows, hi, ticks, unit_note):
    fig.text(x0, 120, heading, "head")
    lx, bx = x0, x0 + 176             # labels, then the bars
    bw = w - 176 - 72
    for i, (label, v, value) in enumerate(rows):
        y = 184 + 104 * i
        fig.text(lx, y + 4, label, "label")
        with fig.data():
            fig.outline(Box(bx, y - 20, bw * v / hi, 40), "ink", width=1.5, dash="proj")
        fig.text(bx + bw * v / hi + 8, y + 4, value, "value", color="ink")
    ay = 184 + 104 * len(rows) - 32
    fig.edge((bx, ay), (bx + bw, ay), color="ink-muted", width=1)
    for t in ticks:
        tx = bx + bw * t / hi
        with fig.data():
            fig.edge((tx, ay), (tx, ay + 4), color="ink-muted", width=1)
        fig.text(tx, ay + 24, f"{t}%", "tick", anchor="middle")
    fig.text(lx, ay + 56, unit_note, "note")
    return ay

L = panel(40, 432, "The same 1,053 planted commands",
          [("humans caught", 13.6, "13.6%, 143"), ("classifier blocked", 89, "89%, 937")],
          100, [0, 50, 100], "share caught or blocked, cited")
R = panel(504, 416, "Human block rate within a session",
          [("early in a session", 17, "about 17%"), ("after 50+ prompts", 5, "about 5%")],
          20, [0, 10, 20], "dangerous commands blocked, cited")
fig.text(504, 444, "the classifier's rate stayed flat; no number given", "note")

fig.caption("Hollow, dashed bars: cited values, graded controlled (the vendor's own study), not measured here.")
fig.write()
