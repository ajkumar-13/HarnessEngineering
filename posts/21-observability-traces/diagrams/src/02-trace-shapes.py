"""Post 21, section 4: four runs of trace_loop.py as span strips on one time axis, read by their shape.

Run from the series root:  uv run python posts/21-observability-traces/diagrams/src/02-trace-shapes.py
Writes posts/21-observability-traces/diagrams/02-trace-shapes.svg.
A section 4 trace form of hrn_fig_design.md, computed: the script imports the post's snippets/trace_loop.py,
runs its six scripted runs into a temporary file, reads runs 1, 3, 6 and 4 back and draws each model, tool and
gate span at its simulated start and end, one strip per run. Every value drawn (the spans, the stop reasons, the
input tokens of run 4) comes from that file and is asserted against the body. Durations are simulated and the
tokens the series' illustrative run, so the figure is computed and illustrative. Roles: model calls blue, tool
calls orange, the gate purple, the repeated calls of the doom loop and the call that crossed the budget red.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("trace_loop", POST / "snippets" / "trace_loop.py")
snip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snip)
BODY = (POST / "index.md").read_text(encoding="utf-8")

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "spans.jsonl"
    snip.demo(path)
    _, rows = snip.summarise(path)
by_task = {r["task"].split()[0]: r for r in rows}
SHOWN = [("1", "healthy", "run 1, gated"), ("3", "doom loop", "run 3, exit (4) off"),
         ("6", "victory declaration", "run 6, no gate"), ("4", "growing context", "run 4, ceiling 100,000")]
assert [by_task[k]["stop"] for k, _, _ in SHOWN] == ["completed", "max_iters", "completed", "budget"]
assert [by_task[k]["iters"] for k, _, _ in SHOWN] == [6, 12, 2, 7]
assert by_task["4"]["tokens"] == 107_100 and by_task["6"]["gate"] == "none" and by_task["1"]["gate"] == "pass"
for phrase in ["repeats one read_file call twelve times", "stops after two iterations",
               "until exit (3), budget, at 107,100 tokens"]:
    assert phrase in BODY, phrase
LONGEST = max(max(s["end"] for s in by_task[k]["all"]) for k, _, _ in SHOWN)
assert LONGEST < 21

fig = Figure(
    "02-trace-shapes", "Four runs, four shapes, read before any label",
    "Four runs of trace_loop.py drawn as strips of spans on one axis from 0 to 21 simulated seconds: blue model "
    "calls, orange tool calls, a purple gate. Run 1, healthy, alternates model and tool spans over six iterations "
    "and ends with a gate that passes, completed. Run 3, a doom loop with exit (4) off, repeats one read_file call "
    "twelve times, the repeats edged in red, with no gate, and stops at the cap, max_iters. Run 6, an ungated "
    "answer, stops after two iterations, completed, with a dashed empty slot where a gate would be. Run 4, a "
    "growing context, makes seven model calls that widen as the history grows and stops on exit (3), budget, at "
    "107,100 input tokens against a ceiling of 100,000, the last call edged in red.",
    subtitle="Computed by trace_loop.py: simulated seconds on one axis; tokens are the series' illustrative run.",
    data_w=True)

X0, PX, BAR = 272, 24, 24
RX = 792
ROWS = [148, 228, 308, 388]
AXIS = 428

for t in range(0, 22, 3):
    fig.edge((X0 + PX * t, 112), (X0 + PX * t, AXIS), color="grid", width=0.75)
    fig.text(X0 + PX * t, AXIS + 20, f"{t} s", "tick", anchor="middle")
fig.edge((X0, AXIS), (X0 + PX * 21, AXIS), color="ink-muted", width=1)
fig.text(RX, AXIS + 5, "simulated seconds", "note")

for (key, head, note), y in zip(SHOWN, ROWS):
    r = by_task[key]
    spans = sorted((s for s in r["all"] if s["name"] in ("model.call", "verify.gate") or s["name"].startswith("tool.")),
                   key=lambda s: s["start"])
    models = [s for s in spans if s["name"] == "model.call"]
    seen = set()
    fig.text(40, y - 4, head, "head")
    fig.text(40, y + 16, note, "note")
    for s in spans:
        box = Box(X0 + PX * s["start"], y - BAR // 2, PX * (s["end"] - s["start"]), BAR)
        if s["name"] == "model.call":
            role = "model"
            red = key == "4" and s is models[-1]
        elif s["name"] == "verify.gate":
            role, red = "gate", False
        else:
            role = "act"
            sig = s["attributes"]["tool.args"]
            red = key == "3" and sig in seen
            seen.add(sig)
        with fig.data():
            fig.fill(box, f"{role}-soft", fit=False)
            fig.outline(box, "error" if red else role, width=1.5 if red else 1)
    end = max(s["end"] for s in r["all"])
    if key == "6":
        slot = Box(X0 + PX * end + 4, y - BAR // 2, PX * 1.2, BAR)
        with fig.data():
            fig.outline(slot, "gate", width=1, dash="proj")
        fig.text(int(X0 + PX * end + PX * 1.2 + 16) // 4 * 4, y + 5, "no gate", "note")
    if key == "4":
        fig.text(int(X0 + PX * end + 12) // 4 * 4, y + 5, f"{r['tokens']:,} tokens", "label", color="error-ink")
    fig.text(RX, y + 5, r["stop"], "code")

fig.legend(40, 476, [dict(color="model", label="model call"), dict(color="act", label="tool call"),
                     dict(color="gate", label="gate"), dict(color="error", label="repeated call or overrun",
                                                            mark="outline")], direction="row")
fig.caption("The doom loop never converges; the victory declaration is read from what is missing.")
fig.write()
