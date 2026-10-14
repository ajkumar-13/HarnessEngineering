"""A tool never raises into the loop: failures come back as observations, flagged with is_error.

call_tools() answers every tool call of one turn by id, in one list for one user message. A tool that raises
and a tool the model invented both become a tool_result with "is_error": true, so the run goes on and the
model reads the failure on its next turn. The companion's calculator catches its own errors and returns
"error: ..." as plain content, without the flag; the last line shows that string.

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/tool_errors.py
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "03-agent-loop" / "src"))
from agent_loop import Tool, ToolUse, calculator  # noqa: E402


def call_tools(tool_uses, tool_map):
    results = []
    for tu in tool_uses:
        tool = tool_map.get(tu.name)
        if tool is None:                      # the model invented a tool
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": f"error: unknown tool '{tu.name}'", "is_error": True})
            continue
        try:
            output = tool.run(tu.input)
        except Exception as e:                # the tool failed; the run has not
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": f"error: {e}", "is_error": True})
            continue
        results.append({"type": "tool_result", "tool_use_id": tu.id, "content": output})
    return results


def _read_file(args):
    return Path(args["path"]).read_text(encoding="utf-8")


read_file = Tool("read_file", "Read a text file.", _read_file)

if __name__ == "__main__":
    turn = [ToolUse("tu_1", "calculator", {"expression": "(2 + 3) * 4"}),
            ToolUse("tu_2", "read_file", {"path": "no/such/file.txt"}),
            ToolUse("tu_3", "search", {"query": "agent loop"})]
    results = call_tools(turn, {t.name: t for t in (calculator, read_file)})
    for r in results:
        r = dict(r, content=r["content"].replace("\\\\", "/").replace("\\", "/"))  # one path style on every OS
        print(json.dumps(r))
    print(f"one user message, {len(results)} results, ids {[r['tool_use_id'] for r in results]}")
    print(f"companion calculator on 1 / 0: {calculator.run({'expression': '1 / 0'})!r}")
