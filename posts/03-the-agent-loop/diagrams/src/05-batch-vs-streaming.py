"""Post 03, section 10: one turn scheduled batch and streaming on one time axis.

Run from the series root:  uv run python posts/03-the-agent-loop/diagrams/src/05-batch-vs-streaming.py
Writes posts/03-the-agent-loop/diagrams/05-batch-vs-streaming.svg.
A schematic, not a measurement: no durations are shown and none is claimed, so the axis has no numbers and the
subtitle says "schematic". The response holds narration and two tool calls, A and B, and the harness runs a turn's
tools one after another, as the companion's run() does (a for loop over resp.tool_uses, asserted below). Batch
starts tool A after the last token; streaming starts it when call A's block is complete (its content_block_stop
event, section 10). Model output is blue, tool runs are orange (hrn_fig_design.md section 0).
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "03-agent-loop" / "src"))
from figkit import Figure  # noqa: E402
from agent_loop import run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
assert "for tu in resp.tool_uses:" in inspect.getsource(run)          # the companion runs tools in sequence
for phrase in ("parse them once the block's `content_block_stop` event arrives", "streaming saves nothing",
               "the companion is batch"):
    assert phrase in BODY, phrase

# schematic units: narration, call A, call B are generated in turn; each tool takes the same time
TEXT, CALL, TOOL = 120, 120, 100
A_DONE, END = TEXT + CALL, TEXT + 2 * CALL


def x(u):
    return 192 + u * 1.2


SCHEDULES = {   # lane: (tool A start, tool B start); the next call follows tool B
    "batch": (END, END + TOOL),
    "streaming": (A_DONE, max(A_DONE + TOOL, END)),
}

fig = Figure(
    "05-batch-vs-streaming", "Streaming starts a tool as soon as its call is complete",
    "A schematic of one turn on one time axis, without numbers. The response holds narration, then tool call A, then "
    "tool call B, generated in that order and equally long in both lanes. Batch: tool A starts only after the last "
    "token of the response, and tool B after tool A, then the next call. Streaming: tool A starts as soon as call A's "
    "block is complete, while call B is still being generated; tool B starts when its own block is complete. The "
    "streaming lane reaches the next call earlier, and a bracket marks the time saved, which comes from the part of "
    "the response generated after call A.",
    subtitle="Schematic, no measured durations: two tool calls in one response, run one after another as the companion does.",
    data_w=True)

LANES = {"batch": 136, "streaming": 288}
next_calls = {}
for lane, top in LANES.items():
    fig.text(40, top + 20, lane, "label", bold=True)
    fig.text(120, top + 20, "model", "note")
    fig.text(120, top + 68, "harness", "note")
    for u0, u1, name in [(0, TEXT, "narration"), (TEXT, A_DONE, "call A"), (A_DONE, END, "call B")]:
        fig.card(x(u0), top, x(u1) - x(u0) - 4, 32, radius=4, color="model")
        fig.text((x(u0) + x(u1) - 4) / 2, top + 21, name, "label", anchor="middle")
    a0, b0 = SCHEDULES[lane]
    for u0, name in [(a0, "tool A"), (b0, "tool B")]:
        fig.card(x(u0), top + 48, x(u0 + TOOL) - x(u0) - 4, 32, radius=4, color="act")
        fig.text((x(u0) + x(u0 + TOOL) - 4) / 2, top + 69, name, "label", anchor="middle")
    nxt = b0 + TOOL
    next_calls[lane] = nxt
    fig.edge((x(nxt), top - 8), (x(nxt), top + 88), color="ink", width=1.5)
    fig.text(x(nxt) - 8, top + 4, "next call", "note", anchor="end")
    if lane == "streaming":
        fig.edge((x(A_DONE) - 2, top - 16), (x(A_DONE) - 2, top + 88), color="model", width=1.5, dash="lead")
        fig.text(x(A_DONE) - 10, top - 4, "call A complete", "note", anchor="end", color="model")

saved_from, saved_to = next_calls["streaming"], next_calls["batch"]
assert saved_from < saved_to
fig.brace(x(saved_from), x(saved_to), 392, label="saved", side="below")
fig.arrow((192, 464), (x(END + 2 * TOOL) + 16, 464), label=None)
fig.text(x(END + 2 * TOOL) + 16, 456, "time", "note", anchor="end")
fig.caption("If the response ended with call A, both lanes would start it at the same moment.")
fig.write()
