"""Post 12, section 3: the sprint contract, frozen before the work, against the three attempts of the snippet's run.

Run from the series root:  uv run python posts/12-planner-generator-evaluator/diagrams/src/02-sprint-contract.py
Writes posts/12-planner-generator-evaluator/diagrams/02-sprint-contract.svg.
A section 4 timeline of hrn_fig_design.md read as a table: the negotiation (draft, refusal, frozen contract) runs
left to right above, then each criterion's result on each attempt. Every cell is computed here by running the
snippet's checks and its judge rule on the three scripted versions of parse.py, and the verdict row and the digest
are asserted against what snippets/three_roles.py prints and the body quotes. Roles: the contract is state
(green), the refused draft criterion and every unmet cell are red, the verdicts are the gate's (purple).
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
import three_roles as tr  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
kept, refused = tr.review(tr.plan(tr.TASK))
contract = tr.Contract(kept)
DIGEST = contract.digest()
assert [c.number for c in refused] == [7]

LOGGED = tr.CHANGELOG + "- 0.2.0: parse() change for the export\n"
RESULTS = []                                        # RESULTS[attempt][criterion index] -> met?
for source in tr.VERSIONS:
    work = {"parse.py": source, "CHANGELOG.md": LOGGED}
    RESULTS.append([(c.check(work)[0] if c.check else tr.understandable(work)[0]) for c in kept])
UNMET = [[c.number for c, ok in zip(kept, row) if not ok] for row in RESULTS]
assert UNMET == [[2, 3, 6], [6], []], UNMET

out = io.StringIO()
with contextlib.redirect_stdout(out):
    tr.main()
printed = out.getvalue()
for line in (f"contract frozen before attempt 1: 6 criteria, digest {DIGEST}",
             f"attempt 1  NEEDS_WORK  digest {DIGEST}  unmet: 2, 3, 6",
             f"attempt 2  NEEDS_WORK  digest {DIGEST}  unmet: 6",
             f"attempt 3  PASS        digest {DIGEST}"):
    assert line in printed and line in BODY, line

SHORT = ["parse([]) returns []", "malformed row: ValueError names the row", "every row matches the schema",
         "public functions annotated", "CHANGELOG.md gains one line", "error understandable without source"]
VERIFIER = {"unit test": "unit test", "schema check": "schema check", "annotation check": "annotation check",
            "script": "script", "evaluator": "evaluator: judged"}

fig = Figure(
    "02-sprint-contract", "The bar is fixed before the work and never moves",
    "Above, the negotiation: the planner drafts seven criteria, the evaluator refuses criterion 7, the code is "
    f"clean, because it names nothing observable, and the contract is frozen with six criteria as digest {DIGEST} "
    "before attempt 1. Below, a table of the six criteria, each with its verifier (unit test, unit test, schema "
    "check, annotation check, script, and the evaluator for the judged sixth), against three attempts. Attempt 1 "
    "leaves criteria 2, 3 and 6 unmet: NEEDS_WORK. Attempt 2 leaves only criterion 6 unmet: NEEDS_WORK, and the "
    "evaluator's write_file call is refused. Attempt 3 meets all six: PASS. The digest is "
    f"{DIGEST} on every attempt.",
    subtitle="This post's run: one contract, three attempts, every cell computed by the snippet's checks.",
    height=720, data_w=True)

# the negotiation, left to right
fig.card(40, 112, 232, 72, color="model")
fig.text(56, 140, "planner drafts", "head", color="model")
fig.text(56, 168, "7 criteria", "label")
fig.card(344, 112, 264, 72, color="error")
fig.text(360, 140, "evaluator refuses 7", "head", color="error")
fig.text(360, 168, "\"the code is clean\": nothing observable", "label")
fig.card(680, 112, 240, 72, color="state")
fig.text(696, 140, "contract frozen", "head", color="state")
fig.text(696, 168, f"6 criteria, digest {DIGEST}", "label")
fig.arrow((272, 148), (344, 148))
fig.arrow((608, 148), (680, 148))

# the table: criteria against attempts
X, Y, RH = 40, 224, 40
W = [32, 344, 168, 112, 112, 112]
xs = [X + sum(W[:j]) for j in range(len(W))]
for a, row in enumerate(RESULTS):
    for i, ok in enumerate(row):
        if not ok:
            fig.fill(Box(xs[3 + a], Y + RH * (i + 1), W[3 + a], RH), "error-soft", fit=False)
rows = [["#", "criterion", "settled by", "attempt 1", "attempt 2", "attempt 3"]]
for i, c in enumerate(kept):
    rows.append([str(c.number), SHORT[i], VERIFIER[c.verifier]]
                + ["met" if RESULTS[a][i] else "unmet" for a in range(3)])
fig.table(X, Y, rows, W, row_h=RH, col_align=["start", "start", "start", "middle", "middle", "middle"])

# verdicts and the digest under each attempt
VY = Y + RH * 7 + 32
fig.text(xs[2] + 8, VY, "verdict", "note")
fig.text(xs[2] + 8, VY + 28, "digest", "note")
for a, unmet in enumerate(UNMET):
    cx = xs[3 + a] + W[3 + a] // 2
    fig.text(cx, VY, "NEEDS_WORK" if unmet else "PASS", "label", anchor="middle", color="gate", bold=True)
    fig.text(cx, VY + 28, DIGEST, "label", anchor="middle")
assert "evaluator write_file refused" in printed
fig.text(xs[4] + W[4] // 2, VY + 56, "write refused", "label", anchor="middle", color="error")
fig.note(Box(X, Y + RH * 7, 504, 1), ["Five criteria are settled by code at no model call;",
                                      "only criterion 6 is ever sent to the evaluator."])

fig.caption("Attempt 2 passes every coded check and still fails: its error message reads row 2 and nothing more.")
fig.write()
