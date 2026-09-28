"""Offline tests for Build #1 — the gate and every stop condition, no API key.

The safety surface is the set of exits and the verification gate: each test
forces one behaviour and asserts the harness takes the right exit with the right
``verified`` flag.
"""
from minimal_harness import (Result, ScriptedModel, StopReason, ToolRegistry,
                             Workspace, make_bash_tool, make_write_file_tool,
                             python_function_tests, run, text_response,
                             tool_response, validate)
from minimal_harness.verify import VerifyResult
import pathlib
import tempfile

FIXED = "def is_palindrome(s):\n    return s == s[::-1]\n"
BUGGY = "def is_palindrome(s):\n    return True\n"


def _palindrome_verifier():
    return python_function_tests(
        "solution.py", "is_palindrome",
        [(("racecar",), True), (("abc",), False), (("",), True)],
    )


def test_gate_passes_verified_solution():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws)])
    model = ScriptedModel([
        tool_response("write_file", {"path": "solution.py", "content": FIXED}),
        text_response("done"),
    ])
    res = run(model, reg, "write it", verify=_palindrome_verifier(), workspace=ws)
    assert res.stop_reason is StopReason.COMPLETED
    assert res.verified is True
    assert res.iterations == 2


def test_gate_rejects_then_accepts_after_feedback():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws)])
    model = ScriptedModel([
        tool_response("write_file", {"path": "solution.py", "content": BUGGY}),
        text_response("done (but it is wrong)"),
        tool_response("write_file", {"path": "solution.py", "content": FIXED}),
        text_response("fixed"),
    ])
    res = run(model, reg, "write it", verify=_palindrome_verifier(), workspace=ws)
    assert res.stop_reason is StopReason.COMPLETED
    assert res.verified is True
    # the rejection was fed back into the transcript as an observation
    feedback = [m for m in res.transcript if m["role"] == "user"
                and isinstance(m["content"], str)
                and "verification failed" in m["content"]]
    assert feedback, "the failing gate report should be injected back into the loop"


def test_no_verifier_means_final_answer_completes():
    reg = ToolRegistry([])
    model = ScriptedModel([text_response("hello")])
    res = run(model, reg, "say hi")
    assert res.stop_reason is StopReason.COMPLETED
    assert res.verified is True
    assert res.answer == "hello"


def test_max_iters_backstop_when_gate_never_passes():
    ws = Workspace()
    reg = ToolRegistry([make_write_file_tool(ws)])
    # always writes the buggy version, then says done -> gate always fails
    script = []
    for i in range(50):
        script.append(tool_response("write_file",
                                    {"path": "solution.py", "content": BUGGY},
                                    id=f"w{i}"))
        script.append(text_response("done"))
    res = run(ScriptedModel(script), reg, "loop", verify=_palindrome_verifier(),
              workspace=ws, max_iters=6)
    assert res.stop_reason is StopReason.MAX_ITERS
    assert res.verified is False
    assert res.iterations == 6


def test_budget_stops_the_run():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("ok", 0))])
    script = [tool_response("bash", {"command": f"echo {i}"}, id=f"b{i}", tokens=50)
              for i in range(100)]
    res = run(ScriptedModel(script), reg, "spend", max_iters=100, token_budget=120)
    assert res.stop_reason is StopReason.BUDGET
    assert res.tokens_used >= 120


def test_no_progress_detection():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("same", 0))])
    script = [tool_response("bash", {"command": "echo same"}, id="b", tokens=1)
              for _ in range(20)]
    res = run(ScriptedModel(script), reg, "thrash", max_iters=20,
              no_progress_window=3)
    assert res.stop_reason is StopReason.NO_PROGRESS
    assert res.iterations == 3


def test_bash_tool_denies_dangerous_commands():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("ran", 0))])
    assert "blocked" in reg.dispatch("bash", {"command": "rm -rf /"})
    assert reg.dispatch("bash", {"command": "echo hi"}) == "ran"


def test_schema_rejects_malformed_tool_call():
    reg = ToolRegistry([make_bash_tool(runner=lambda c, t: ("ran", 0))])
    # wrong key -> schema validation rejects it before the runner is touched
    out = reg.dispatch("bash", {"cmd": "echo oops"})
    assert "invalid input" in out


def test_validate_catches_missing_and_extra_properties():
    schema = {"type": "object", "properties": {"x": {"type": "string"}},
              "required": ["x"], "additionalProperties": False}
    assert validate({"x": "ok"}, schema) == []
    assert any("missing" in e for e in validate({}, schema))
    assert any("unexpected" in e for e in validate({"x": "ok", "y": 1}, schema))


def test_budget_stops_the_run_when_the_gate_keeps_rejecting():
    """The BUDGET exit must be reachable on the gate-rejection path.

    A rejected final answer is a spent model call like any other. When the
    budget check sat below the ``continue`` on that path, a model that only ever
    declared done made BUDGET unreachable and the run spent to ``max_iters`` --
    a 20x overrun against the stated ceiling.
    """
    ws = Workspace(pathlib.Path(tempfile.mkdtemp()))
    always_reject = lambda candidate: VerifyResult(False, "still wrong")
    result = run(ScriptedModel([text_response("done", tokens=1000)] * 100),
                 ToolRegistry([]), "loop", verify=always_reject, workspace=ws,
                 max_iters=40, token_budget=2000)
    assert result.stop_reason is StopReason.BUDGET
    assert result.tokens_used <= 3000  # at most one iteration of overrun
