"""Post 13, section 3: the two composition rules, run through the companion's HookRegistry.

Run from the series root:  uv run python posts/13-hooks-enforcement/diagrams/src/03-gates-and-reports.py
Writes posts/13-hooks-enforcement/diagrams/03-gates-and-reports.svg.
The registry is code/13-hooks/src/hook_system (imported unchanged). Three pre-tool hooks (a stand-in secret scan
that allows, the companion's deny_list(), a stand-in permission check) see rm -rf /; three post-edit hooks (a
stand-in typecheck that finds a problem, the companion's post_edit_tests() with a failing runner, a stand-in
formatter that finds nothing) see an edit. Which hooks were called, the reason returned and the problems collected
are all recorded from the run and asserted. hrn_fig_design.md section 3: a gate is purple, a report neutral, as in
the hero; a hook that was never called is dashed.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "13-hooks" / "src"))
from figkit import Box, Figure  # noqa: E402
from hook_system.hooks import ALLOW, HookRegistry, deny_list, post_edit_tests  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
assert "**the first block wins**" in BODY and "**collect every problem**" in BODY

called, results = [], {}


def counted(name, hook):
    def run(*args):
        called.append(name)
        results[name] = hook(*args)
        return results[name]
    return run


PRE = [("secret scan", counted("secret scan", lambda tool, args: ALLOW)),
       ("deny-list", counted("deny-list", deny_list())),
       ("permission check", counted("permission check", lambda tool, args: ALLOW))]
POST_EDIT = [("typecheck", counted("typecheck", lambda path, content: f"typecheck: {path} line 3: str is not int")),
             ("tests", counted("tests", post_edit_tests(lambda: (False, "3 failed")))),
             ("formatter", counted("formatter", lambda path, content: None))]

gates = HookRegistry()
for _, h in PRE:
    gates.add_pre_tool(h)
decision = gates.check_tool("bash", "rm -rf /")
pre_called = list(called)
reports = HookRegistry()
for _, h in POST_EDIT:
    reports.add_post_edit(h)
problems = reports.after_edit("app.py", "x: int = 'one'")
post_called = called[len(pre_called):]
assert pre_called == ["secret scan", "deny-list"] and not decision.allow
assert decision.reason == "blocked: recursive delete of a broad path"
assert post_called == ["typecheck", "tests", "formatter"] and len(problems) == 2

fig = Figure(
    "03-gates-and-reports", "Gates stop at the first block; reports collect every problem",
    "Two columns run through the companion's hook registry. Left, pre-tool, the command rm -rf / meets three "
    "purple gates in order: secret scan allows; deny-list blocks; permission check, drawn dashed, is never asked. "
    "One reason returns: blocked: recursive delete of a broad path. Right, post-edit, an edit to app.py meets "
    "three neutral report hooks, and all three run: typecheck reports a problem, tests report tests failed after "
    "editing app.py: 3 failed, the formatter finds nothing. Both problems return together as one observation.",
    subtitle="Three hooks at each point, run through HookRegistry from code/13-hooks.",
    data_w=True)

left, right = fig.row(2)
CW, CHH, STEP = 248, 40, 56
VX = 248 + 40                                 # verdicts start here, relative to the panel x

# left: pre-tool, first block wins
lb = fig.panel(left, "pre-tool: first block wins")
fig.card(lb.x, lb.y, CW, CHH, color="model")
fig.text(lb.x + 16, lb.y + 26, "rm -rf /", "code")
ys = [lb.y + STEP * (k + 1) for k in range(3)]
for k, ((name, _), y) in enumerate(zip(PRE, ys)):
    ran = name in pre_called
    if ran:
        fig.card(lb.x, y, CW, CHH, color="gate")
    else:
        fig.outline(Box(lb.x, y, CW, CHH), "gate", width=1.5, dash="proj", radius=8)
    fig.text(lb.x + 16, y + 26, name, "label")
    blocked = ran and k == pre_called.index(pre_called[-1]) and not decision.allow
    verdict = "never asked" if not ran else ("block" if blocked else "allow")
    fig.text(lb.x + VX, y + 26, verdict, "label", color="error" if blocked else None, bold=blocked)
fig.arrow((lb.x + CW // 2, lb.y + CHH), (lb.x + CW // 2, ys[0]))
fig.arrow((lb.x + CW // 2, ys[0] + CHH), (lb.x + CW // 2, ys[1]))
OUT_Y = ys[2] + STEP + 16
fig.arrow((lb.x + CW, ys[1] + CHH // 2), (lb.x + CW + 16, OUT_Y), via=[(lb.x + CW + 16, ys[1] + CHH // 2)])
fig.card(lb.x, OUT_Y, lb.w, 64, color="state")
fig.text(lb.x + 16, OUT_Y + 26, "one reason returns", "note")
fig.text(lb.x + 16, OUT_Y + 48, decision.reason, "label", color="error")

# right: post-edit, collect every problem
rb = fig.panel(right, "post-edit: collect every problem")
fig.card(rb.x, rb.y, CW, CHH, color="act")
fig.text(rb.x + 16, rb.y + 26, "edit app.py", "label")
for k, ((name, _), y) in enumerate(zip(POST_EDIT, ys)):
    fig.card(rb.x, y, CW, CHH)
    fig.text(rb.x + 16, y + 26, name, "label")
    found = bool(results[name])
    fig.text(rb.x + VX, y + 26, "problem" if found else "nothing", "label",
             color="error" if found else None, bold=found)
fig.chain([Box(rb.x, rb.y, CW, CHH)] + [Box(rb.x, y, CW, CHH) for y in ys])
fig.arrow((rb.x + CW // 2, ys[2] + CHH), (rb.x + CW // 2, OUT_Y))
fig.card(rb.x, OUT_Y, rb.w, 88, color="state")
fig.text(rb.x + 16, OUT_Y + 26, "both return as one observation", "note")
for j, p in enumerate(problems):
    fig.text(rb.x + 16, OUT_Y + 48 + 24 * j, p, "label", color="error")

fig.caption("A gate saves the rest of the checks; a report saves the model a round trip.")
fig.write()
