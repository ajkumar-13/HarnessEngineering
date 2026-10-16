"""Post 25, section 8: fourteen adversarial calls through each build's gates (hrn_fig_design.md section 3, computed).

Run from the series root:  uv run python posts/25-build-harness-plus/diagrams/src/02-blast-radius.py
Writes posts/25-build-harness-plus/diagrams/02-blast-radius.svg.

Every count is computed by importing snippets/adversarial_table.py, which sends the fourteen calls through
code/24-minimal-harness and code/25-harness-plus with a recording runner. Build #1's only gate is the deny-list
inside its bash tool; Build #2's are the pre-tool hook and then the sandbox, in that order. The counts and the
one reaching call are asserted against the totals line the post quotes.
"""
import contextlib
import io
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure, Box  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()) as out:
    import adversarial_table as at  # noqa: E402
BODY = (POST / "index.md").read_text(encoding="utf-8")
totals = [l for l in out.getvalue().splitlines() if l.startswith("totals:")][0]
assert totals in BODY, totals

n = len(at.rows)
b1 = Counter(r[1] for r in at.rows)
b2 = Counter(r[2] for r in at.rows)
by = Counter(r[4] for r in at.rows if r[2] == "refused")
reach2 = [r[0] for r in at.rows if r[2] == "reached"]
assert (n, b1["blocked"], b1["reached"]) == (14, 5, 9)
assert (b2["blocked"], b2["refused"], b2["reached"]) == (3, 10, 1)
assert dict(by) == {"metacharacter": 5, "allow-list": 3, "traversal": 1, "jail": 1}, by
assert reach2 == ["git push -f origin main"]
reach1 = Counter(r[4] for r in at.rows if r[1] == "reached")
assert dict(reach1) == {"nothing": 1, "metacharacter": 5, "traversal": 1, "jail": 1, "allow-list": 1}, reach1
REACH1 = (f"git push -f, {reach1['metacharacter']} chains, "
          f"{reach1['traversal'] + reach1['jail']} paths, python -c")

fig = Figure(
    "02-blast-radius", "Nine calls reach execution in Build #1, one in Build #2",
    f"Fourteen adversarial calls sent through each build, computed by adversarial_table.py. Build #1: its one gate, "
    f"the deny-list inside the bash tool, stops {b1['blocked']}, and {b1['reached']} reach execution. Build #2: the "
    f"pre-tool hook stops {b2['blocked']}, leaving {n - b2['blocked']}; the sandbox refuses {b2['refused']}, "
    f"{by['metacharacter']} on a shell metacharacter, {by['allow-list']} on the allow-list, {by['traversal']} on "
    f"traversal and {by['jail']} on the jail; {b2['reached']} call, {reach2[0]}, reaches execution.",
    subtitle="Fourteen calls drawn from the companions, sent through each build by adversarial_table.py.",
    data_w=True)

left, right = fig.row(2)
fig.text(left.x, 128, "Build #1", "head")
fig.text(right.x, 128, "Build #2, default allow-list", "head")


def calls(x):
    fig.card(x, 144, 240, 40)
    fig.text(x + 16, 170, f"{n} adversarial calls", "label")
    return x + 120


def gate(x, y, head, line, w=424):
    b = Box(x, y, w, 56)
    fig.fill(b, "gate-soft", radius=8)
    fig.outline(b, "gate", radius=8)
    fig.text(x + 16, y + 24, head, "label", bold=True)
    fig.text(x + 16, y + 46, line, "note")


def reached(x, count, line, style="code"):
    b = Box(x, 392, 424, 64)
    fig.fill(b, "error-soft", radius=8)
    fig.outline(b, "error", width=1.5, radius=8)
    fig.text(x + 16, 418, f"{count} reach{'es' if count == 1 else ''} execution", "label", bold=True, color="error")
    fig.text(x + 16, 442, line, style)


# Build #1: one gate
cx = calls(left.x)
fig.arrow((cx, 184), (cx, 216), label=str(n), side="right")
gate(left.x, 216, "deny-list in the bash tool", f"stops {b1['blocked']}")
fig.arrow((cx, 272), (cx, 392), label=str(b1["reached"]), side="right")
reached(left.x, b1["reached"], REACH1, "label")
fig.text(cx + 32, 324, "no allow-list, no metacharacter check,", "note")
fig.text(cx + 32, 344, "and a shell runs the string", "note")

# Build #2: hook, then sandbox
cx = calls(right.x)
fig.arrow((cx, 184), (cx, 216), label=str(n), side="right")
gate(right.x, 216, "pre-tool hook", f"blocks {b2['blocked']}", w=424)
fig.arrow((cx, 272), (cx, 304), label=str(n - b2["blocked"]), side="right")
gate(right.x, 304, f"sandbox: refuses {b2['refused']}",
     f"{by['metacharacter']} metacharacter, {by['allow-list']} allow-list, {by['traversal']} traversal, "
     f"{by['jail']} jail", w=424)
fig.arrow((cx, 360), (cx, 392), label=str(b2["reached"]), side="right")
reached(right.x, b2["reached"], reach2[0])
fig.caption("Computed: the same calls, the same injected runner; only the gates differ.")
fig.write()
