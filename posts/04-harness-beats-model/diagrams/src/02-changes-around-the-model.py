"""Post 04, section 2: where each of LangChain's harness changes acts on one Terminal-Bench run.

Run from the series root:  uv run python posts/04-harness-beats-model/diagrams/src/02-changes-around-the-model.py
Writes posts/04-harness-beats-model/diagrams/02-changes-around-the-model.svg.
The changes, their names and the reasoning settings are Trivedy's, "Improving Deep Agents with harness engineering"
(LangChain blog, 17 February 2026), read at the source on 2026-10-14 and asserted against the table in index.md.
The figure shows no measured number. Roles (hrn_fig_design.md section 0): the model's reasoning per phase is blue;
the checks on the run (the pre-completion checklist at the exit, loop detection on edits) are gates, purple; the
system prompt, the injected local context and the time-budget warnings are neutral harness parts.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

BODY = (Path(__file__).resolve().parents[2] / "index.md").read_text(encoding="utf-8")

PHASES = [("plan and discover", "xhigh"), ("build", "high"), ("verify and fix", "xhigh")]
for phrase in ("planning and discovery, build, verify, fix", "`PreCompletionChecklistMiddleware`",
               "`LocalContextMiddleware`", "`LoopDetectionMiddleware`", "Injected time-budget warnings",
               "An \"xhigh-high-xhigh\" reasoning sandwich", "Prompting for testable code",
               "keeping the model fixed at `gpt-5.2-codex`", "this series counts seven"):
    assert phrase in BODY, phrase

fig = Figure(
    "02-changes-around-the-model", "Seven changes, all around a model that never changed",
    "One Terminal-Bench run drawn left to right. A neutral bar over the whole run is the system prompt, which gained "
    "a build-verify loop and guidance for testable code. Three blue phase cards, plan and discover, build, and verify "
    "and fix, carry the reasoning setting of each, xhigh, high and xhigh. A purple gate at the exit is the "
    "pre-completion checklist. Below, local context acts at the start, loop detection, purple, on repeated edits "
    "during the build, and time-budget warnings injected as the run goes. A blue bar at the bottom is the model, "
    "gpt-5.2-codex, unchanged. No numbers are shown.",
    subtitle="deepagents-cli on Terminal-Bench 2.0; the changes as Trivedy lists them, 17 February 2026.",
    data_w=True)

X0, RUN_R = 40, 776                      # the run spans X0..RUN_R; the exit gate sits right of it
PW, GAP = 216, 44                        # phase card width and gap
fig.card(X0, 112, RUN_R - X0, 48, lines=["system prompt: a build-verify loop, and testable code"])

phase_boxes = []
for k, (name, effort) in enumerate(PHASES):
    x = X0 + k * (PW + GAP)
    fig.card(x, 192, PW, 88, heading=name, lines=[f"reasoning: {effort}"], color="model")
    phase_boxes.append(Box(x, 192, PW, 88))
fig.chain(phase_boxes)

# the exit, gated by the pre-completion checklist
GX, GY = 840, 236
fig.arrow(phase_boxes[-1].anchor("right"), (GX - 14, GY))
with fig.data():
    fig.marker(GX, GY, "diamond", "gate", size=24)
fig.text(GX, GY - 28, "exit", "label", anchor="middle")
fig.text(GX, GY + 44, "pre-completion", "label", anchor="middle", color="gate")
fig.text(GX, GY + 64, "checklist", "label", anchor="middle", color="gate")

# middleware that acts during the run
fig.card(X0, 320, PW, 72, lines=["local context: maps the", "directories, finds the tools"], leading=20)
fig.leader((X0 + PW / 2, 320), (X0 + PW / 2, 280))
lx = X0 + PW + GAP
fig.card(lx, 320, PW, 72, lines=["loop detection: N edits to", "one file prompt a rethink"], color="gate",
         leading=20)
fig.leader((lx + PW / 2, 320), (lx + PW / 2, 280))
fig.card(X0 + 2 * (PW + GAP), 320, PW, 72, lines=["time-budget warnings,", "injected as the run goes"],
         leading=20)

# the model, the one thing held fixed
fig.card(X0, 428, RUN_R - X0, 48, lines=["model: gpt-5.2-codex, the same weights before and after"], color="model")
fig.caption("Every change acts on the prompt, the middleware or the run settings; none on the weights.")
fig.write()
