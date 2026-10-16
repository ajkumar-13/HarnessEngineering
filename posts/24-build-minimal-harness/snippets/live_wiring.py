"""Post 24: the live wiring of Build #1, and the request it would send, recorded offline.

Run from the series root:  uv run python posts/24-build-minimal-harness/snippets/live_wiring.py

Builds the live configuration from code/24-minimal-harness unchanged: AnthropicModel, the real subprocess_runner
behind the deny-listed bash tool, the write_file tool and the palindrome gate. It never goes live. Instead of the
Anthropic client it hands AnthropicModel a recorder (through the adapter's own _client field), makes one respond()
call, and prints the keyword arguments the adapter would pass to messages.create. go_live() is the one call that
would spend money; nothing here calls it. To call it, install the companion's `anthropic` extra and set
ANTHROPIC_API_KEY.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "24-minimal-harness" / "src"))
from minimal_harness import (AnthropicModel, ToolRegistry, Workspace, run,  # noqa: E402
                             make_bash_tool, make_write_file_tool,
                             subprocess_runner, python_function_tests)

TASK = "Write is_palindrome(s) in solution.py and make it correct."

workspace = Workspace()
registry = ToolRegistry([
    make_write_file_tool(workspace),
    make_bash_tool(runner=subprocess_runner, timeout=10.0),   # a real shell
])
verify = python_function_tests("solution.py", "is_palindrome",
                               [(("racecar",), True), (("abc",), False), (("",), True)])


def go_live():
    return run(AnthropicModel(), registry, TASK, verify=verify,
               workspace=workspace, max_iters=12, token_budget=200_000)


class Recorder:
    """Stands in for anthropic.Anthropic(): records the request, sends nothing."""

    def __init__(self):
        self.requests = []
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.requests.append(kwargs)
        block = SimpleNamespace(model_dump=lambda: {"type": "text", "text": "(recorded, not sent)"})
        return SimpleNamespace(content=[block], usage=SimpleNamespace(input_tokens=0, output_tokens=0))


def main():
    recorder = Recorder()
    model = AnthropicModel(_client=recorder)
    model.respond(None, [{"role": "user", "content": TASK}], registry.specs())
    request = recorder.requests[0]
    print(f"model: {request['model']}")
    print(f"max_tokens: {request['max_tokens']}")
    print(f"tools: {[t['name'] for t in request['tools']]}")
    print(f"messages: {len(request['messages'])}, first from {request['messages'][0]['role']}")
    print(f"keys sent: {sorted(request)}")
    return request


if __name__ == "__main__":
    main()
