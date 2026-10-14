"""Post 04, the hero: every graded result holds one model fixed and moves its score; the reported multiple has no point.

Run from the series root:  uv run python posts/04-harness-beats-model/diagrams/src/01-graded-evidence.py
Writes posts/04-harness-beats-model/diagrams/01-graded-evidence.svg.
Every value is cited, not run, and was read at its source on 2026-10-14:
  Trivedy, "Improving Deep Agents with harness engineering", LangChain blog, 17 February 2026: 52.8% to 66.5%.
  Trivedy and Daugherty, "Tuning Deep Agents to Work Well with Different Models", LangChain blog, 29 April 2026:
    a curated subset of harder tau2-bench tasks, GPT-5.3-Codex 33% to 53%, Claude Opus 4.7 43% to 53%.
  Yang et al., "SWE-agent", NeurIPS 2024, Table 1: SWE-bench Lite with GPT-4 Turbo, shell-only 11.00%, SWE-agent 18.00%.
  Starace, "Scaffold Effects on GAIA", 7 June 2026, section 5: Opus Level 2, robust slice, ReAct 0.56, PAR 0.84.
  MindStudio, "What Is Harness Engineering?", 8 May 2026: "up to 6x", no model, benchmark or base named.
Cited values are hollow marks with the word "cited" (hrn_fig_design.md section 5); the grade is written as a word
beside each row, never as colour. Each row is one model: the rows sit on one axis but are different benchmarks.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# label, source as the figure names it, (weaker, stronger) in %, printed forms, grade
CITED = [
    ("Terminal-Bench 2.0, gpt-5.2-codex", "Trivedy, 17 February 2026", (52.8, 66.5), ("52.8%", "66.5%"), "firm"),
    ("τ²-bench subset, GPT-5.3-Codex", "Trivedy and Daugherty, 29 April 2026", (33, 53), ("33%", "53%"), "firm"),
    ("τ²-bench subset, Claude Opus 4.7", "Trivedy and Daugherty, 29 April 2026", (43, 53), ("43%", "53%"), "firm"),
    ("SWE-bench Lite, GPT-4 Turbo", "Yang et al., 2024", (11.0, 18.0), ("11.0%", "18.0%"), "controlled"),
    ("GAIA Level 2, Claude Opus 4.7", "Starace, 7 June 2026", (56, 84), ("56%", "84%"), "controlled"),
]
REPORTED = ("up to 6x, same model", "MindStudio, 8 May 2026", "reported")

for phrase in ("from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points",
               "keeping the model fixed at `gpt-5.2-codex`",
               "moved GPT-5.3-Codex from 33% to 53% and Claude Opus 4.7 from 43% to 53%",
               "the ACI resolved 18.0% against 11.0%", "with GPT-4 Turbo held fixed",
               "planner-actor-rater scored 84% and ReAct 56%", "The cell is Claude Opus 4.7 at Level 2",
               "performance gaps of up to 6x", "names no model, no benchmark and no baseline",
               "\"Improving Deep Agents with harness engineering\" (LangChain blog, 17 February 2026)",
               "(LangChain blog, 29 April 2026)", "(7 June 2026)", "(8 May 2026)",
               "This is the firm grade", "That is firm", "This is the controlled grade", "That is controlled",
               "It is reported"):
    assert phrase in BODY, phrase
assert round(CITED[0][2][1] - CITED[0][2][0], 1) == 13.7 and CITED[4][2][1] - CITED[4][2][0] == 28
assert round(CITED[3][2][1] / CITED[3][2][0] - 1, 2) == 0.64          # the paper's "64% relative increase"

fig = Figure(
    "01-graded-evidence", "Hold the model fixed, and the harness moves the score",
    "A dot plot on a 0 to 100% axis, one row per cited result, each row one model under a weaker harness, a hollow "
    "circle, and a stronger harness, a hollow diamond. Terminal-Bench 2.0 with gpt-5.2-codex, 52.8% to 66.5%, firm "
    "(Trivedy, 17 February 2026). A tau-squared-bench subset with GPT-5.3-Codex, 33% to 53%, and with Claude Opus "
    "4.7, 43% to 53%, both firm (Trivedy and Daugherty, 29 April 2026). SWE-bench Lite with GPT-4 Turbo, 11.0% to "
    "18.0%, controlled (Yang et al., 2024). GAIA Level 2 with Claude Opus 4.7, 56% to 84%, controlled (Starace, "
    "7 June 2026). A last row, up to 6x for the same model, reported (MindStudio, 8 May 2026), has no marks: no "
    "model, benchmark or base is given. The caption warns that the rows are different benchmarks.",
    subtitle="Cited results, each row one model under two harnesses. Grades as this post defines them.",
    height=720, data_w=True)

box = fig.row(1, y=128, h=480)[0]
rows = [(label, list(vals)) for label, _, vals, _, _ in CITED] + [(REPORTED[0], [])]
ax = fig.dot_plot(box, rows, 0, 100, [0, 20, 40, 60, 80, 100], colors=("ink-muted", "ink"),
                  shapes=("circle", "diamond"), hollow=True, unit="%", label_w=264, pad_right=136,
                  fmt_tick=lambda v: f"{v:g}", axis_label="score of the same model under each harness, cited")
GRADE_X = ax.right + 40
with fig.data():
    fig.text(GRADE_X, ax.y - 8, "grade", "note", snap=False)
    for i, (_, source, (lo, hi), (lo_s, hi_s), grade) in enumerate(CITED):
        cy = ax.sy(i)
        fig.text(box.x, cy + 25, source, "note", snap=False)
        fig.text(ax.sx(lo) - 10, cy + 5, lo_s, "value", anchor="end", color="ink-muted", snap=False)
        fig.text(ax.sx(hi) + 10, cy + 5, hi_s, "value", color="ink", snap=False)
        fig.text(GRADE_X, cy + 5, grade, "label", bold=True, snap=False)
    cy = ax.sy(len(CITED))
    fig.text(box.x, cy + 25, REPORTED[1], "note", snap=False)
    fig.text(ax.sx(2), cy + 5, "no model, benchmark or base: nothing to plot", "note", snap=False)
    fig.text(GRADE_X, cy + 5, REPORTED[2], "label", bold=True, snap=False)
fig.legend(box.x, ax.bottom + 76,
           [dict(color="ink-muted", label="weaker harness, cited", mark="circle", hollow=True),
            dict(color="ink", label="stronger harness, cited", mark="diamond", hollow=True)], direction="row")
fig.caption("Each row is its own benchmark: compare a row's two marks, not one row with another.")
fig.write()
