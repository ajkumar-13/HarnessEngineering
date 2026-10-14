"""Post 09: the whole ladder on one run, managed against unmanaged (the Lab/gate of the post).

Run from the series root:  uv run python posts/09-context-management-loop/snippets/ladder.py

The same generated transcript (transcript.py) is sent twice, call by call. Unmanaged, every tool result
is appended as it comes. Managed, the policy of section 5 runs before each call: every tool output is
offloaded at the tool boundary when it is over 4,000 characters (offload.py); at the soft trigger, 80
per cent of the illustrative window, spent results are cleared if that frees at least 10,000 tokens
(the clear_at_least idea); at the hard trigger, 95 per cent, the head is compacted (compact.py). For each
rung that fires it prints the tokens before and after, and how much of the rewritten request that call can
still read from the prompt cache. The window, the triggers and every size are illustrative.
"""
import tempfile

from compact import compact, summarise
from offload import clear_spent, offload_if_big
from transcript import TURNS, WINDOW, request, shared_prefix, transcript

SOFT, HARD, CLEAR_AT_LEAST = int(0.80 * WINDOW), int(0.95 * WINDOW), 10_000


def run(managed, scratch):
    """Input tokens of every call, and the rungs that fired: (call, rung, before, after, cached next)."""
    raw = transcript()
    msgs, sizes, events, prev = raw[:1], [], [], None
    for k in range(1, TURNS + 1):
        a, u = raw[2 * k - 1], raw[2 * k]
        if managed:
            b = u["content"][0]
            text = offload_if_big(b["content"], scratch, f"turn-{k}.txt")
            if text is not b["content"]:
                u = {**u, "content": [{**b, "content": text}]}
                events.append((k + 1, "offload", None, None, None))
        msgs = msgs + [a, u]
        before = request(msgs)
        if managed and before >= HARD:
            msgs = compact(msgs, summarise)
            events.append((k + 1, "compact", before, request(msgs), shared_prefix(prev, msgs)))
        elif managed and before >= SOFT:
            cleared, freed = clear_spent(msgs)
            if freed >= CLEAR_AT_LEAST:
                msgs = cleared
                events.append((k + 1, "clear", before, request(msgs), shared_prefix(prev, msgs)))
        sizes.append(request(msgs))
        prev = msgs
    return sizes, events


def table():
    with tempfile.TemporaryDirectory() as scratch:
        plain, _ = run(False, scratch)
        managed, events = run(True, scratch)
    return plain, managed, events


if __name__ == "__main__":
    plain, managed, events = table()
    over = next(i for i, n in enumerate(plain, 2) if n > WINDOW)
    print(f"window {WINDOW:,} (illustrative); soft trigger {SOFT:,}; hard trigger {HARD:,}; calls 2 to {TURNS + 1}")
    print(f"unmanaged: call {over} would send {plain[over - 2]:,} tokens, past the window")
    offloads = [c for c, rung, *_ in events if rung == "offload"]
    print(f"managed: build logs offloaded at the tool boundary before calls {', '.join(map(str, offloads))}")
    print("call  rung       before    after  shared with the call before")
    for call, rung, before, after, cached in events:
        if rung != "offload":
            print(f"{call:>4}  {rung:<8}{before:>9,}{after:>9,}  {cached:,} of {after:,} ({cached / after:.0%})")
    print(f"managed peak: {max(managed):,} tokens; last call: {managed[-1]:,}")
