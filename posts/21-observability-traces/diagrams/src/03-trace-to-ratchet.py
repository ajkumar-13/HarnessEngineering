"""Post 21, section 5: a trace localises a failure to one component, and the ratchet's three teeth receive it.

Run from the series root:  uv run python posts/21-observability-traces/diagrams/src/03-trace-to-ratchet.py
Writes posts/21-observability-traces/diagrams/03-trace-to-ratchet.svg.
A section 3 form of hrn_fig_design.md, its trace panel computed: the script imports the post's
snippets/trace_loop.py, runs its six scripted runs into a temporary file and reads runs 3 and 2 back. Run 3 is the
doom loop with exit (4) off; run 2 is the same script with exit (4) on. The iteration counts, the stop reasons,
the input-token totals and the repeated signature are read from the file and asserted against the body. The three
teeth are post 10's (memory line, hook, reviewer check), written for this failure. Roles: tool calls orange, the
repeats red, the loop's exit, the hook and the reviewer check purple, the memory line green (a rule
on disk, as in post 10's hero).
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("trace_loop", POST / "snippets" / "trace_loop.py")
snip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snip)
BODY = (POST / "index.md").read_text(encoding="utf-8")

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "spans.jsonl"
    snip.demo(path)
    _, rows = snip.summarise(path)
doom, fixed = rows[2], rows[1]
calls = sorted((s for s in doom["all"] if s["name"].startswith("tool.")), key=lambda s: s["start"])
sigs = [(s["name"], s["attributes"]["tool.args"]) for s in calls]
first_repeat = next(k for k in range(1, len(sigs)) if sigs[k] == sigs[k - 1]) + 1
assert (doom["stop"], doom["iters"], doom["tokens"], len(calls)) == ("max_iters", 12, 276_600, 12)
assert len(set(sigs)) == 1 and first_repeat == 2 and json.loads(sigs[0][1]) == {"path": "src/parser.py"}
assert (fixed["stop"], fixed["iters"], fixed["tokens"]) == ("no_progress", 3, 27_300)
for phrase in ["run 3's twelve identical read_file spans", "ending max_iters at 276,600 tokens",
               "identical signatures from iteration 2", "stops at iteration 3 on no_progress at 27,300 tokens",
               "a memory line, a pre-tool hook refusing a third identical call, and a reviewer check"]:
    assert phrase in BODY, phrase

fig = Figure(
    "03-trace-to-ratchet", "The trace names the component; the ratchet keeps the fix",
    "Three panels joined by arrows. Trace: run 3 of trace_loop.py, a root ending max_iters after 12 iterations and "
    "276,600 input tokens, its twelve read_file calls on src/parser.py identical, the repeats from iteration 2 "
    "edged in red. Localise: the repeated signature is owned by component 01, the loop, whose exit (4) was off; "
    "with it on, the same script stops at iteration 3 on no_progress at 27,300 tokens. Ratchet: three teeth, "
    "a green memory line to change approach when a call repeats, a purple pre-tool hook that refuses a third "
    "identical call, and a purple reviewer check that replays run 3 and requires it to stop by iteration 3.",
    subtitle="Runs 2 and 3 of trace_loop.py: one script, exit (4) on and off; tokens are the series' illustrative run.",
    data_w=True)

left, mid, right = fig.row(3, gutter=64)

# Trace: the root, then the twelve calls as a strip, repeats in red
body = fig.panel(left, "Trace")
fig.text(body.x, body.y + 20, f"stop.reason = {doom['stop']}", "code")
fig.text(body.x, body.y + 44, f"{doom['iters']} iterations, {doom['tokens']:,} tokens", "note")
strip = fig.strip(body.x, body.y + 72, 12, cell=20)
for k in range(12):
    fig.fill(strip.cell(k).inset(2), "act-soft")
    fig.outline(strip.cell(k).inset(2), "error" if k + 1 >= first_repeat else "act", width=1.5 if k else 1)
for k in (0, 1, 11):
    cell = strip.cell(k)
    fig.text(cell.x + cell.w // 2, cell.y + cell.h + 20, str(k + 1), "tick", anchor="middle")
fig.text(body.x, body.y + 148, "12 calls, each ok:", "label")
fig.text(body.x, body.y + 172, "read_file src/parser.py", "code")
fig.text(body.x, body.y + 204, f"identical from iteration {first_repeat}", "label", color="error-ink")

# Localise: the owning component and the counterfactual run
body2 = fig.panel(mid, "Localise")
c = fig.card(body2.x, body2.y + 4, body2.w, None, heading="component 01, the loop",
             lines=["exit (4), no progress, was off"], color="gate", fit=True)
fig.text(body2.x, c.y + c.h + 44, "with exit (4) on, the same script:", "note")
short = fig.strip(body2.x, c.y + c.h + 64, 2, cell=20)
for k in range(2):
    fig.fill(short.cell(k).inset(2), "act-soft")
    fig.outline(short.cell(k).inset(2), "error" if k else "act", width=1.5 if k else 1)
fig.marker(body2.x + 56, c.y + c.h + 74, "diamond", "gate", size=16)
fig.text(body2.x + 76, c.y + c.h + 79, "exit (4) at iteration 3", "label", color="gate-ink")
fig.text(body2.x, c.y + c.h + 124, f"stop.reason = {fixed['stop']}", "code")
fig.text(body2.x, c.y + c.h + 148, f"{fixed['tokens']:,} tokens, not {doom['tokens']:,}", "label")

# Ratchet: the three teeth of post 10
body3 = fig.panel(right, "Ratchet: three teeth")
y = body3.y + 4
for head, line, role in [("memory line", "change approach on a repeat", "state"),
                         ("hook, pre-tool", "refuse a third identical call", "gate"),
                         ("reviewer check", "replay run 3: stop by iteration 3", "gate")]:
    card = fig.card(body3.x, y, body3.w, None, heading=head, lines=[line], color=role, fit=True)
    y = card.y + card.h + 32

fig.arrow((left.x + left.w + 4, 200), (mid.x - 4, 200))
fig.arrow((mid.x + mid.w + 4, 200), (right.x - 4, 200))
fig.caption("Without the trace the run is \"flaky\"; with it, the fix has an owner and a test.")
fig.write()
