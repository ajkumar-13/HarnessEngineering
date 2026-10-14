"""Post 06, section 6: the same capability defined twice, and what the companion's validator does with one stray call.

Run from the series root:  uv run python posts/06-tools-bash-code/diagrams/src/03-schema-that-teaches.py
Writes posts/06-tools-bash-code/diagrams/03-schema-that-teaches.svg.
A section 3 form of hrn_fig_design.md, two cards side by side (never a Venn diagram). The right-hand definition is
read from the post's own JSON fence; the left-hand one is the post's pytest_invoke (two-word description, one free
args string). Token sizes are counted with tiktoken's o200k_base encoding over the compact JSON, as
snippets/run_tests_schema.py counts them, and the right-hand count is asserted against the post's quoted output.
The verdicts on the stray call {"scope": "everything"} come from the companion's validate(), imported unchanged.
Markers 1 to 4 are the four rules of section 6, asserted present in the body.
"""
import json
import re
import sys
from pathlib import Path

import tiktoken

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST.parents[1] / "code" / "06-tools-and-bash" / "src"))
from figkit import Box, Figure  # noqa: E402
from tools import validate  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")
RUN_TESTS = json.loads(next(b for b in re.findall(r"```json\n(.*?)```", BODY, re.S) if '"name": "run_tests"' in b))
PYTEST_INVOKE = {"name": "pytest_invoke", "description": "Invokes pytest.",
                 "input_schema": {"type": "object", "properties": {"args": {"type": "string"}}}}
ENC = tiktoken.get_encoding("o200k_base")
TOK = {d["name"]: len(ENC.encode(json.dumps(d))) for d in (PYTEST_INVOKE, RUN_TESTS)}
assert f"run_tests definition: {TOK['run_tests']} tokens (o200k_base estimate)" in BODY
STRAY = {"scope": "everything"}
LEFT_ERR = validate(STRAY, PYTEST_INVOKE["input_schema"])
RIGHT_ERR = validate(STRAY, RUN_TESTS["input_schema"])
assert LEFT_ERR == [] and len(RIGHT_ERR) == 2
for rule in ("**Name for the action, not the implementation.**", "**Write the description for the caller, not the maintainer.**",
             "**Constrain the input.**", "**Return errors as information.**", "`pytest_invoke`"):
    assert rule in BODY, rule
DESC = RUN_TESTS["description"]
DESC_LINES = ['"Run the suite and return the', 'failures. Use after any code edit.', 'Do NOT use to read a file: use', 'bash for that."']
assert " ".join(DESC_LINES) == f'"{DESC}"'
assert RUN_TESTS["input_schema"]["required"] == ["path"] and RUN_TESTS["input_schema"]["additionalProperties"] is False
ENUM = RUN_TESTS["input_schema"]["properties"]["scope"]["enum"]

fig = Figure(
    "03-schema-that-teaches", "A schema that teaches, and one that only describes",
    f"The same capability defined twice. Left, pytest_invoke: the description \"Invokes pytest.\" and one optional "
    f"free-form args string, about {TOK['pytest_invoke']} tokens; the companion's validator accepts the stray "
    f"call scope: everything as valid. Right, run_tests: a description that says what it returns, when to use it "
    f"and that it is not for reading a file, a required path, a scope limited to unit, integration or all, no "
    f"additional properties, and errors returned as strings, about {TOK['run_tests']} tokens; the validator "
    f"refuses the same stray call with two errors, the missing path and the scope outside its enum. Numbered "
    f"markers 1 to 4 place the four rules: name for the action, describe for the caller, constrain the input, "
    f"return errors as information.",
    subtitle="Token sizes are tiktoken o200k_base estimates; the verdicts are the companion's validate().",
    height=720, data_w=True)

LX, RX, CW, TOP = 40, 496, 424, 120


def marker(x, y, n):
    fig.node(x, y - 5, r=12, label=str(n), color="gate")


# left: only describes
fig.card(LX, TOP, CW, 432, heading="only describes")
left = ["name: pytest_invoke", 'description: "Invokes pytest."', "input: args: string"]
for k, s in enumerate(left):
    fig.text(LX + 16, TOP + 72 + 24 * k, s, "code")
for k, s in enumerate(["the model must guess what args holds", "nothing says when not to call it",
                       "nothing is required or forbidden", "a stray call reaches pytest"]):
    fig.text(LX + 16, TOP + 168 + 24 * k, s, "note")

# right: teaches judgement
fig.card(RX, TOP, CW, 432, heading="teaches judgement")
right = [("name: run_tests", 1), ("description:", 2)] + [("  " + s, None) for s in DESC_LINES] + [
    ("path: string, required", 3), (f"scope: {' | '.join(ENUM)}", 3), ("additionalProperties: false", 3)]
for k, (s, n) in enumerate(right):
    y = TOP + 72 + 24 * k
    fig.text(RX + 16, y, s, "code")
    if n is not None:
        marker(RX + CW - 24, y, n)
# below a divider: what the tool does at run time, outside the definition the model reads
y = TOP + 72 + 24 * len(right) + 6
fig.edge((RX + 16, y - 16), (RX + CW - 16, y - 16), color="rule", width=1, dash="ref")
fig.text(RX + 16, y, 'at run time: errors returned as "error: ..."', "note")
marker(RX + CW - 24, y, 4)

# the stray call through the companion's validator, and the size of each definition
for x, verdict, color, tok in ((LX, "valid: accepted as it stands", "error", TOK["pytest_invoke"]),
                               (RX, f"refused: {len(RIGHT_ERR)} errors", "gate", TOK["run_tests"])):
    fig.text(x + 16, TOP + 344, '{"scope": "everything"}', "code")
    fig.text(x + 16, TOP + 368, verdict, "label", color=color)
    fig.text(x + 16, TOP + 400, f"about {tok} tokens, read on every call", "note")
fig.text(LX + 16, TOP + 320, "one stray call", "note")
fig.text(RX + 16, TOP + 320, "the same stray call", "note")

# the key to the markers
KEY = ["name for the action", "describe for the caller", "constrain the input", "errors as information"]
for k, s in enumerate(KEY):
    x = LX + 16 + k * 224
    marker(x + 8, 600, k + 1)
    fig.text(x + 32, 600, s, "label")

fig.caption("Every marked line prevents a misuse, and every line of the definition is tokens the model reads on each call.")
fig.write()
