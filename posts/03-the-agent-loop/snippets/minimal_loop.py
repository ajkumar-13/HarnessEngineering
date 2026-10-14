"""The minimal control loop of post 03, run offline against the companion's scripted model.

run() below is the companion's run() (code/03-agent-loop/src/agent_loop/loop.py) with exits (3) and (4)
removed for legibility. It drives the companion's ScriptedModel and tools through the companion's demo task,
then prints the answer and the one turn that went over the wire: the assistant message the model returned and
the user message the harness sent back.

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/minimal_loop.py
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "03-agent-loop" / "src"))
from agent_loop import DEFAULT_TOOLS, ScriptedModel, text_response, tool_response  # noqa: E402


def run(model, tools, task, *, system=None, max_iters=12):
    tool_map = {t.name: t for t in tools}
    messages = [{"role": "user", "content": task}]
    for step in range(1, max_iters + 1):
        resp = model.respond(system, messages, tools)          # REASON
        messages.append({"role": "assistant", "content": resp.content_blocks})
        if resp.is_final():                                    # exit (1): a final answer
            return resp.text, messages
        results = []
        for tu in resp.tool_uses:                              # ACT
            tool = tool_map.get(tu.name)
            output = tool.run(tu.input) if tool else f"error: unknown tool '{tu.name}'"
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": output})
        messages.append({"role": "user", "content": results})  # OBSERVE
    return "stopped: hit max_iters", messages                  # exit (2): the backstop


def demo_model():
    """The companion's demo script (agent_loop/__main__.py): one calculator call, then an answer."""
    return ScriptedModel([
        tool_response("calculator", {"expression": "(2 + 3) * 4"},
                      text="I'll compute that.", tokens=12),
        text_response("The result is 20.", tokens=6),
    ])


if __name__ == "__main__":
    answer, messages = run(demo_model(), DEFAULT_TOOLS, "What is (2 + 3) * 4?")
    print(f"answer: {answer}  ({len(messages)} messages, {sum(m['role'] == 'assistant' for m in messages)} model calls)")
    print()
    for msg in messages[1:3]:
        print(json.dumps(msg))
