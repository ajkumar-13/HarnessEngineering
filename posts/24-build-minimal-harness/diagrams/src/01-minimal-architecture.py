"""Post 24, the hero: Build #1 as the component map of hrn_fig_design.md section 2, cut down to its four primitives.

Run from the series root:  uv run python posts/24-build-minimal-harness/diagrams/src/01-minimal-architecture.py
Writes posts/24-build-minimal-harness/diagrams/01-minimal-architecture.svg.

The loop (component 01) is at the centre with its three steps in their roles (reason model, act act, observe
state); the tool registry (component 02, tools) is act; the verification gate (component 06) and the four exits are
gate; the report the gate sends back is error; the model seam is a neutral card, because the figure is about the
harness around the model. Every number is computed: the module sizes by snippets/line_count.py (wc -l), the
defaults by reading run()'s signature, the deny-list size from the companion's DENY. All are asserted against the
values the post states.
"""
import contextlib
import importlib.util
import inspect
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
BODY = (POST / "index.md").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location("line_count", POST / "snippets" / "line_count.py")
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
with contextlib.redirect_stdout(io.StringIO()):
    n = lc.main()
from minimal_harness import harness  # noqa: E402  (line_count put the companion on the path)

SIZE = {name: n["sizes"][name][0] for name in lc.ENGINE}
assert SIZE == {"models.py": 108, "tools.py": 160, "verify.py": 75, "harness.py": 108}
assert n["engine"] == 451 and n["deny"] == 8
defaults = inspect.signature(harness.run).parameters
MAX_ITERS, WINDOW = defaults["max_iters"].default, defaults["no_progress_window"].default
assert (MAX_ITERS, WINDOW, defaults["token_budget"].default) == (12, 3, None)
assert "451 of them engine" in BODY and "max_iters=12" in BODY

fig = Figure(
    "01-minimal-architecture", f"Build #1 is four primitives in {n['engine']} lines",
    f"The engine of Build #1 as a component map. At the centre, component 01, the loop, in harness.py "
    f"({SIZE['harness.py']} lines): reason, act, observe, joined clockwise. On the left, the model seam, "
    f"models.py ({SIZE['models.py']} lines), a scripted model in tests and the Anthropic adapter live, answers "
    f"each call; below it, component 06, verification, verify.py ({SIZE['verify.py']} lines), receives every "
    f"final answer and sends a failure report back into the loop. On the right, component 02, tools, tools.py "
    f"({SIZE['tools.py']} lines), validates each call before dispatch to bash, with {n['deny']} deny patterns, or "
    f"write_file, and returns an observation. Along the bottom the loop's four exits: (1) completed, when "
    f"the gate passes; (2) max_iters, {MAX_ITERS} by default; (3) budget, token_budget reached; (4) no_progress, "
    f"{WINDOW} identical turns of tool calls.",
    subtitle="Module sizes by wc -l, counted by snippets/line_count.py; the four exits are the only ways out.",
    data_w=True)

# the loop, centre
LOOP = Box(336, 120, 288, 232)
fig.fill(LOOP, "surface", radius=8)
fig.outline(LOOP, "ink-muted", width=1.5, radius=8)
fig.text(LOOP.x + 16, LOOP.y + 28, "01", "value", color="ink-muted")
fig.text(LOOP.x + 48, LOOP.y + 28, "loop", "label", bold=True)
fig.text(LOOP.x + 104, LOOP.y + 28, f"harness.py, {SIZE['harness.py']} lines", "note")
steps = {"reason": (Box(440, 176, 80, 32), "model"),
         "act": (Box(520, 272, 72, 32), "act"),
         "observe": (Box(368, 272, 80, 32), "state")}
for word, (b, role) in steps.items():
    fig.fill(b, f"{role}-soft", radius=8)
    fig.outline(b, role, radius=8)
    fig.text(b.x + b.w / 2, b.y + 21, word, "label", anchor="middle")
fig.arrow((512, 208), (548, 272))
fig.arrow((520, 288), (448, 288))
fig.arrow((404, 272), (456, 208))


def component(box, num, name, file, lines, role=None):
    fig.fill(box, f"{role}-soft" if role else "neutral-soft", radius=8)
    fig.outline(box, f"{role}-line" if role else "border", radius=8)
    x = box.x + 16
    if num:
        fig.text(x, box.y + 28, num, "value", color=role)
        x += 32
    fig.text(x, box.y + 28, name, "label", bold=True)
    fig.text(box.x + 16, box.y + 52, f"{file}, {SIZE[file]} lines", "note")
    for k, line in enumerate(lines):
        fig.text(box.x + 16, box.y + 76 + 20 * k, line, "label")


# the model seam and the gate, left
MODEL = Box(40, 120, 184, 104)
component(MODEL, None, "model seam", "models.py", ["scripted, or live"])
GATE = Box(40, 248, 184, 104)
component(GATE, "06", "verification", "verify.py", ["candidate in, verdict out"], role="gate")
fig.arrow((MODEL.x + MODEL.w, 160), (LOOP.x, 160), label="respond()")
fig.arrow((LOOP.x, 280), (GATE.x + GATE.w, 280), label="final answer")
fig.arrow((GATE.x + GATE.w, 328), (LOOP.x, 328), label="report", side="below", color="error")

# the registry, right
TOOLS = Box(736, 120, 184, 128)
component(TOOLS, "02", "tools", "tools.py", ["validate, dispatch", f"bash: {n['deny']} deny patterns"],
          role="act")
fig.arrow((LOOP.x + LOOP.w, 160), (TOOLS.x, 160), label="tool call")
fig.arrow((TOOLS.x, 216), (LOOP.x + LOOP.w, 216), label="observation", side="below")
fig.legend(744, 288, [dict(color="model", label="model", mark="swatch"),
                      dict(color="state", label="state", mark="swatch")], step=32)
fig.legend(840, 288, [dict(color="act", label="act", mark="swatch"),
                      dict(color="gate", label="gate", mark="swatch")], step=32)

# the four exits, bottom
EXITS = [("(1) completed", "when the gate passes"), ("(2) max_iters", f"{MAX_ITERS} turns by default"),
         ("(3) budget", "token_budget reached"), ("(4) no_progress", f"{WINDOW} identical tool turns")]
EY, EW = 400, 208
for k, (head, line) in enumerate(EXITS):
    x = 40 + k * (EW + 16)
    box = Box(x, EY, EW, 64)
    fig.fill(box, "gate-soft", radius=8)
    fig.outline(box, "gate-line", radius=8)
    fig.text(x + 16, EY + 26, head, "label", bold=True)
    fig.text(x + 16, EY + 48, line, "note")
fig.arrow((144, GATE.y + GATE.h), (144, EY), label="pass", color="gate", side="below")
fig.arrow((368, LOOP.y + LOOP.h), (368, EY), color="gate")
fig.arrow((592, LOOP.y + LOOP.h), (592, EY), color="gate")
fig.arrow((608, LOOP.y + LOOP.h), (816, EY), via=((608, 376), (816, 376)), color="gate")
fig.caption("A rejected answer goes back into the loop as a report; only a pass leaves through exit (1).")
fig.write()
