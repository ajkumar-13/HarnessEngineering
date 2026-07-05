"""Offline tests for the agent loop — every stop condition, no API key needed.

The safety surface here is the set of exits: each test forces exactly one of the
four stop conditions and asserts the loop takes it.
"""
from agent_loop.loop import StopReason, run
from agent_loop.models import ScriptedModel, text_response, tool_response
from agent_loop.tools import DEFAULT_TOOLS, calculator


def test_stop1_completes_on_final_answer():
    model = ScriptedModel([text_response("hello", tokens=5)])
    res = run(model, DEFAULT_TOOLS, "say hi")
    assert res.stop_reason is StopReason.COMPLETED
    assert res.answer == "hello"
    assert res.iterations == 1


def test_tool_result_feeds_back_then_completes():
    model = ScriptedModel([
        tool_response("calculator", {"expression": "2 + 3 * 4"}, tokens=10),
        text_response("the answer is 14", tokens=8),
    ])
    res = run(model, DEFAULT_TOOLS, "compute 2 + 3 * 4")
    assert res.stop_reason is StopReason.COMPLETED
    assert res.answer == "the answer is 14"
    assert res.iterations == 2
    # the tool's real output was fed back into the transcript as a tool_result
    tool_results = [b for m in res.transcript if isinstance(m["content"], list)
                    for b in m["content"] if b.get("type") == "tool_result"]
    assert tool_results and tool_results[0]["content"] == "14"


def test_stop2_max_iters_backstop():
    # a model that always calls a tool (with distinct args) never finishes
    script = [tool_response("echo", {"text": str(i)}, id=f"t{i}", tokens=1)
              for i in range(100)]
    res = run(ScriptedModel(script), DEFAULT_TOOLS, "run forever", max_iters=5)
    assert res.stop_reason is StopReason.MAX_ITERS
    assert res.iterations == 5


def test_stop3_budget():
    script = [tool_response("echo", {"text": str(i)}, id=f"t{i}", tokens=50)
              for i in range(100)]
    res = run(ScriptedModel(script), DEFAULT_TOOLS, "spend it",
              max_iters=100, token_budget=120)
    assert res.stop_reason is StopReason.BUDGET
    assert res.tokens_used >= 120


def test_stop4_no_progress():
    # the identical tool call every turn -> thrashing
    script = [tool_response("echo", {"text": "same"}, id="t", tokens=1)
              for _ in range(20)]
    res = run(ScriptedModel(script), DEFAULT_TOOLS, "repeat",
              max_iters=20, no_progress_window=3)
    assert res.stop_reason is StopReason.NO_PROGRESS
    assert res.iterations == 3


def test_calculator_is_sandboxed():
    assert calculator.run({"expression": "2 + 3 * 4"}) == "14"
    # anything that is not arithmetic is refused, not executed
    assert "error" in calculator.run({"expression": "__import__('os').getcwd()"})


def test_unknown_tool_is_reported_not_raised():
    model = ScriptedModel([
        tool_response("does_not_exist", {}, tokens=1),
        text_response("done", tokens=1),
    ])
    res = run(model, DEFAULT_TOOLS, "call a missing tool")
    assert res.stop_reason is StopReason.COMPLETED
    tool_results = [b for m in res.transcript if isinstance(m["content"], list)
                    for b in m["content"] if b.get("type") == "tool_result"]
    assert "unknown tool" in tool_results[0]["content"]
