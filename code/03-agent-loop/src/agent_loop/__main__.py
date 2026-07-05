"""Offline demo: `python -m agent_loop`.

Runs the loop with a scripted model (no API key needed) so you can watch one
reason -> act -> observe -> reason -> answer cycle and the transcript it builds.
Swap `ScriptedModel` for `AnthropicModel()` to drive it with a real model.
"""
from .loop import run
from .models import ScriptedModel, text_response, tool_response
from .tools import DEFAULT_TOOLS


def main() -> None:
    model = ScriptedModel([
        tool_response("calculator", {"expression": "(2 + 3) * 4"},
                      text="I'll compute that.", tokens=12),
        text_response("The result is 20.", tokens=6),
    ])
    result = run(model, DEFAULT_TOOLS, "What is (2 + 3) * 4?",
                 system="You are a careful assistant. Use tools when useful.")

    for msg in result.transcript:
        print(f"[{msg['role']:9}] {msg['content']}")
    print(f"\nanswer      : {result.answer}")
    print(f"stop_reason : {result.stop_reason.value}")
    print(f"iterations  : {result.iterations}")
    print(f"tokens_used : {result.tokens_used}")


if __name__ == "__main__":
    main()
