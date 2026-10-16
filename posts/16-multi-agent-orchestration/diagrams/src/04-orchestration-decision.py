"""Post 16, section 9: the decision framework as three gates, with the single agent as the fall-through.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/diagrams/src/04-orchestration-decision.py
Writes posts/16-multi-agent-orchestration/diagrams/04-orchestration-decision.svg.
A section 3 gate form of hrn_fig_design.md: each question is a gate (purple) in the order the post states them; a
"no" at any gate falls through to the single agent, the default; a "yes" at all three reaches orchestration, which
carries the two follow-on rules; isolation enters orchestration from the side without passing the gates. The
single agent, orchestration and isolation are neutral cards (design choices, not roles). The wording is the post's,
asserted below. There are no numbers in this figure.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("the subtasks are genuinely independent, the context fragmentation is acceptable, and the gain covers "
               "the coordination cost",
               "A \"no\" to any one of them sends the design back to one agent with sub-tasks",
               "Keep writes single-threaded unless the machinery of",
               "settle the partial-failure policy in the same design session that chooses the topology",
               "Isolation is the one exception that skips the gates entirely"):
    assert phrase in BODY, phrase

fig = Figure(
    "04-orchestration-decision", "Three gates stand between a task and a second agent",
    "A task meets three purple gates in order: are the subtasks independent and parallel; is the fragmentation "
    "acceptable; does the gain cover the coordination tax. A no at any gate falls through to one agent with "
    "sub-tasks, the default. A yes at all three reaches orchestration, which carries two rules: one writer unless "
    "the claiming and worktrees of post 17 exist, and a partial-failure policy chosen before dispatch. Isolation "
    "enters orchestration from above without passing the gates, because it buys containment, not throughput.",
    subtitle="A no at any gate keeps the work on one agent; isolation is the one shape bought without them.",
    data_w=True)


def lines(x, y, rows, style="label", anchor="middle", color=None):
    for i, r in enumerate(rows):
        fig.text(x, y + 24 * i, r, style, anchor=anchor, color=color)


GY, GH, GW = 224, 72, 168
fig.card(40, 236, 88, 48)
fig.text(84, 264, "a task", "label", anchor="middle")
gates = [(160, ["subtasks independent", "and parallel?"]),
         (360, ["fragmentation", "acceptable?"]),
         (560, ["gain covers the", "coordination tax?"])]
prev = (128, 260)
for x, words in gates:
    fig.card(x, GY, GW, GH, color="gate")
    lines(x + GW // 2, GY + 32, words)
    fig.arrow(prev, (x, 260), label="yes" if prev[0] != 128 else None)
    prev = (x + GW, 260)
    fig.arrow((x + GW // 2, GY + GH), (x + GW // 2, 376), label="no", side="right")

# the yes at all three
OX, OW = 776, 144
fig.arrow(prev, (OX, 260), label="yes")
fig.card(OX, GY, OW, GH)
lines(OX + OW // 2, GY + 44, ["orchestrate"])
fig.text(OX, 328, "with two rules:", "note")
lines(OX, 356, ["1. one writer, unless", "post 17's machinery"], anchor="start")
lines(OX, 412, ["2. failure policy fixed", "before dispatch"], anchor="start")

# isolation, from the side
fig.card(OX, 116, OW, 64)
lines(OX + OW // 2, 144, ["isolation, for", "containment only"])
fig.arrow((OX + OW // 2, 180), (OX + OW // 2, GY), dash="proj")

# the fall-through
fig.card(160, 376, 568, 56)
fig.outline(Box(160, 376, 568, 56), "ink", width=2.5, radius=8)
lines(444, 410, ["one agent with sub-tasks: the default"])

fig.caption("The tax is paid on every run; the gain only on the runs whose work really was parallel.")
fig.write()
