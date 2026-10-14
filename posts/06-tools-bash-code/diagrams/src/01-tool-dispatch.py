"""Post 06, the hero: the act step of the loop opened into the companion's dispatch, and three calls through it.

Run from the series root:  uv run python posts/06-tools-bash-code/diagrams/src/01-tool-dispatch.py
Writes posts/06-tools-bash-code/diagrams/01-tool-dispatch.svg.
The stages are the companion's own order (code/06-tools-and-bash): ToolRegistry.dispatch() validates against the
schema, then calls the bash tool, which checks its deny-list, hands the command to the runner, and shapes the
result with the exit prefix. Roles as hrn_fig_design.md: the model's request blue, gates purple, actions orange,
the observation green, a refused call red. The three calls are section 7's; every string the figure prints is
computed here by the companion's dispatch() with an injected runner that runs nothing (as snippets/three_gates.py
does) and asserted to appear in the post's quoted output.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "06-tools-and-bash" / "src"))
from figkit import Figure  # noqa: E402
from tools import DENY, ToolRegistry, make_bash_tool  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
ran = []


def runner(command, timeout):
    ran.append(command)
    return ("cat: /tmp/nope: No such file or directory", 1) if command == "cat /tmp/nope" else ("", 0)


reg = ToolRegistry([make_bash_tool(runner)])
CALLS = [{"cmd": "ls"}, {"command": "rm -rf /"}, {"command": "cat /tmp/nope"}]
SEEN = [reg.dispatch("bash", c) for c in CALLS]
for s in SEEN:
    assert f"loop sees: {s}" in BODY, s
assert ran == ["cat /tmp/nope"] and len(DENY) == 12

# the strings as the cards print them, wrapped at word boundaries of the computed text
WRAPS = [
    ["error: invalid input:", "$: missing required", "property 'command';", "$: unexpected", "property 'cmd'"],
    ["blocked: command matches", "a deny-list rule", "(\\brm\\s+-[rf])"],
    ["(exit 1) cat: /tmp/nope:", "No such file or directory"],
]
for wrap, s in zip(WRAPS, SEEN):
    assert " ".join(wrap) == s, (wrap, s)

fig = Figure(
    "01-tool-dispatch", "Validate, then execute; every outcome returns as a string",
    "The act step of the loop opened into the companion's dispatch, left to right: the model emits a tool_use "
    "block (blue); a purple gate validates its input against the schema; a purple gate checks the command "
    "against the deny-list of 12 patterns; an orange step runs the command and shapes the result with its exit "
    "status; a green tool_result goes back to the model as the next observation. Three calls stop at three "
    "places. The call with the key cmd instead of command is refused by the schema check and returns error: "
    "invalid input: $: missing required property 'command'; $: unexpected property 'cmd'. The call rm -rf / "
    "is blocked by the deny-list and returns blocked: command matches a deny-list rule (\\brm\\s+-[rf]). The "
    "call cat /tmp/nope runs and returns (exit 1) cat: /tmp/nope: No such file or directory. Only the third "
    "reached the runner.",
    subtitle="The companion's dispatch() and bash tool, with three calls and the string each one returns.",
    height=720, data_w=True)

# the pipeline: five stages across, roles by colour
SW, SH, SY = 144, 88, 152
STAGES = [("model", "tool_use block", "model"), ("validate", "schema.py", "gate"),
          ("deny-list", "12 patterns", "gate"), ("run, shape", "exit status", "act"),
          ("tool_result", "observation", "state")]
xs = [40 + k * (SW + 40) for k in range(5)]
for x, (head, line, role) in zip(xs, STAGES):
    fig.card(x, SY, SW, SH, heading=head, lines=[line], style="note", color=role)
for k in range(4):
    fig.arrow((xs[k] + SW, SY + SH // 2), (xs[k + 1], SY + SH // 2))
# the observation returns to the model on the next turn
fig.arrow((xs[4] + SW // 2, SY), (xs[0] + SW // 2, SY), via=[(xs[4] + SW // 2, 120), (xs[0] + SW // 2, 120)],
          label="next turn")

# three calls, each stopped where the companion stops it
CW, CH, CY = 272, 312, 320
cards = [
    (40, "refused by the schema", "error", '{"cmd": "ls"}', WRAPS[0], "no", xs[1]),
    (344, "blocked by the deny-list", "error", '{"command": "rm -rf /"}', WRAPS[1], "no", xs[2]),
    (648, "ran, failed, reported", "act", '{"command": "cat /tmp/nope"}', WRAPS[2], "yes", xs[3]),
]
for x, head, role, call, wrap, reached, sx in cards:
    fig.card(x, CY, CW, CH, heading=head, color=role)
    fig.text(x + 16, CY + 72, "call", "note")
    fig.text(x + 16, CY + 96, call, "code")
    fig.text(x + 16, CY + 136, "the loop reads", "note")
    for k, s in enumerate(wrap):
        fig.text(x + 16, CY + 160 + 24 * k, s, "code")
    fig.text(x + 16, CY + CH - 20, f"runner reached: {reached}", "note")
    fig.arrow((sx + SW // 2, SY + SH), (sx + SW // 2, CY), color=role)

fig.caption("A bad call is not a crash: each string is the tool_result the model reads next turn.")
fig.write()
