"""Offline demo: ``python -m minimal_harness``.

Watch the whole harness run one task with a scripted model (no API key): the
agent writes a buggy function, the verification gate rejects it, the failure
report is fed back, the agent fixes it, and only then does the run stop as
verified. Swap ``ScriptedModel`` for ``AnthropicModel()`` to drive it live.
"""
from .harness import run
from .models import ScriptedModel, text_response, tool_response
from .tools import ToolRegistry, Workspace, make_write_file_tool
from .verify import python_function_tests

BUGGY = "def is_palindrome(s):\n    return s == s  # bug: always true\n"
FIXED = "def is_palindrome(s):\n    return s == s[::-1]\n"


def main() -> None:
    workspace = Workspace()
    registry = ToolRegistry([make_write_file_tool(workspace)])
    verify = python_function_tests(
        "solution.py", "is_palindrome",
        [(("racecar",), True), (("abc",), False), (("",), True)],
    )

    model = ScriptedModel([
        tool_response("write_file", {"path": "solution.py", "content": BUGGY},
                      text="Here is a first attempt.", tokens=20),
        text_response("Done — is_palindrome is implemented.", tokens=8),
        tool_response("write_file", {"path": "solution.py", "content": FIXED},
                      text="Fixing: compare against the reverse.", tokens=18),
        text_response("Fixed and it should pass now.", tokens=8),
    ])

    result = run(model, registry,
                 "Write is_palindrome(s) in solution.py and make it correct.",
                 system="You are a careful engineer. Verify before declaring done.",
                 verify=verify, workspace=workspace)

    for msg in result.transcript:
        print(f"[{msg['role']:9}] {msg['content']}")
    print(f"\nstop_reason : {result.stop_reason.value}")
    print(f"verified    : {result.verified}")
    print(f"iterations  : {result.iterations}")
    print(f"tokens_used : {result.tokens_used}")
    print(f"final file  :\n{workspace.files.get('solution.py', '(none)')}")


if __name__ == "__main__":
    main()
