"""Post 09, section 9: the ladder of four moves, with what each loses and what it does to the cache.

Run from the series root:  uv run python posts/09-context-management-loop/diagrams/src/04-ladder.py
Writes posts/09-context-management-loop/diagrams/04-ladder.svg.
The rungs, their losses and their cache effects are the post's (sections 3 to 7), asserted against the body; the
cache effects are the ones the snippets print (offload.py: the call after a boundary offload reads 95% of itself
from cache; offload.py and ladder.py: a clear rewrites from the first cleared result; compact.py: the call after a
compaction keeps only the tools and the system prompt). A ladder is a boundary form (hrn_fig_design.md section 3):
neutral cards, one per rung, stepping up as the loss grows; colour carries no rung, the words do.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
RUNGS = [
    ("offload", "lossless", "nothing", ("untouched at the", "tool boundary")),
    ("clear", "nearly lossless", "the raw bytes", ("broken from the first", "cleared result")),
    ("compact", "lossy", "what the brief drops", ("rewritten after the", "system prompt")),
    ("reset", "total", "all the handoff lacks", ("starts over from", "the handoff")),
]
for phrase in ("**offload** a big output to disk (lossless)", "**clear** tool results already acted on (nearly lossless)",
               "**compact** older turns into a summary (lossy)", "**reset** the window behind a handoff file (total)",
               "at the tool boundary the log never enters the prefix",
               "the compaction in section 5 kept 773 tokens, the tools and the system prompt"):
    assert phrase in BODY, phrase

fig = Figure(
    "04-ladder", "Each rung up loses more and rewrites more of the cache",
    "Four cards stepping up from left to right, one per rung of the ladder, cheapest first. 1 offload, lossless: "
    "loses nothing; the cached message history is untouched at the tool boundary. 2 clear, nearly lossless: loses "
    "the raw bytes; the cache is broken from the first cleared result. 3 compact, lossy: loses what the brief drops; "
    "the cache is rewritten after the system prompt. 4 reset, total: loses all the handoff lacks; the cache starts "
    "over from the handoff.",
    subtitle="The four moves, cheapest first, and what each does to the cached message history.",
    data_w=True)

W, GAP, H, STEP, X0, BOTTOM = 208, 16, 136, 72, 40, 456
for k, (name, kind, loses, cache) in enumerate(RUNGS):
    x, y = X0 + k * (W + GAP), BOTTOM - H - k * STEP
    fig.card(x, y, W, H)
    fig.text(x + 16, y + 32, f"{k + 1}  {name}", "head")
    fig.text(x + W - 16, y + 32, kind, "note", anchor="end")
    fig.edge((x + 16, y + 48), (x + W - 16, y + 48), color="border", width=1)
    fig.text(x + 16, y + 72, f"loses: {loses}", "label")
    fig.text(x + 16, y + 100, f"cache: {cache[0]}", "label")
    fig.text(x + 16, y + 120, cache[1], "label")
fig.arrow((X0 + 16, 296), (X0 + 2 * (W + GAP) - 24, 188))
fig.text(X0, 192, "each rung up: dearer, and more is lost", "note")
fig.caption("Only offloading at the tool boundary leaves the prefix whole; make every other rewrite count.")
fig.write()
