"""Post 09, section 5: where a count-based cut lands in an agentic transcript, and where the safe cut moves it.

Run from the series root:  uv run python posts/09-context-management-loop/diagrams/src/02-safe-cut.py
Writes posts/09-context-management-loop/diagrams/02-safe-cut.svg.
The messages, the naive cut and the safe cut come from snippets/compact.py run over the first 40 turns of
snippets/transcript.py, as the post quotes it: messages[-5:] starts on turn 38's tool_result, whose tool_use is
cut away; compact(keep_last=5) walks back one message to turn 38's assistant turn and returns 7 messages. A turn
is drawn as hrn_fig_design.md section 1 draws one: the model's call blue, the observation (the tool's result)
green; the naive cut is an error (red), the safe cut a gate (purple).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Figure, text_width  # noqa: E402
from compact import compact, open_tool_uses, summarise  # noqa: E402
from transcript import transcript  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
msgs = transcript()[:81]
naive = msgs[-5:]
out = compact(msgs, summarise, keep_last=5)
assert len(msgs) == 81 and len(out) == 7 and out[1] is msgs[75] and not open_tool_uses(out)
assert naive[0]["role"] == "user" and naive[0]["content"][0]["tool_use_id"] == "tu_38"
for phrase in ("naive cut, messages[-5:]: starts with a user turn; orphaned tool_result: ['tu_38']",
               "compact(keep_last=5): 81 -> 7 messages; the kept tail starts with an assistant turn"):
    assert phrase in BODY, phrase

SHOWN = list(range(73, 81))                       # turns 37 to 40: assistant, user, assistant, user, ...


def tid(i):
    b = msgs[i]["content"][-1] if msgs[i]["role"] == "assistant" else msgs[i]["content"][0]
    return b["id"] if msgs[i]["role"] == "assistant" else b["tool_use_id"]


fig = Figure(
    "02-safe-cut", "Cut where no tool call is left open",
    "Two rows of message cards. The top row is the request the 41st call would send, 81 messages: one card for the "
    "goal and turns 1 to 36, then turns 37 to 40, each an assistant turn carrying a tool call, in blue, and a user "
    "turn carrying its result, in green, ids tu_37 to tu_40. A red line marks messages[-5:], which cuts between "
    "the call tu_38 and its result, leaving tool_result tu_38 orphaned. A purple line one message earlier marks the "
    "safe cut, before the call tu_38. The bottom row is the compacted request, 7 messages: one user brief of earlier "
    "turns, then turn 38's call and result onward, so the roles still alternate.",
    subtitle="Turns 37 to 40 of the generated run, cut by snippets/compact.py with keep_last=5.",
    data_w=True)

X0, LEAD, CW, GAP, CH = 40, 136, 84, 8, 64
XS = {i: X0 + LEAD + GAP + k * (CW + GAP) for k, i in enumerate(SHOWN)}
TOP, BOT = 184, 340


def chip(x, y, i):
    call = msgs[i]["role"] == "assistant"
    fig.card(x, y, CW, CH, radius=4, color="model" if call else "state")
    fig.text(x + CW // 2, y + 26, "call" if call else "result", "label", anchor="middle")
    fig.text(x + CW // 2, y + 48, tid(i), "code", anchor="middle")


fig.text(X0, 128, "Before: the request the 41st call would send, 81 messages", "head")
fig.card(X0, TOP, LEAD, CH, radius=4)
fig.text(X0 + LEAD // 2, TOP + 26, "goal and", "label", anchor="middle")
fig.text(X0 + LEAD // 2, TOP + 48, "turns 1 to 36", "label", anchor="middle")
for i in SHOWN:
    chip(XS[i], TOP, i)
for i, turn in zip(SHOWN[::2], range(37, 41)):
    fig.text(XS[i] + CW + GAP // 2, TOP + CH + 20, f"turn {turn}", "tick", anchor="middle")

naive_x = XS[76] - GAP // 2
safe_x = XS[75] - GAP // 2
fig.edge((naive_x, TOP - 32), (naive_x, TOP + CH + 8), color="error", width=2.5)
fig.edge((safe_x, TOP - 32), (safe_x, TOP + CH + 8), color="gate", width=2.5)
fig.text(naive_x + 8, TOP - 16, "messages[-5:]", "code", color="error")
fig.text(naive_x + 12 + int(text_width("messages[-5:]", 14, mono=True)), TOP - 16,
         "starts on the result tu_38, with no call", "label", color="error")
fig.text(safe_x - 8, TOP - 16, "safe cut: no call left open", "label", anchor="end", color="gate")

fig.text(X0, BOT - 16, "After: compact(keep_last=5), 7 messages", "head")
fig.card(X0, BOT, safe_x - GAP // 2 - X0, CH, radius=4)
fig.text(X0 + 16, BOT + 26, "user: brief of earlier turns", "label")
fig.text(X0 + 16, BOT + 48, "goal, decisions, files, checks, readings", "note")
for i in SHOWN[2:]:
    chip(XS[i], BOT, i)
fig.text(X0, BOT + CH + 32, "The brief is a user turn of its own, so the roles still alternate: user, then the "
         "call that opens the tail.", "note")
fig.caption("A cut by count orphans a result half the time; walking back to a call never does.")
fig.write()
