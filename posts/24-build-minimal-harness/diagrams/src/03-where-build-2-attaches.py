"""Post 24, section 10: where post 25's four layers attach to the tool-call path Build #1 leaves open.

Run from the series root:  uv run python posts/24-build-minimal-harness/diagrams/src/03-where-build-2-attaches.py
Writes posts/24-build-minimal-harness/diagrams/03-where-build-2-attaches.svg.

A boundary-and-gate form (hrn_fig_design.md section 3): two lanes of the same path, model to loop to registry to
bash tool to runner. Top, Build #1 as code/24-minimal-harness ships it; below, Build #2 as code/25-harness-plus
ships it, with the hook and the approval gate as gate diamonds on the arrow they intercept, the sandbox as a gate
frame around the bash tool and its runner, the sub-agent as one more tool in the registry, and the tracer as a
state frame around the run (observability is state in post 02's map). Every fact drawn is read from the two
companions, imported or read unchanged, and asserted: the run() parameters of each build, the order of the checks in
Build #2's _gated_dispatch, the deny-list size and shell=True of Build #1, the default allow-list and the argv
runner of Build #2, and the delegate tool.
"""
import inspect
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
CODE = Path(__file__).resolve().parents[4] / "code"
sys.path.insert(0, str(CODE / "24-minimal-harness" / "src"))
sys.path.insert(0, str(CODE / "25-harness-plus" / "src"))
from figkit import Box, Figure  # noqa: E402
import minimal_harness  # noqa: E402
import harness_plus.harness as plus  # noqa: E402
import harness_plus.sandbox as sandbox  # noqa: E402
import harness_plus.subagent as subagent  # noqa: E402

one = set(inspect.signature(minimal_harness.run).parameters)
two = set(inspect.signature(plus.run).parameters)
assert two - one == {"hooks", "approval", "tracer", "span_name"}, two - one
assert len(minimal_harness.DENY) == 8
assert "shell=True" in inspect.getsource(minimal_harness.subprocess_runner)
assert "shell=False" in inspect.getsource(sandbox.subprocess_runner)
ALLOW = sandbox.Sandbox().allow
assert ALLOW == ["echo", "ls", "cat", "git"]
gated = inspect.getsource(plus._gated_dispatch)
order = [gated.index(s) for s in ("hooks.check(", "approval.needs_approval(", "registry.dispatch(")]
assert order == sorted(order)
assert subagent.make_delegate_tool(lambda s: s).name == "delegate"

fig = Figure(
    "03-where-build-2-attaches", "Build #2 adds its gates to the same tool-call path",
    "Two lanes of one tool-call path: model, loop, registry, bash tool, runner. Top, Build #1: the registry "
    "validates the call, the bash tool checks 8 deny-list patterns, and the runner executes the string with "
    "shell=True. Bottom, Build #2: 1, a pre-tool hook that can block, and 2, an approval gate for sensitive calls, "
    "sit on the arrow from the loop to the registry, in the order its _gated_dispatch checks them; 3, a sandbox "
    "frame around the bash tool, whose allow-list is echo, ls, cat and git, and a runner that executes an argument "
    "list without a shell; 4, a delegate tool in the registry that runs a sub-agent in its own loop; and a brace "
    "under the lane for the tracer, one span per run, iteration and call.",
    subtitle="Top, code/24-minimal-harness as shipped; below, code/25-harness-plus, hook and approval in checking order.",
    data_w=True)

XS = {"model": (40, 96), "loop": (168, 96), "registry": (440, 136), "bash": (624, 128), "runner": (784, 124)}
H = 56


def card(key, y, title, line, role=None, mono=False):
    x, w = XS[key]
    box = Box(x, y, w, H)
    fig.fill(box, f"{role}-soft" if role else "neutral-soft", radius=8)
    fig.outline(box, f"{role}-line" if role else "border", radius=8)
    fig.text(x + 12, y + 24, title, "label", bold=True)
    fig.text(x + 12, y + 44, line, "code" if mono else "note")
    return box


def path(y, label_runner, line_bash, line_runner):
    boxes = [card("model", y, "model", "a seam"), card("loop", y, "loop", "run()"),
             card("registry", y, "registry", "validate", "act"), card("bash", y, label_runner, line_bash, "act"),
             card("runner", y, "runner", line_runner, "act")]
    mid = y + H // 2
    fig.arrow((136, mid), (168, mid))
    fig.arrow((576, mid), (624, mid))
    fig.arrow((752, mid), (784, mid))
    return boxes, mid


# Build #1
fig.text(40, 128, "Build #1, post 24", "head")
_, mid1 = path(144, "bash tool", f"{len(minimal_harness.DENY)} deny patterns", "shell=True")
fig.arrow((264, mid1), (440, mid1), label="tool call")

# Build #2
fig.text(40, 248, "Build #2, post 25", "head")
Y2 = 280
_, mid2 = path(Y2, "sandbox bash", "allow-list of " + str(len(ALLOW)), "argv, no shell")
fig.arrow((264, mid2), (440, mid2))
for k, (x, word) in enumerate(((304, "hook"), (392, "approval"))):
    fig.marker(x, mid2, "diamond", "gate", size=20)
    fig.text(x, Y2 - 8, f"{k + 1} {word}", "label", anchor="middle", color="gate")
FRAME = Box(608, Y2 - 12, 312, H + 24)
fig.outline(FRAME, "gate", width=1.5, radius=8)
fig.text(FRAME.x + 12, FRAME.y - 8, "3 sandbox", "label", color="gate")
SUB = Box(440, 368, 312, 48)
fig.fill(SUB, "act-soft", radius=8)
fig.outline(SUB, "act-line", radius=8)
fig.text(SUB.x + 12, SUB.y + 30, "4 delegate tool: a sub-agent, its own loop", "label")
fig.arrow((488, Y2 + H), (488, SUB.y))
fig.brace(40, 920, 432, label="tracer: one span per run, iteration and call, around all of it", color="state")

fig.caption("Hook, approval and tracer are new parameters of run(); the sandbox and the sub-agent arrive as tools.")
fig.write()
