"""Post 25, hero: Build #2 as a component map of Build #1 with four layers added (hrn_fig_design.md sections 2 and 3).

Run from the series root:  uv run python posts/25-build-harness-plus/diagrams/src/01-layered-harness.py
Writes posts/25-build-harness-plus/diagrams/01-layered-harness.svg.

Build #1's engine on the left (the loop, its tool registry and its four exits; no verifier, because this
companion ships none). Each tool call leaves the act step and meets the pre-tool hook, then the approval gate,
then registry.dispatch, in the order _gated_dispatch in code/25-harness-plus/src/harness_plus/harness.py runs
them (asserted below against the source). The sandbox is drawn inside the bash tool only, because it lives in
Sandbox.make_bash_tool; the delegate tool starts a sub-agent drawn as a second loop in its own boundary; the
tracer is the state-coloured frame around all of it. The tool names and the four outcome tags are read from the
companion and asserted.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Figure, Box  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
HARNESS = (ROOT / "code" / "25-harness-plus" / "src" / "harness_plus" / "harness.py").read_text(encoding="utf-8")
MAIN = (ROOT / "code" / "25-harness-plus" / "src" / "harness_plus" / "__main__.py").read_text(encoding="utf-8")
order = [HARNESS.index(s) for s in ("hooks.check(", "approval.needs_approval(", "registry.dispatch(")]
assert order == sorted(order), "the gate order in _gated_dispatch changed"
for tag in ('"blocked"', '"denied"', '"refused"', '"ok"'):
    assert tag in HARNESS, tag
for tool in ("make_bash_tool", "make_delegate_tool", "make_write_file_tool(workspace, sensitive=True)"):
    assert tool in MAIN, tool
assert "verify" not in HARNESS.split("def run(")[1].split(")")[0], "Build #2's run() now takes a verifier"

fig = Figure(
    "01-layered-harness", "Every tool call meets the gates in one order",
    "The component map of Build #2. On the left, Build #1's engine: the loop of reason, act and observe, the tool "
    "registry and the four exits, with no verification gate. Each tool call leaves the act step and meets a "
    "pre-tool hook, tagged blocked when it stops a call, then an approval gate for sensitive tools, tagged denied, "
    "then registry.dispatch. Dispatch reaches three tools: bash, the only tool inside the sandbox, tagged refused; "
    "write_file, marked sensitive; and delegate, which starts a sub-agent, a second loop in its own context that "
    "returns only its answer. A tracer frame around everything records a span for each step.",
    subtitle="Build #1's engine, unchanged; a hook and an approval gate on every call, a sandbox inside bash.",
    height=720, data_w=True)

# the tracer: a state frame around the whole build
fig.outline(Box(40, 104, 880, 520), "state", width=1.5, radius=8)
fig.text(64, 136, "tracer: a span for every run, iteration, model call and tool call", "label", color="state")


def pill(b, word, role):
    fig.fill(b, f"{role}-soft", radius=8)
    fig.outline(b, role, radius=8)
    fig.text(b.x + b.w / 2, b.y + 21, word, "label", anchor="middle")


# Build #1's engine
eng = Box(72, 168, 248, 304)
fig.fill(eng, "surface", radius=8)
fig.outline(eng, "ink-muted", width=1.5, radius=8)
fig.text(96, 200, "Build #1's engine", "head")
reason, act, observe = Box(96, 224, 96, 32), Box(200, 288, 96, 32), Box(96, 352, 96, 32)
pill(reason, "reason", "model")
pill(act, "act", "act")
pill(observe, "observe", "state")
fig.arrow((168, 256), (224, 288))
fig.arrow((200, 312), (168, 352))
fig.arrow((120, 352), (120, 256))
fig.text(96, 416, "tool registry, exits (1) to (4)", "label")
fig.text(96, 444, "no verification gate", "note")

# the gates, in _gated_dispatch's order
GATE_Y, GATE_H = 168, 64
hook, appr, disp = Box(376, GATE_Y, 152, GATE_H), Box(552, GATE_Y, 152, GATE_H), Box(728, GATE_Y, 176, GATE_H)
for b, head, line in ((hook, "pre-tool hook", "every tool"), (appr, "approval gate", "sensitive tools")):
    fig.fill(b, "gate-soft", radius=8)
    fig.outline(b, "gate", radius=8)
    fig.text(b.x + 16, b.y + 26, head, "label", bold=True)
    fig.text(b.x + 16, b.y + 48, line, "note")
fig.card(disp.x, disp.y, disp.w, disp.h)
fig.text(disp.x + 16, disp.y + 38, "registry.dispatch", "code")
fig.text(hook.x + 16, 256, "blocked", "label", color="error")
fig.text(appr.x + 16, 256, "denied", "label", color="error")
fig.arrow((296, 304), (376, 200), via=[(344, 304), (344, 200)])
fig.arrow((528, 200), (552, 200))
fig.arrow((704, 200), (728, 200))

# the tools behind dispatch; the sandbox frame holds only bash
TOOL_Y = 320
sand = Box(376, TOOL_Y, 144, 112)
fig.fill(sand, "gate-soft", radius=8)
fig.outline(sand, "gate", width=1.5, radius=8)
fig.text(sand.x + 16, sand.y + 96, "sandbox", "label", bold=True)
bash = Box(392, TOOL_Y + 16, 112, 48)
write, deleg = Box(600, TOOL_Y + 16, 120, 48), Box(752, TOOL_Y + 16, 136, 48)
for b, name in ((bash, "bash"), (write, "write_file"), (deleg, "delegate")):
    fig.fill(b, "act-soft", radius=8)
    fig.outline(b, "act", radius=8)
    fig.text(b.x + 16, b.y + 30, name, "code")
fig.text(sand.x + 16, sand.y + 140, "refused", "label", color="error")
fig.text(write.x, write.y + 76, "sensitive", "note")
fig.text(376, 600, "Each tool span is tagged blocked, denied, refused or ok.", "note")
fig.arrow((768, 232), (448, 336), via=[(768, 272), (448, 272)])
fig.arrow((800, 232), (664, 336), via=[(800, 288), (664, 288)])
fig.arrow((832, 232), (832, 336))

# the sub-agent: a second loop in its own boundary
ctx = Box(600, 456, 304, 112)
fig.outline(ctx, "rule", width=1.5, radius=8)
fig.text(ctx.x + 16, ctx.y + 28, "sub-agent, its own context", "label", bold=True)
fig.text(ctx.x + 16, ctx.y + 56, "the same run() and four exits", "label")
fig.text(ctx.x + 16, ctx.y + 84, "only its answer comes back", "note")
fig.arrow((832, 384), (832, 456), label="spawn", side="right")
fig.legend(72, 512, [dict(color="model", label="model", mark="swatch"),
                     dict(color="act", label="act", mark="swatch"),
                     dict(color="state", label="state", mark="swatch"),
                     dict(color="gate", label="gate", mark="swatch")])
fig.caption("The sandbox guards only bash; write_file and delegate pass the hook and the gate and then run.")
fig.write()
