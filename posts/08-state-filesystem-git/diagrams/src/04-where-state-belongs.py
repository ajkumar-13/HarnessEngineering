"""Post 08, section 9: where a piece of state belongs, decided by when it is needed and then by how it is read.

Run from the series root:  uv run python posts/08-state-filesystem-git/diagrams/src/04-where-state-belongs.py
Writes posts/08-state-filesystem-git/diagrams/04-where-state-belongs.svg.
Five regions side by side (hrn_fig_design.md section 3 form): the window as a neutral card, the four stores on
disk as state cards. Every rule and example is a phrase of the post's body (sections 2, 4, 8 and 9), asserted
below. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
for phrase in ("If the model needs it *this turn and every turn*, it belongs in the prompt",
               "Whole reads want a file; queries want an index.", "| Access pattern | read whole | queried over structured rows | queried by similarity |",
               "| Concurrent writers | one; more needs one file per writer | many, serialised by the database | many |",
               "retrieval over a corpus too large to read whole", "**checkpoint after each verified step; revert on error.**",
               "A one-line rule the model must honour on every turn belongs in the window",
               "Write them to `scratch/build.log` and return a *pointer*", "Pasting a 2,000-line log into the transcript",
               "so the agent spends its turns doing filesystem bookkeeping"):
    assert phrase in BODY, phrase

REGIONS = [
    ("window", "needed this turn", ["and every turn:", "the task, the rules,", "pointers to the rest"], None),
    ("files", "read whole", ["plans, offloaded", "output, artefacts,", "the handoff"], "state"),
    ("git", "a point to return to", ["a checkpoint after", "each verified step"], "state"),
    ("SQLite", "queried rows", ["many writers,", "transactions,", "still one file"], "state"),
    ("index", "queried by similarity", ["a corpus too large", "to read whole"], "state"),
]

fig = Figure(
    "04-where-state-belongs", "State goes where it is needed, read the way it is read",
    "Five regions side by side. The window, drawn neutral, holds what is needed this turn and every turn: the task, "
    "the rules, and pointers to the rest. Four green regions on disk follow: files, read whole, "
    "for plans, offloaded output, artefacts and the handoff; git, a point to return to, a checkpoint after each "
    "verified step; SQLite, queried rows, many writers, transactions, still one file; an index, queried by "
    "similarity, for a corpus too large to read whole. Below, in red, the two mirror-image mistakes: a pasted log "
    "in the window that belongs on disk, and a rule behind a file read that belongs in the window.",
    subtitle="First ask when it is needed; if not every turn, the access pattern picks the store on disk.",
    data_w=True)

xs = [40 + k * 180 for k in range(5)]
fig.text(xs[0], 132, "in the window", "head")
fig.brace(xs[1], xs[4] + 160, 140, label="on disk", side="above")
for x, (name, rule, lines, role) in zip(xs, REGIONS):
    fig.card(x, 160, 160, 184, color=role)
    fig.text(x + 16, 192, name, "head")
    fig.text(x + 16, 220, rule, "label", color=None if role is None else "state")
    for k, line in enumerate(lines):
        fig.text(x + 16, 252 + 24 * k, line, "note")
MISTAKES = [("in the window, belongs on disk", "a pasted log: bloats every call, dies at a reset"),
            ("on disk, belongs in the window", "a rule behind a read: turns spent on bookkeeping")]
for k, (head, note) in enumerate(MISTAKES):
    x = 40 + k * 448
    fig.card(x, 368, 432, 72, color="error")
    fig.text(x + 16, 396, head, "label", bold=True)
    fig.text(x + 16, 420, note, "note")

fig.caption("Size is a proxy: a tiny rule needed every turn still belongs in the window.")
fig.write()
