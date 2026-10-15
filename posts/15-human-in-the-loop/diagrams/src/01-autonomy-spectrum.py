"""Post 15, hero: four stops on the autonomy spectrum, chosen per action rather than per agent.

Run from the series root:  uv run python posts/15-human-in-the-loop/diagrams/src/01-autonomy-spectrum.py
Writes posts/15-human-in-the-loop/diagrams/01-autonomy-spectrum.svg.
The four stops and what the human becomes at each are section 1's table; the five actions and their stops are
section 1's per-action rule and section 2's two axes (reversibility, visibility). Each is asserted against the body.
Roles (hrn_fig_design.md section 0): the approve stop and the gated actions are purple (an approval is a gate the
human decides); the human and the other stops are neutral. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in (
    "| **Suggest** | Proposes an action; does not take it | The operator, doing the work |",
    "| **Approve** | Acts, but only after a decision on each action | The approver, in front of every artefact |",
    "| **Act and notify** | Acts on its own; only the irreversible is gated | The supervisor, watching and able to interrupt |",
    "| **Autonomous** | Acts; the work is reviewed afterwards | The observer, reading the result |",
    "choose the row **per action, not per agent**",
    "runs tests, edits files and reads logs at the autonomous row, because those are reversible",
    "Opening a pull request (PR) is technically reversible",
    "A deploy, a delete against production data",
):
    assert phrase in BODY, phrase

fig = Figure(
    "01-autonomy-spectrum", "Choose the stop per action, not per agent",
    "Four cards on an axis from less autonomy to more. Suggest: the agent proposes and does not act; the human is "
    "the operator. Approve, drawn as a gate: the agent acts after a decision on each action; the human is the "
    "approver. Act and notify: the agent acts and only the irreversible is gated; the human is the supervisor. "
    "Autonomous: the agent acts and the work is reviewed afterwards; the human is the observer. Below, a table of "
    "one coding agent's five actions: read the logs, run the tests and edit the working tree are autonomous because "
    "a checkpoint undoes them; open a pull request needs approval because others see it first; deploy to "
    "production needs approval because it cannot be undone.",
    subtitle="What the human becomes at each stop, and where one coding agent's actions land.",
    data_w=True)

# the axis
AY = 112
fig.arrow((40, AY), (920, AY))
fig.text(40, AY - 8, "less autonomy", "note")
fig.text(920, AY - 8, "more autonomy", "note", anchor="end")

STOPS = [
    ("Suggest", None, ["proposes an action,", "does not take it"], "the operator"),
    ("Approve", "gate", ["acts after a decision", "on each action"], "the approver"),
    ("Act and notify", None, ["acts; only the", "irreversible is gated"], "the supervisor"),
    ("Autonomous", None, ["acts; the work is", "reviewed afterwards"], "the observer"),
]
CW, CY, CH = 208, 128, 128
for i, (name, role, lines, human) in enumerate(STOPS):
    x = 40 + i * (CW + 16)
    fig.card(x, CY, CW, CH, color=role)
    fig.text(x + 16, CY + 28, name, "head", color=role)
    for k, s in enumerate(lines):
        fig.text(x + 16, CY + 56 + 20 * k, s, "label")
    fig.text(x + 16, CY + 108, "human:", "note")
    fig.text(x + 72, CY + 108, human, "label", bold=True)

# one agent, five actions, each placed on its own stop
fig.text(40, 288, "One coding agent: the stop is chosen for each action", "head")
rows = [
    ["action", "its stop", "why"],
    ["read the logs", "autonomous", "reversible"],
    ["run the tests", "autonomous", "reversible"],
    ["edit the working tree", "autonomous", "reversible: a checkpoint undoes it"],
    ["open a pull request", "approve", "visible: others see it before it can be undone"],
    ["deploy to production", "approve", "irreversible: no rollback undoes it"],
]
fig.table(40, 304, rows, [272, 176, 432], row_h=28, highlight_row={4: "gate", 5: "gate"})

fig.caption("Pinning a whole agent to one stop wastes attention on safe actions or gives away the dangerous ones.")
fig.write()
