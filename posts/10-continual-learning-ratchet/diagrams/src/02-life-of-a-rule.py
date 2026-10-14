"""Post 10, section 7: the life of a rule, from a failure to the day it leaves the file.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/diagrams/src/02-life-of-a-rule.py
Writes posts/10-continual-learning-ratchet/diagrams/02-life-of-a-rule.svg.
A timeline in the form of hrn_fig_design.md section 4, with stages in place of dates (the post states no dates for
a rule's life; the provenance note's issue id and date are the illustrative ones of section 3). The stages are the
post's: the failure (section 4), the rule and check staged by propose_rule() (section 4), the reviewed root cause a
person accepts (section 7), the three teeth (sections 4 and 5), the hook's firing rate per rule id (section 10),
and pruning, including the model-upgrade trigger (section 9). Each is asserted against the body. Roles: the failure
red, staged and permanent files green (state), review and enforcement purple (gates), watching and pruning neutral.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
PROVENANCE = "[#455, 2026-06-08]"
for phrase in (
    "a pull request (PR) with a commented-out test, merged by accident",
    "The helper writes the proposed rule to a staging file",
    "Having the agent *propose* rules and a person accept them",
    "**A rule needs a reviewed root cause, not a plausible one.**",
    "Three independent layers from one failure",
    "tagged with the rule's id",
    "The firing rate per rule, sorted, *is* the prune list",
    "**Retire rules a better model made redundant.**",
    "a model upgrade is a discrete, dated event, the natural trigger for a memory-file review",
    "Never comment out tests; delete them or fix them. " + PROVENANCE,
    "Provenance is also what makes pruning possible at all",
):
    assert phrase in BODY, phrase

fig = Figure(
    "02-life-of-a-rule", "Most of a rule's life happens outside the teeth",
    "A timeline of six stages from left to right. 1 failure, in red: a commented-out test is merged. 2 proposed, in "
    "green: the agent stages a rule and a check. 3 accepted, in purple: a person reviews the root cause. 4 "
    "enforced, in purple: the memory line, the hook and the reviewer check. 5 watched: the hook's firing rate, "
    "counted per rule. 6 pruned: obsolete, or redundant after a model upgrade. Braces group stages 1 to 3 as "
    "earning the rule, stage 4 as the teeth, and stages 5 and 6 as watching and pruning. A green bar under stages "
    "3 to 6 is the provenance note, issue 455 of 8 June 2026, written at review and read when pruning.",
    subtitle="Nothing in the loop removes a rule; a person adds it after review and removes it with evidence.",
    data_w=True)

STAGES = [
    ("failure", "error", ["a commented-out", "test is merged"]),
    ("proposed", "state", ["the agent stages", "a rule and a check"]),
    ("accepted", "gate", ["a person reviews", "the root cause"]),
    ("enforced", "gate", ["memory line, hook", "and reviewer check"]),
    ("watched", None, ["the hook's firing", "rate, per rule id"]),
    ("pruned", None, ["obsolete, or made", "redundant by a", "model upgrade"]),
]
COL = 144
cx = [112 + COL * i for i in range(len(STAGES))]
AXIS = 232

# the groups, over the stages
fig.brace(56, 456, 152, label="earning the rule", side="above")
fig.brace(488, 600, 152, label="the teeth", side="above")
fig.brace(632, 904, 152, label="watching and pruning", side="above")

# the time axis, left to right, then one node per stage
fig.arrow((40, AXIS), (920, AXIS))
for i, (name, role, lines) in enumerate(STAGES):
    fig.text(cx[i], 200, f"{i + 1}  {name}", "head", anchor="middle", color=role)
    fig.node(cx[i], AXIS, r=12, color=role)
    for k, s in enumerate(lines):
        fig.text(cx[i], 280 + 24 * k, s, "label", anchor="middle")

# the provenance note travels with the rule from review to pruning
px, pw = cx[2] - 64, cx[5] + 72 - (cx[2] - 64)
fig.card(px, 376, pw, 56, color="state")
fig.text(px + 16, 408, PROVENANCE, "code")
fig.text(px + 192, 408, "the provenance note: written at review, read when pruning", "label")

fig.caption("Without the note, a rule can never be safely removed, so the file only grows.")
fig.write()
