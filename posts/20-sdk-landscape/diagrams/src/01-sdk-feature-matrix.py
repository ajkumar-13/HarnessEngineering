"""Post 20, hero: six harness components against four shapes, as the vendors documented them in October 2026.

Run from the series root:  uv run python posts/20-sdk-landscape/diagrams/src/01-sdk-feature-matrix.py
Writes posts/20-sdk-landscape/diagrams/01-sdk-feature-matrix.svg.
Every mark is a reading of a named vendor page, consulted 16 October 2026 (the SOURCES table below), and the body's
third section states the qualifications of the partial cells; the phrases the marks rest on are asserted against the
body. The matrix is illustrative and dated, and says so on the figure. Roles (hrn_fig_design.md section 0): the
products are neutral cards and the marks are ink, because a product is a neutral thing; the mark's shape and its
words carry the meaning, never a colour. No numbers.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")

SHAPES = [("Claude Agent SDK", "batteries-included"), ("OpenAI Agents SDK", "code-first"),
          ("LangGraph", "graph framework"), ("Codex harness", "open engine")]
# component -> one (mark, words) per shape; mark is built, partial or team
CELLS = [
    ("01", "loop", [("built", "agent loop"), ("built", "built-in loop"), ("team", "the team draws it"),
                    ("built", "agent loop")]),
    ("03", "state", [("built", "sessions, forks"), ("built", "sessions"), ("built", "checkpointers"),
                     ("built", "threads, forks")]),
    ("04", "context management", [("built", "auto compaction"), ("partial", "opt-in compaction"),
                                  ("team", "the team builds it"), ("built", "thread compaction")]),
    ("07", "hooks", [("built", "lifecycle hooks"), ("built", "tool guardrails"), ("team", "a node of its own"),
                     ("built", "lifecycle hooks")]),
    ("08", "permissions", [("built", "rules and modes"), ("partial", "approval per tool"),
                           ("partial", "interrupt()"), ("built", "sandbox, approvals")]),
    ("09", "orchestration", [("built", "subagents"), ("built", "handoffs"), ("partial", "topology by hand"),
                             ("built", "subagents")]),
]
SOURCES = {  # the page behind each column, and the body phrase that carries it
    "Claude Agent SDK": ('"Agent SDK overview", "How the agent loop works", hooks, "Configure permissions"',
                         "its capabilities table lists built-in tools, hooks, subagents"),
    "OpenAI Agents SDK": ('Agents SDK documentation: index, "Sessions", guardrails, "Human-in-the-loop"',
                          "compaction is an opt-in session wrapper"),
    "LangGraph": ('overview, "Persistence", "Interrupts"', "the team draws any multi-agent topology itself"),
    "Codex harness": ('"Codex as a platform", app-server, hooks and subagents pages',
                      "app-server threads that start, resume and fork, with compaction and approval requests"),
}
for page, phrase in SOURCES.values():
    assert phrase in BODY, phrase
for phrase in ('"partial" means this section qualifies it', "`interrupt()` pauses the graph for a human",
               "approval is set per tool", "automatic compaction", "subagents"):
    assert phrase in BODY, phrase
assert len(CELLS) == 6 and all(len(c[2]) == 4 for c in CELLS)

WORDS = {"built": "built in", "partial": "partial", "team": "the team builds it"}
desc_rows = "; ".join(
    f"{name}: " + ", ".join(f"{s[0]} {WORDS[m]} ({w})" for s, (m, w) in zip(SHAPES, cells))
    for _, name, cells in CELLS)
fig = Figure(
    "01-sdk-feature-matrix", "What each shape ships, as documented",
    "A matrix, illustrative and dated October 2026. Columns: the Claude Agent SDK, batteries-included; the OpenAI "
    "Agents SDK, code-first; LangGraph, a graph framework; the Codex harness, an open engine. Rows, with each cell "
    "marked built in (a solid dot), partial (a hollow dot) or the team builds it (a dash): " + desc_rows + ".",
    subtitle="Six components against four shapes, read from vendor documentation in October 2026; illustrative.",
    data_w=True)

X0, COMP_W, COL_W = 40, 176, 176
HEAD_Y, TOP, ROW_H = 104, 156, 48
for k, (name, shape) in enumerate(SHAPES):
    x = X0 + COMP_W + k * COL_W
    fig.text(x + 12, HEAD_Y + 20, name, "head")
    fig.text(x + 12, HEAD_Y + 40, shape, "note")
fig.text(X0, HEAD_Y + 20, "component", "head")
fig.edge((X0, TOP), (920, TOP), color="ink-muted", width=1)
for i, (number, name, cells) in enumerate(CELLS):
    top = TOP + i * ROW_H
    if i:
        fig.edge((X0, top), (920, top), color="border", width=0.75)
    fig.text(X0, top + 28, number, "note")
    fig.text(X0 + 28, top + 28, name, "label")
    for k, (mark, words) in enumerate(cells):
        x = X0 + COMP_W + k * COL_W
        cy = top + 24
        if mark == "team":
            fig.edge((x + 12, cy), (x + 24, cy), color="ink-muted", width=1.5)
        else:
            fig.marker(x + 18, cy, "circle", "ink", size=10, hollow=(mark == "partial"))
        style = "code" if words.endswith("()") else ("note" if mark == "team" else "label")
        fig.text(x + 32, top + 28, words, style)
fig.edge((X0, TOP + 6 * ROW_H), (920, TOP + 6 * ROW_H), color="ink-muted", width=1)

fig.legend(X0, 468, [dict(color="ink", label="built in", mark="circle"),
                     dict(color="ink", label="partial, qualified in the text", mark="circle", hollow=True),
                     dict(color="ink-muted", label="the team builds it", mark="line")],
           direction="row", gap=40)
fig.caption("The marks record documentation on one date; the defaults behind them still have to be read.")
fig.write()
