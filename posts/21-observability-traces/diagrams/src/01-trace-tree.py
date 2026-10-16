"""Post 21, hero: one run of trace_loop.py drawn as a waterfall of nested spans.

Run from the series root:  uv run python posts/21-observability-traces/diagrams/src/01-trace-tree.py
Writes posts/21-observability-traces/diagrams/01-trace-tree.svg.
A section 4 trace of hrn_fig_design.md, computed: the script imports posts/21-observability-traces/snippets/
trace_loop.py, runs its six scripted runs into a temporary file, reads run 1 back from that file and draws every
span at its simulated start and end. Every value drawn (the span names, the durations, the input tokens, the
outcomes, the stop reason) comes from that file and is asserted against the body. Durations are the snippet's
simulated clock and the token counts the series' illustrative run, so the figure is computed and illustrative.
Roles: model calls blue, tool calls orange, the verification gate purple, the latency outlier red-edged, the
outcomes a gate decided against in red; the run and its iterations neutral.
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
run1 = rows[0]
TREE = snip.tree(run1["all"])
root = TREE[0][1]
END = root["end"]
tools = [s for _, s in TREE if s["name"].startswith("tool.")]
models = [s for _, s in TREE if s["name"] == "model.call"]
gate = next(s for _, s in TREE if s["name"] == "verify.gate")
slow = max(tools, key=lambda s: s["end"] - s["start"])
assert root["attributes"]["stop.reason"] == "completed" and len(TREE) == 19 and abs(END - 17.92) < 1e-9
assert [s["attributes"]["outcome"] for s in tools] == ["ok", "blocked", "refused", "ok", "denied"]
assert [s["attributes"]["gen_ai.usage.input_tokens"] for s in models] == [6_000 + 3_100 * k for k in range(6)]
assert slow["name"] == "tool.run_tests" and abs(slow["end"] - slow["start"] - 7.8) < 1e-9
assert gate["attributes"]["outcome"] == "pass"
for phrase in ["A waterfall of nineteen spans", "about 18 simulated seconds", "climb from 6,000 to 21,500",
               "tagged ok, blocked, refused, ok and denied", "7.8-second run_tests span", "verify.gate that passes"]:
    assert phrase in BODY, phrase

DECIDER = {"blocked": "blocked by hook", "refused": "refused by sandbox", "denied": "denied by approver"}

fig = Figure(
    "01-trace-tree", "The root says why it ended; each tool span, who decided",
    "A waterfall of the 19 spans of run 1 of trace_loop.py on a time axis from 0 to 18 simulated seconds. The "
    "root agent.run lasts 17.92 seconds and carries stop.reason completed. Six iterations follow, each opening "
    "with a model call whose input tokens are 6,000, 9,100, 12,200, 15,300, 18,400 and 21,500. The first five "
    "each have a tool span: read_file ok, bash blocked by the hook, bash refused by the sandbox, run_tests ok, "
    "which takes 7.80 seconds and is edged in red as the latency outlier, and deploy denied by the approver. A "
    "purple verify.gate span of 1.20 seconds passes after the final answer.",
    subtitle="Computed by trace_loop.py, run 1: simulated seconds; tokens are the series' illustrative run.",
    height=720, data_w=True)

X0, PX = 272, 24                      # the time axis: x of 0 s, pixels per simulated second
RX = 720                              # the right column: duration and the attribute that matters
PITCH, BAR = 36, 20


def tx(t):
    return X0 + PX * t


def fmt_s(s):
    return f"{s['end'] - s['start']:.2f} s"


# rows: the root, then one or two per iteration, then the gate
layout, y = [], 140
for depth, s in TREE:
    if s["name"] == "iteration":
        continue
    layout.append((s, y))
    y += PITCH
AXIS = y - PITCH + 28

# iteration bands: each a soft neutral span across its children's rows
iters = [s for _, s in TREE if s["name"] == "iteration"]
for it in iters:
    kids = [ry for s, ry in layout if s["parent_id"] == it["span_id"]]
    top, bottom = min(kids) - 14, max(kids) + 14
    with fig.data():
        fig.fill(Box(tx(it["start"]), top, PX * (it["end"] - it["start"]), bottom - top), "neutral-soft", fit=False)
        fig.outline(Box(tx(it["start"]), top, PX * (it["end"] - it["start"]), bottom - top), "border", width=1)
    fig.text(40, (top + bottom) // 2 // 4 * 4 + 4, f"iteration {it['attributes']['iteration.index']}", "note")

# time grid and axis
for t in range(0, 19, 3):
    fig.edge((tx(t), 120), (tx(t), AXIS), color="grid", width=0.75)
    fig.text(tx(t), AXIS + 20, f"{t} s", "tick", anchor="middle")
fig.edge((X0, AXIS), (tx(18), AXIS), color="ink-muted", width=1)
fig.text(RX, AXIS + 5, "simulated seconds", "note")

for s, ry in layout:
    box = Box(tx(s["start"]), ry - BAR // 2, PX * (s["end"] - s["start"]), BAR)
    name, a = s["name"], s["attributes"]
    if name == "agent.run":
        role, label = "ink-muted", fmt_s(s)
        fig.text(40, ry + 5, "agent.run", "code")
    elif name == "model.call":
        role, label = "model", f"{fmt_s(s)}, {a['gen_ai.usage.input_tokens']:,} tokens"
        fig.text(136, ry + 5, "model.call", "code")
    elif name == "verify.gate":
        role, label = "gate", f"{fmt_s(s)}, {a['outcome']}"
        fig.text(40, ry + 5, "verify.gate", "code")
    else:
        role = "act"
        word = DECIDER.get(a["outcome"], a["outcome"])
        label = f"{fmt_s(s)}, {word}" + (", the outlier" if s is slow else "")
        fig.text(136, ry + 5, name, "code")
    with fig.data():
        fig.fill(box, "neutral-soft" if role == "ink-muted" else f"{role}-soft", fit=False)
        if s is slow:
            fig.outline(box, "error", width=2.5)
        else:
            fig.outline(box, role, width=1)
    colour = "error-ink" if a.get("outcome") in DECIDER else ("gate-ink" if role == "gate" else None)
    fig.text(RX, ry + 5, label, "label", color=colour)

ry0 = layout[0][1]
fig.text(tx((root["start"] + root["end"]) / 2) // 4 * 4, ry0 + 5, f"stop.reason = {root['attributes']['stop.reason']}",
         "code", anchor="middle")

fig.legend(40, 648, [dict(color="model", label="model call"), dict(color="act", label="tool call"),
                     dict(color="gate", label="verification gate"),
                     dict(color="error", label="latency outlier", mark="outline")], direction="row")
fig.caption("Read the root first, then the outcomes: three calls were stopped, each by a different layer.")
fig.write()
