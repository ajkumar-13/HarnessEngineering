"""Post 18, section 3: one iteration's context, stable first, and who may write each file it is built from.

Run from the series root:  uv run python posts/18-long-horizon-ralph/diagrams/src/02-inside-one-iteration.py
Writes posts/18-long-horizon-ralph/diagrams/02-inside-one-iteration.svg.
The stack is the order in which snippets/ralph_driver.py's stand-in agent reads its files (agent(): PROMPT.md and
the spec first, then the status file, the handoff, the git log and the source). The two token counts are computed
here by running the snippet's honest scenario: the frozen prefix's size, asserted byte-identical in every
iteration, and the smallest and largest volatile re-entry part. Files are state (green); the iteration's own
output is the model's (blue); the write rules are the permissions table of the post's sixth section.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import ralph_driver as rd  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
SRC = (POST / "snippets" / "ralph_driver.py").read_text(encoding="utf-8")
rows, it, reason = rd.scenario("honest", quiet=True)
assert (it, reason) == (4, "completed") and len({r["prefix_sha"] for r in rows}) == 1
FROZEN = rows[0]["frozen"]
LO, HI = min(r["volatile"] for r in rows), max(r["volatile"] for r in rows)
assert (FROZEN, LO, HI) == (208, 28, 137)
assert f"frozen prefix is {FROZEN} tokens" in BODY and f"from {LO} to {HI} tokens at re-entry" in BODY
# the reading order in the agent: frozen = PROMPT.md + spec; volatile = status + handoff + git log + source
assert 'frozen = (repo / "PROMPT.md")' in SRC and "volatile = (repo / STATUS)" in SRC

fig = Figure(
    "02-inside-one-iteration", "Stable first: the frozen prefix, then what moved",
    f"Left, one iteration's context as a stack read top to bottom. PROMPT.md, the system prompt, and the spec are "
    f"bracketed as the frozen prefix, {FROZEN} tokens in the snippet's toy build and byte-identical in every "
    f"iteration, so a prompt cache can serve them. Below them status.json, handoff.md, the git log and the source "
    f"file are bracketed as volatile, {LO} to {HI} tokens at re-entry, rebuilt every time; last comes the "
    f"iteration's own work. Right, a table of who may write each file: the spec, a human between runs; "
    f"status.json, only the gate; handoff.md, the loop, rewritten whole; the source, the loop, one commit per "
    f"iteration.",
    subtitle="Computed from snippets/ralph_driver.py's toy build; its token counts are illustrative.",
    data_w=True)

left, right = fig.row([5, 4])
stack = fig.panel(left, "What one fresh context reads, in order")
BLOCKS = [("PROMPT.md", "system prompt", "state"), ("spec/feature_list.json", "the spec", "state"),
          ("spec/status.json", "pass bits", "state"), ("handoff.md", "where it stands", "state"),
          ("git log --oneline", "history", "state"), ("calc.py", "the source", "state"),
          ("this iteration's work", "", "model")]
X, W, RH, GAP = stack.x, 304, 40, 8
ys = []
for k, (name, what, role) in enumerate(BLOCKS):
    y = stack.y + k * (RH + GAP)
    ys.append(y)
    box = Box(X, y, W, RH)
    fig.fill(box, f"{role}-soft", radius=4)
    fig.outline(box, f"{role}-line", radius=4)
    fig.text(X + 12, y + 25, name, "label" if not what else "code")
    if what:
        fig.text(X + W - 12, y + 25, what, "note", anchor="end")

BRX = X + W + 8
fig.brace(ys[0], ys[1] + RH, BRX, vertical=True, side="right", color="state")
fig.brace(ys[2], ys[5] + RH, BRX, vertical=True, side="right", color="state")
TX = BRX + 24
fig.text(TX, ys[0] + 25, "frozen prefix", "value", color="state")
fig.text(TX, ys[1] + 25, f"{FROZEN} tokens, identical", "note")
fig.text(TX, ys[3] + 25, "volatile", "value", color="state")
fig.text(TX, ys[4] + 25, f"{LO} to {HI} tokens", "note")

table = fig.panel(right, "Who may write it")
fig.table(table.x, table.y, [["File", "Writer"], ["the spec", "a human, between runs"],
                             ["status.json", "the gate, only"], ["handoff.md", "the loop, rewritten"],
                             ["the source", "the loop, one commit"]], [120, 232], row_h=40)
fig.note(Box(table.x, table.y, 352, 200), ["The agent may write neither", "file under spec/."])

fig.caption("What never changes sits first, where a cache can find it.")
fig.write()
