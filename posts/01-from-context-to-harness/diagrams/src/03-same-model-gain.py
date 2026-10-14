"""Post 01, section 5: one model, two harnesses, on Terminal-Bench 2.0.

Run from the series root:  uv run python posts/01-from-context-to-harness/diagrams/src/03-same-model-gain.py
Writes posts/01-from-context-to-harness/diagrams/03-same-model-gain.svg.
Both values are cited, not run: Trivedy, "Improving Deep Agents with harness engineering" (LangChain blog,
17 February 2026), as section 5 of index.md states them. They are drawn as hollow marks with the word "cited"
and the grade written beside the gain (hrn_fig_design.md section 5). The task equivalents (about 47 and about 59
of 89) and the gain are computed here from the cited rates and asserted against the body.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

# label, cited resolve rate in %, rank as the source words it; source: Trivedy, LangChain, 17 February 2026
CITED = [("default harness", 52.8, "just outside the top 30"), ("tuned harness", 66.5, "the top 5")]
TASKS = 89
gain = round(CITED[1][1] - CITED[0][1], 1)
equiv = [round(rate / 100 * TASKS) for _, rate, _ in CITED]
assert gain == 13.7 and equiv == [47, 59]
for phrase in ("from 52.8% to 66.5% on Terminal-Bench 2.0, a gain of 13.7 points",
               "with the model held fixed at `gpt-5.2-codex`", "from just outside the top 30 into the top 5",
               "has 89 human-verified tasks", "the equivalent of about 47 tasks and 66.5% of about 59",
               "\"Improving Deep Agents with harness engineering\" (17 February 2026)", "(firm)"):
    assert phrase in BODY, phrase

fig = Figure(
    "03-same-model-gain", "Only the harness changed, and the score rose 13.7 points",
    "Two rows on a resolve-rate axis from 40 to 80% on Terminal-Bench 2.0, for one model, gpt-5.2-codex. Both "
    "values are hollow cited marks. The default harness scores 52.8%, about 47 of 89 tasks, just outside the top "
    "30; the tuned harness scores 66.5%, about 59 of 89 tasks, in the top 5. A dotted line carries 52.8% down to "
    "the second row, and a bracket over the first row marks the gain of 13.7 points, graded firm. The caption "
    "says every change was to the harness around the model.",
    subtitle="Model held fixed at gpt-5.2-codex. Cited: Trivedy, LangChain, 17 February 2026.",
    data_w=True)

body = fig.panel(fig.row(1, y=136, h=320)[0])
ax = fig.dot_plot(body, [(label, [rate]) for label, rate, _ in CITED], 40, 80, [40, 50, 60, 70, 80],
                  colors=("ink",), hollow=True, unit="%", values=True, label_w=160, pad_right=24,
                  fmt_tick=lambda v: f"{v:g}", fmt_value=lambda v: f"{v:.1f}",
                  axis_label="resolve rate on Terminal-Bench 2.0, 89 tasks")
for i, ((_, rate, rank), n) in enumerate(zip(CITED, equiv)):
    with fig.data():
        fig.text(ax.sx(rate) + 10, ax.sy(i) + 29, f"about {n} of {TASKS} tasks, {rank}", "note", snap=False)
# the default harness's score carried down to the second row, so the gap reads on one line
with fig.data():
    fig.edge((ax.sx(CITED[0][1]), ax.sy(0) + 12), (ax.sx(CITED[0][1]), ax.bottom), color="ink-muted", dash="ref")
    fig.brace(ax.sx(CITED[0][1]), ax.sx(CITED[1][1]), ax.sy(0) - 16, label=f"+{gain} points, cited, firm",
              side="above")
fig.legend(body.x, ax.bottom + 20, [dict(color="ink", label="cited value", mark="circle", hollow=True)],
           direction="row")
assert "No model change, 13.7 points." in BODY
fig.caption("Same model, same 89 tasks: every change was to the harness around the model.")
fig.write()
