"""Post 26, section 3: what each generator call of the capstone's driver is handed, and what crosses the resets.

Run from the series root:  uv run python posts/26-capstone-coding-agent/diagrams/src/02-multi-context-run.py
Writes posts/26-capstone-coding-agent/diagrams/02-multi-context-run.svg.

A turn-by-turn picture (hrn_fig_design.md sections 1 and 4), computed: the script imports
posts/26-capstone-coding-agent/snippets/spec_run.py and runs its part 1 (the companion's build() on the demo's
two-task spec, with the wrapper that records what each generator call was handed). Every value drawn is read from
that run: per call, the task, whether a failure report was handed in, the number of rules in the context, the file
written, the verdict; after each call, the commits, the rules held and the meter's running cost. The cost after k
calls is the companion's CostMeter fed k times the driver's default tokens_per_attempt, asserted against the run's
final meter. Post 18's figure 04 plots a Ralph window's tokens; this one shows the capstone's three contexts.
Roles: the context card neutral, the candidate model blue, the verdict a gate (purple), the failure red, the
three stores state green.
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
spec = importlib.util.spec_from_file_location("spec_run", POST / "snippets" / "spec_run.py")
snip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snip)
from coding_agent import CostMeter, build  # noqa: E402  (on the path spec_run set)

BODY = (POST / "index.md").read_text(encoding="utf-8")
with contextlib.redirect_stdout(io.StringIO()):
    res, calls = snip.part1()

in_tok, cached_tok, out_tok = inspect.signature(build).parameters["tokens_per_attempt"].default
running = []
meter = CostMeter()
for _ in calls:
    meter.add(input_tokens=in_tok, cached_tokens=cached_tok, output_tokens=out_tok)
    running.append(meter.cost())
assert abs(running[-1] - res.cost.cost()) < 1e-12
outcomes = []
for i, c in enumerate(calls):
    later_same = i + 1 < len(calls) and calls[i + 1]["task"] == c["task"]
    outcomes.append("fail" if later_same else "pass")
commits = [sum(o == "pass" for o in outcomes[:i + 1]) for i in range(len(calls))]
rules_after = [1 if i >= 0 and "fail" in outcomes[:i + 1] else 0 for i in range(len(calls))]
assert [c["task"] for c in calls] == ["add", "add", "is_even"]
assert [c["feedback"] is not None for c in calls] == [False, True, False]
assert [c["rules"] for c in calls] == [0, 1, 1]
assert outcomes == ["fail", "pass", "pass"] and commits == [0, 1, 2] and rules_after == [1, 1, 1]
assert [f"{v:.5f}" for v in running] == ["0.00645", "0.01290", "0.01935"]
assert res.stop_reason == "spec_complete" and len(res.rules_learned) == 1
for phrase in ["call 1 on task add with no report and 0 rules, verdict fail",
               "call 2 on add with the last report and 1 rule, verdict pass",
               "call 3 on is_even with no report and 1 rule, verdict pass",
               "commits rise 0, 1, 2", "the ratchet holds 1 rule after each call",
               "0.00645, 0.01290 and 0.01935 dollars"]:
    assert phrase in BODY, phrase

fig = Figure(
    "02-multi-context-run", "Each call starts fresh; the stores carry on",
    "Three generator calls of the capstone's driver on the demo spec, left to right, each a fresh context showing "
    "what the driver handed it. Call 1, task add: no report, 0 rules; it writes calc.py and the verdict is fail, "
    "drawn red, and the ratchet learns one rule. Call 2, task add: the last report and 1 rule; calc.py, verdict "
    "pass. Call 3, task is_even: no report, because the report stays with its task, and 1 rule; parity.py, verdict "
    "pass. Below, the state after each call: commits 0, 1, 2; rules held 1, 1, 1; the cost meter at 0.00645, "
    "0.01290 and 0.01935 dollars. The run stops on exit (1), spec complete.",
    subtitle="Computed by snippets/spec_run.py: the companion's build() on its demo spec, stopping on exit (1).",
    height=720, data_w=True)

LABEL_X = 40
COLS = [168, 432, 696]          # left edge of each call's column
CW = 200


def money(v):
    return f"${v:.5f}"


# the three contexts
for i, (c, x) in enumerate(zip(calls, COLS)):
    card = Box(x, 120, CW, 128)
    fig.fill(card, "neutral-soft", radius=8)
    fig.outline(card, "border", radius=8)
    fig.text(x + 16, 148, f"call {i + 1}: {c['task']}", "head")
    fig.text(x + 16, 172, "fresh context", "note")
    fig.text(x + 16, 204, "report: " + ("last one" if c["feedback"] else "none"), "label")
    fig.text(x + 16, 228, f"rules: {c['rules']}", "label")
    # the candidate the call wrote
    cand = Box(x + 16, 272, CW - 32, 40)
    fig.fill(cand, "model-soft", radius=8)
    fig.outline(cand, "model", radius=8)
    fig.text(x + 32, 298, "writes", "label")
    fig.text(x + 88, 298, c["files"][0], "code")
    fig.arrow((x + CW / 2, 248), (x + CW / 2, 272))
    # the verdict, a gate
    v = Box(x + 16, 336, CW - 32, 40)
    bad = outcomes[i] == "fail"
    fig.fill(v, "error-soft" if bad else "gate-soft", radius=8)
    fig.outline(v, "error" if bad else "gate", radius=8)
    fig.text(x + 32, 362, f"verdict: {outcomes[i]}", "label", color="error" if bad else None)
    fig.arrow((x + CW / 2, 312), (x + CW / 2, 336))

# row labels, and what crosses between the two contexts of one task
for y, word in ((204, "handed in"), (298, "candidate"), (362, "gate")):
    fig.text(LABEL_X, y, word, "note")
fig.arrow((COLS[0] + CW, 200), (COLS[1], 200), label="report")

# the stores, after each call
fig.edge((LABEL_X, 408), (920, 408), color="rule")
fig.text(LABEL_X, 436, "after each call", "head")
LANES = [("rules held", [str(n) for n in rules_after]),
         ("commits", [str(n) for n in commits]),
         ("cost meter", [money(v) for v in running])]
for k, (name, values) in enumerate(LANES):
    y = 456 + k * 56
    fig.text(LABEL_X, y + 26, name, "label")
    for x, val in zip(COLS, values):
        b = Box(x, y, CW, 40)
        fig.fill(b, "state-soft", radius=8)
        fig.outline(b, "state-line", radius=8)
        fig.text(x + CW / 2, y + 26, val, "value", anchor="middle", color="state")
fig.arrow((COLS[0] + CW / 2, 376), (COLS[0] + CW / 2, 456), color="error")
fig.text(COLS[0] + CW / 2 + 12, 436, "learns a rule", "note", color="error")

fig.caption("The report stays with its task; the rule, the commits and the meter cross every reset.")
fig.write()
