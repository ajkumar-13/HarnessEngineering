"""Post 21, sections 4 and 8: what a trace's token column says, and how big a run's bodies are.

Run from the series root:  uv run python posts/21-observability-traces/snippets/token_series.py

The run is the series' illustrative twelve-iteration run (post 23): call n sends 6,000 + 3,100 (n - 1) input
tokens. The second series is the same run with one un-offloaded tool result: call 6 sends 66,000 tokens
instead of 21,500, and the excess is re-sent on every later call. The body size uses four characters to a
token, a rule of thumb for English text, so it is illustrative. Standard library only.
"""
FIRST, GROWTH, N = 6_000, 3_100, 12
CHARS_PER_TOKEN = 4                    # illustrative rule of thumb


def healthy(n):
    return FIRST + GROWTH * (n - 1)


def main():
    calls = [healthy(n) for n in range(1, N + 1)]
    total, peak = sum(calls), max(calls)
    print(f"healthy run: {N} calls from {calls[0]:,} to {peak:,} input tokens, {GROWTH:,} more each call")
    print(f"billed input is the sum, {total:,} tokens: {total / peak:.1f} times the largest single window")
    step = 66_000
    excess = step - healthy(6)
    bloated = calls[:5] + [c + excess for c in calls[5:]]
    print(f"call 5 sends {calls[4]:,}, call 6 sends {step:,}: a jump of {step - calls[4]:,} against an increment "
          f"of {GROWTH:,}")
    print(f"the {excess:,}-token excess is re-sent on calls 6 to {N} ({N - 5} calls): "
          f"{sum(bloated) - total:,} more input tokens, against the {total:,} the whole run was planned to send")
    print(f"distinct message content: the last window, {peak:,} tokens, at {CHARS_PER_TOKEN} characters a token "
          f"is about {peak * CHARS_PER_TOKEN:,} bytes")


if __name__ == "__main__":
    main()
