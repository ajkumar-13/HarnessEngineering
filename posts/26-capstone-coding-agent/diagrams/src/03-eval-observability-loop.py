"""Post 26, section 7: trace to localise, A/B to decide, ratchet to keep (hrn_fig_design.md section 3).

Run from the series root:  uv run python posts/26-capstone-coding-agent/diagrams/src/03-eval-observability-loop.py
Writes posts/26-capstone-coding-agent/diagrams/03-eval-observability-loop.svg.

Four cards in a clockwise cycle: the harness run with the model held fixed (neutral), the trace that localises a
failure (state, the trace store), the A/B that decides (gate), and the ratchet that keeps the fix (state). The
values on the cards are computed: the failing span is read from a Tracer over the companion's build() on the demo
spec (snippets/spec_run.py's spec and the demo's generator); the A/B values come from snippets/ab_demo.py's arms()
and its sign test, and are asserted against the body.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, POST / "snippets" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


run_mod, ab = load("spec_run"), load("ab_demo")
from coding_agent import Tracer, build  # noqa: E402  (on the path the snippets set)
from coding_agent.__main__ import generator  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")

# the trace: the first failing attempt and its evaluate span
tracer = Tracer()
build(run_mod.demo_spec(), generator, tracer=tracer, max_attempts=3)
task = attempt = None
failing = None
for _, span in tracer.root.walk():
    if span.name == "task":
        task = span.attributes["task"]
    elif span.name == "attempt":
        attempt = span.attributes["index"]
    elif span.name == "evaluate" and span.attributes["ok"] is False and failing is None:
        failing = (task, attempt)
assert failing == ("add", 1)

# the A/B
results = ab.arms()
on_res, on_cost, _ = results[1]
off_res, off_cost, off_repeats = results[99]
n_tasks = len(ab.mkspec().tasks)
p = ab.sign_test(0, len(on_res.completed) - len(off_res.completed))
assert (len(on_res.completed), len(off_res.completed), n_tasks) == (2, 2 - 2, 2)
assert f"{on_cost.cost():.4f}" == f"{off_cost.cost():.4f}" == "0.0193" and f"{p:.2f}" == "0.50"
for phrase in ["localises a failure to attempt 1 of add, at evaluate, ok=False",
               "here 2 of 2 resolved against 0 of 2 at the same 0.0193 dollars, p = 0.50, not callable"]:
    assert phrase in BODY, phrase

fig = Figure(
    "03-eval-observability-loop", "The model stays fixed; the harness goes round",
    "Four cards in a clockwise cycle. The harness runs with the model held fixed and emits a trace. The trace "
    "localises the failure to attempt 1 of add, at evaluate, ok=False. An A/B with the model held fixed decides "
    "whether a change helps: ratchet on 2 of 2 tasks resolved, ratchet off 0 of 2, both at 0.0193 dollars; a sign "
    "test gives p = 0.50, not callable on two tasks. The ratchet keeps the fix: a rule in memory and the failing "
    "spec added to the fixed set. An arrow returns to the run with the changed harness.",
    subtitle="Computed from snippets/spec_run.py and snippets/ab_demo.py on the demo's two-task spec.",
    data_w=True)

L, R, W, H = 40, 520, 400, 112
TOP, BOT = 128, 336


def card(x, y, role, head, lines):
    b = Box(x, y, W, H)
    fig.fill(b, f"{role}-soft" if role else "neutral-soft", radius=8)
    fig.outline(b, f"{role}-line" if role else "border", radius=8)
    fig.text(x + 16, y + 32, head, "head")
    for k, (s, style) in enumerate(lines):
        fig.text(x + 16, y + 64 + k * 24, s, style)
    return b


card(L, TOP, None, "1. Run the harness", [("the model held fixed", "label"), ("every step a span", "label")])
card(R, TOP, "state", "2. Trace: localise", [(f"attempt {failing[1]} of {failing[0]}, at evaluate", "label"),
                                            ("evaluate  [ok=False]", "code")])
card(R, BOT, "gate", "3. A/B: decide", [(f"ratchet on {len(on_res.completed)} of {n_tasks}, "
                                         f"off {len(off_res.completed)} of {n_tasks}, ${on_cost.cost():.4f} each", "label"),
                                        (f"p = {p:.2f}: not callable on {n_tasks} tasks", "label")])
card(L, BOT, "state", "4. Ratchet: keep", [("a rule in memory", "label"),
                                          ("the failing spec in the fixed set", "label")])

fig.arrow((L + W, TOP + H / 2), (R, TOP + H / 2))
fig.arrow((R + W / 2, TOP + H), (R + W / 2, BOT), label="a located failure", side="right")
fig.arrow((R, BOT + H / 2), (L + W, BOT + H / 2))
fig.arrow((L + W / 2, BOT), (L + W / 2, TOP + H), label="a changed harness", side="right")

fig.caption("Trace to localise, A/B to decide, ratchet to keep; no step asks for a better model.")
fig.write()
