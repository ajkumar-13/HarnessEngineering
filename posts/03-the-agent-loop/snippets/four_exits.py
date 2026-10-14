"""Make the companion's scripted model trigger each of the four exits in turn, and read the stop reason.

Each run drives run() from code/03-agent-loop/src/agent_loop/loop.py, unchanged, with a ScriptedModel written to
reach one exit: an answer on the first turn; distinct tool calls forever under a cap of 5; 50 tokens a turn
under a budget of 120; and the identical call every turn under a no-progress window of 3.

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/four_exits.py
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "03-agent-loop" / "src"))
from agent_loop import DEFAULT_TOOLS, ScriptedModel, run, text_response, tool_response  # noqa: E402


def distinct(tokens):
    return [tool_response("echo", {"text": str(i)}, id=f"t{i}", tokens=tokens) for i in range(100)]


RUNS = [
    ("(1) answers on turn 1", [text_response("hello", tokens=5)], {}),
    ("(2) cap of 5, never answers", distinct(1), {"max_iters": 5}),
    ("(3) budget of 120, 50 a turn", distinct(50), {"max_iters": 100, "token_budget": 120}),
    ("(4) same call, window of 3",
     [tool_response("echo", {"text": "same"}, id="t", tokens=1) for _ in range(20)],
     {"max_iters": 20, "no_progress_window": 3}),
]


def results():
    return [(label, run(ScriptedModel(script), DEFAULT_TOOLS, "task", **kw)) for label, script, kw in RUNS]


if __name__ == "__main__":
    print(f"{'run':32}{'stop_reason':>13}{'iterations':>12}{'tokens_used':>13}")
    for label, r in results():
        print(f"{label:32}{r.stop_reason.value:>13}{r.iterations:>12}{r.tokens_used:>13}")
