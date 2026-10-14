"""Exit (1) read from stop_reason, against exit (1) read from a missing tool call.

The seven stop_reason values are those of Anthropic's "Stop reasons and fallback" page (Messages API, 2026). For each,
a response is built the way the API returns it (a tool_use turn carries a tool call; the others carry none),
and two checks are asked whether the loop may stop with an answer: the naive one, "no tool call", and
is_final(), "a terminal stop_reason and no tool call".

Run from the series root:  uv run python posts/03-the-agent-loop/snippets/stop_reasons.py
"""
from dataclasses import dataclass, field

TERMINAL = {"end_turn", "stop_sequence"}


def is_final(resp) -> bool:
    return resp.stop_reason in TERMINAL and not resp.tool_uses


def naive_is_final(resp) -> bool:
    return not resp.tool_uses


@dataclass
class Response:
    stop_reason: str
    tool_uses: list = field(default_factory=list)


STOP_REASONS = ["end_turn", "tool_use", "max_tokens", "stop_sequence", "refusal", "pause_turn",
                "model_context_window_exceeded"]

if __name__ == "__main__":
    print(f"{'stop_reason':31}{'tool call':>10}{'naive: answer?':>16}{'is_final():':>13}")
    wrong = []
    for reason in STOP_REASONS:
        resp = Response(reason, ["calculator"] if reason == "tool_use" else [])
        naive, right = naive_is_final(resp), is_final(resp)
        print(f"{reason:31}{'yes' if resp.tool_uses else 'no':>10}{'yes' if naive else 'no':>16}"
              f"{'yes' if right else 'no':>13}")
        if naive != right:
            wrong.append(reason)
    print(f"the naive check takes {len(wrong)} non-answers as answers: {', '.join(wrong)}")
