"""Post 19, section 8: a guard exit writes a handoff, and a fresh run resumes from it.

Run from the series root:  uv run python posts/19-loop-engineering/diagrams/src/03-after-a-guard-exit.py
Writes posts/19-loop-engineering/diagrams/03-after-a-guard-exit.svg.
A section 4 timeline of hrn_fig_design.md, computed: the script imports posts/19-loop-engineering/snippets/
layered_loop.py, runs its demo() (the companion's run() under the snippet's controller), and draws one bar per
model call at the input tokens the call sent. Every value drawn (the bars, the refused call, the retries, the
handoff's fields, both totals and both stop reasons) is read from that run and asserted against the body. The
token sizes are the series' illustrative run, so the bars are illustrative and computed. Roles: model calls blue,
the reserve check purple, the refused call and the retries red, the handoff file green.
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
from figkit import Box, Figure  # noqa: E402

POST = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("layered_loop", POST / "snippets" / "layered_loop.py")
snip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snip)
BODY = (POST / "index.md").read_text(encoding="utf-8")

o = snip.demo()
reason1, iters1, spent1 = o["run1"]
reason2, iters2, spent2 = o["run2"]
ctl = o["ctl1"]
refused_n, refused_need = ctl.refused
RUN1 = [snip.request_size(n) for n in range(1, iters1 + 1)]
RUN2 = [snip.request_size(n) for n in range(1, iters2 + 1)]
retried = sorted({call for call, *_ in ctl.retries})
assert (reason1, iters1, spent1) == ("budget", 10, 199_500) and sum(RUN1) == spent1
assert (reason2, iters2, spent2) == ("completed", 4, 42_600) and sum(RUN2) == spent2
assert (refused_n, refused_need, snip.BUDGET) == (11, 37_000, 200_000) and retried == [4] and len(ctl.retries) == 2
assert o["handoff"]["Done"].startswith("m01, m02") and "(10 of 13)" in o["handoff"]["Done"]
assert o["next"] == ["m11", "m12", "m13"]
for phrase in ["Run 1 makes ten calls from 6,000 to 33,900 input tokens, call 4 retried twice",
               "refuses call 11, 37,000 tokens, at 199,500 spent", "makes four calls, 42,600 tokens"]:
    assert phrase in BODY, phrase


def fmt(v):
    return f"{v:,}"


fig = Figure(
    "03-after-a-guard-exit", "A guard exit hands off; a fresh run finishes",
    f"Input tokens sent on each model call of two runs, one bar per call. Run 1 makes {iters1} calls, rising from "
    f"{fmt(RUN1[0])} to {fmt(RUN1[-1])} tokens; call 4 is retried twice after a rate limit and an overload. Call "
    f"{refused_n}, which would send {fmt(refused_need)}, is drawn dashed in red: the purple reserve check refuses it "
    f"at {fmt(spent1)} tokens spent against a ceiling of {fmt(snip.BUDGET)}, exit (3), budget. A green handoff file "
    f"records modules m01 to m10 done and m11 to m13 next. Run 2, a fresh context built from the file, makes "
    f"{iters2} calls from {fmt(RUN2[0])} to {fmt(RUN2[-1])} tokens, {fmt(spent2)} in all, and ends on exit (1).",
    subtitle="Computed by layered_loop.py on the illustrative run: input tokens per model call, ceiling 200,000.",
    data_w=True)

Y0, PX = 408, 0.006                  # the baseline, and pixels per token (40,000 tokens = 240)
SLOT, BW = 40, 28
X1, X2 = 96, 736                     # first slot of run 1 and of run 2


def bar_x(start, k):
    return start + (k - 1) * SLOT


# the token axis and its grid
for t in range(0, 40_001, 10_000):
    y = Y0 - PX * t
    fig.edge((92, y), (888, y), color="grid" if t else "ink-muted", width=0.75 if t else 1)
    fig.text(84, y + 5, fmt(t), "tick", anchor="end")
fig.text(40, 152, "input tokens sent", "note")

with fig.data():
    for k, v in enumerate(RUN1, 1):
        fig.fill(Box(bar_x(X1, k), Y0 - PX * v, BW, PX * v), "model-soft", fit=False)
        fig.outline(Box(bar_x(X1, k), Y0 - PX * v, BW, PX * v), "model", width=1)
    gx = bar_x(X1, refused_n)
    fig.outline(Box(gx, Y0 - PX * refused_need, BW, PX * refused_need), "error", width=1.5, dash="proj")
    for k, v in enumerate(RUN2, 1):
        fig.fill(Box(bar_x(X2, k), Y0 - PX * v, BW, PX * v), "model-soft", fit=False)
        fig.outline(Box(bar_x(X2, k), Y0 - PX * v, BW, PX * v), "model", width=1)

# call numbers under each run
for k in range(1, refused_n + 1):
    fig.text(bar_x(X1, k) + BW // 2, 428, str(k), "tick", anchor="middle")
for k in range(1, iters2 + 1):
    fig.text(bar_x(X2, k) + BW // 2, 428, str(k), "tick", anchor="middle")
fig.text(X1, 456, "model calls, run 1", "note")
fig.text(X2, 456, "run 2", "note")

# run 1: the refused call and the retries
fig.text(X1, 128, f"run 1: {fmt(spent1)} tokens, exit (3), budget", "head")
fig.marker(gx + BW // 2, 168, "diamond", "gate", size=16)
fig.text(gx + BW // 2 - 16, 172, f"reserve refuses call {refused_n}: {fmt(spent1)} + {fmt(refused_need)} "
         f"> {fmt(snip.BUDGET)}", "label", anchor="end", color="gate")
r4 = bar_x(X1, retried[0]) + BW // 2
fig.text(r4, Y0 - PX * RUN1[retried[0] - 1] - 24, "2 retries", "note", anchor="middle", color="error")

# the handoff between the runs
HX, HY, HW = 552, 248, 152
fig.card(HX, HY, HW, 104, heading="handoff.md", lines=["done m01 to m10", "next m11 to m13"], style="note",
         color="state")
fig.arrow((gx + BW + 4, HY + 52), (HX, HY + 52))
fig.arrow((HX + HW, HY + 52), (X2 - 4, HY + 52))

# run 2
fig.text(X2, 128, f"run 2: {fmt(spent2)}, exit (1)", "head")
fig.text(bar_x(X2, iters2) + BW // 2, Y0 - PX * RUN2[-1] - 12, "answer", "note", anchor="middle")

fig.caption("The reserve stops run 1 one call short of the ceiling; the handoff is all that run 2 reads.")
fig.write()
