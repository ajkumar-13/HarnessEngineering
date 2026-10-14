"""Post 03, section 5: what the loop sends the model on each call of one run.

Run from the series root:  uv run python posts/03-the-agent-loop/diagrams/src/02-history-resent.py
Writes posts/03-the-agent-loop/diagrams/02-history-resent.svg.
Nothing here is typed in: the companion's run() (code/03-agent-loop) drives a ScriptedModel wrapped in a recorder
that copies the messages it is sent on every call, and each column is one recorded request. Every request also
carries the tools and the system prompt ahead of the messages, in the render order section 5 cites. Colours by role
(hrn_fig_design.md section 0): the model's messages blue, tool results (the outcome of an action) orange, the head
and the user's task neutral.
"""
import copy
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "03-agent-loop" / "src"))
from figkit import Figure  # noqa: E402
from agent_loop import DEFAULT_TOOLS, ScriptedModel, run, text_response, tool_response  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")


class Recorder:
    """Passes every call to the scripted model and keeps a copy of the messages it was sent."""

    def __init__(self, inner):
        self.inner, self.sent, self.returned = inner, [], []

    def respond(self, system, messages, tools):
        self.sent.append(copy.deepcopy(messages))
        resp = self.inner.respond(system, messages, tools)
        self.returned.append(resp)
        return resp


model = Recorder(ScriptedModel([
    tool_response("calculator", {"expression": "2 + 3"}, id="tu_1"),
    tool_response("echo", {"text": "5"}, id="tu_2"),
    text_response("The answer is 5."),
]))
result = run(model, DEFAULT_TOOLS, "Add 2 and 3, then echo it.", system="You are a careful assistant.")
assert result.stop_reason.value == "completed" and result.iterations == 3
assert [len(m) for m in model.sent] == [1, 3, 5]
for k in range(1, 3):                                   # each request is the previous one plus one pair
    assert model.sent[k][:-2] == model.sent[k - 1]


def chip(msg):
    """(text, colour) for one message as the request carries it."""
    if isinstance(msg["content"], str):
        return "user: the task", None
    kinds = [b["type"] for b in msg["content"]]
    if "tool_use" in kinds:
        name = next(b["name"] for b in msg["content"] if b["type"] == "tool_use")
        return f"assistant: tool_use, {name}", "model"
    if kinds == ["tool_result"]:
        return "user: tool_result", "act"
    return "assistant: answer", "model"


def reply(resp):
    return (f"tool_use, {resp.tool_uses[0].name}", "model") if resp.tool_uses else ("final answer", "model")


for phrase in ("one on call 1, three on call 2, five on call 3", "rendered in the order tools, then system prompt, "
               "then messages", "**re-sends all of it on every turn**"):
    assert phrase in BODY, phrase

fig = Figure(
    "02-history-resent", "Every call re-sends the whole history",
    "Three columns, one per model call of a scripted run of the companion's loop: two tool calls, then an answer. "
    "Each column lists the request in the order sent: tools and system prompt, the same head every time, then the "
    "messages so far. Call 1 carries 1 message, the user's task; call 2 carries 3, adding the assistant's "
    "calculator tool_use and its tool_result; call 3 carries 5, adding the echo tool_use and its result. Under each "
    "column, the response the model returned: tool_use calculator, tool_use echo, the final answer. Arrows show each "
    "response appended to the next call's request. The model keeps nothing between calls.",
    subtitle="What the companion's loop sent the model on each call of one scripted run, recorded.",
    data_w=True)

X0, CW, GAP = 56, 256, 40
TOP, STEP, CH = 144, 36, 28
RESP_Y = 412
cols = [X0 + k * (CW + GAP) for k in range(3)]
for k, (x, sent, resp) in enumerate(zip(cols, model.sent, model.returned)):
    fig.text(x, TOP - 16, f"call {k + 1}", "head")
    fig.text(x + CW, TOP - 16, f"{len(sent)} message{'s' if len(sent) > 1 else ''}", "note", anchor="end")
    rows = [("tools", None), ("system prompt", None)] + [chip(m) for m in sent]
    for i, (text, colour) in enumerate(rows):
        y = TOP + i * STEP
        fig.card(x, y, CW, CH, radius=4, color=colour)
        fig.text(x + 12, y + 19, text, "label")
    bottom = TOP + len(rows) * STEP - 8
    fig.arrow((x + CW // 2, bottom), (x + CW // 2, RESP_Y), label="model call")
    text, colour = reply(resp)
    fig.card(x, RESP_Y, CW, 32, radius=4, color=colour)
    fig.text(x + 12, RESP_Y + 21, f"returns: {text}", "label")
    if k < 2:                                            # the reply joins the next request
        new_y = TOP + (2 + len(sent)) * STEP + CH // 2
        gx = x + CW + GAP // 2
        fig.arrow((x + CW, RESP_Y + 16), (cols[k + 1], new_y), via=[(gx, RESP_Y + 16), (gx, new_y)])

fig.caption("The model keeps nothing between calls; each reply is appended and sent again with everything before it.")
fig.write()
