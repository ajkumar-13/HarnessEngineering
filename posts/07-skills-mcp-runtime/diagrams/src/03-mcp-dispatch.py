"""Post 07, section 9: one MCP tool call inside the act step, across the process boundary and back.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/diagrams/src/03-mcp-dispatch.py
Writes posts/07-skills-mcp-runtime/diagrams/03-mcp-dispatch.svg.
A section 3 boundary of hrn_fig_design.md, host side in full: the model (blue), the client (neutral, part of the
harness), the tool running in the server (act, orange), the process boundary as a gate line, the validation gate
(purple diamond) on the way back, the observation (state green) and the error path (red). The request frame and
the outcomes are what snippets/mcp_dispatch.py prints, captured and asserted below; no numbers.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
from mcp_dispatch import DownClient, StubClient, call_mcp_tool, validate  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
out = io.StringIO()
with contextlib.redirect_stdout(out):
    ok = call_mcp_tool(StubClient(), "create_ticket", {"title": "Disk full on web-03"})
frame = json.loads(out.getvalue().split("client sends:", 1)[1])
assert frame["method"] == "tools/call" and frame["params"]["name"] == "create_ticket" and frame["jsonrpc"] == "2.0"
assert set(frame["params"]["_meta"]) == {"io.modelcontextprotocol/protocolVersion",
                                         "io.modelcontextprotocol/clientCapabilities"}
assert ok["content"][0]["text"] == "TICKET-4417 created"
assert "unavailable" in call_mcp_tool(DownClient(), "create_ticket", {})["error"]
assert validate({"text": "x"}) == {"error": "malformed tool result"}
for phrase in ("with two extra hops: through the client, and over the transport to the server",
               "messages over a transport (stdio or Streamable HTTP",
               "**Validation still applies.**", "**Failure is an observation, not a crash.**"):
    assert phrase in BODY, phrase

fig = Figure(
    "03-mcp-dispatch", "An MCP call crosses a process boundary and back",
    "One loop turn in six steps. In the host, which is the harness, the model emits a tool call (1) to the MCP "
    "client, which sends a JSON-RPC tools/call request for create_ticket (2) across the process boundary over stdio "
    "or HTTP. In the server process the tool runs (3) and the result returns (4). Back in the host the result passes "
    "a validation gate (5) and becomes the next observation for the model (6). A timeout or a result of the wrong "
    "shape becomes an error observation instead of a crash. The request frame is shown as code.",
    subtitle="Host side in full; the server only runs the tool. Frame printed by snippets/mcp_dispatch.py.",
    data_w=True)

# the two processes and the boundary between them
fig.outline(Box(40, 104, 416, 352), "rule", width=1, radius=8)
fig.text(56, 132, "host: the harness", "head")
fig.outline(Box(520, 104, 400, 352), "rule", width=1, radius=8)
fig.text(536, 132, "MCP server: another process", "head")
with fig.data():
    fig.edge((488, 104), (488, 456), color="gate", width=1.5, dash="proj")
fig.text(488, 480, "process boundary: stdio or HTTP", "label", anchor="middle", color="gate")

# 1: the model emits a tool call to the client
fig.card(72, 160, 128, 48, color="model")
fig.text(136, 188, "model", "label", anchor="middle", bold=True)
fig.card(256, 160, 136, 48)
fig.text(324, 188, "MCP client", "label", anchor="middle")
fig.arrow((200, 184), (256, 184))
fig.text(228, 176, "1", "label", anchor="middle")

# 2 to 4: the request out, the tool runs, the result back
fig.card(648, 160, 240, 48, color="act")
fig.text(768, 188, "3  create_ticket runs", "label", anchor="middle")
fig.arrow((392, 172), (648, 172))
fig.text(532, 164, "2  tools/call", "label")
fig.arrow((648, 200), (392, 200))
fig.text(532, 224, "4  result", "label")

# the frame the client writes and the result it gets, as the snippet printed them
fig.text(552, 268, "the request frame", "note")
fig.code_block(552, 292, ['{"jsonrpc": "2.0", "id": 1,',
                          ' "method": "tools/call",',
                          ' "params": {"name": "create_ticket",',
                          '  "arguments": {...}, "_meta": {...}}}'])
fig.text(552, 400, "the result", "note")
fig.code_block(552, 424, ['"text": "TICKET-4417 created"'])

# 5: validation gate, 6: the observation goes back to the model
fig.arrow((324, 208), (324, 280))
with fig.data():
    fig.marker(324, 244, "diamond", "gate", size=12)
fig.text(340, 248, "5  validate", "label", color="gate")
fig.card(256, 280, 136, 48, color="state")
fig.text(324, 308, "observation", "label", anchor="middle")
fig.arrow((256, 304), (136, 208), via=[(136, 304)])
fig.text(152, 296, "6  next turn", "label")

# the failure path: still an observation
fig.card(72, 368, 352, 56, color="error")
fig.text(88, 392, "timeout or wrong shape:", "label", color="error")
fig.text(88, 412, "an error observation, not a crash", "label", color="error")

fig.caption("Only the result crosses back, and the harness checks it before the model reads it.")
fig.write()
