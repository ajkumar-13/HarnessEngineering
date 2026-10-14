"""Post 09, sections 3 and 4: the two rungs that act on observations, offload and clear.

Run from the series root:  uv run python posts/09-context-management-loop/snippets/offload.py

offload_if_big() is the offloader of section 3: a large tool output goes to a scratch directory and the
window gets a pointer with the head and the tail. clear_spent() is the clear rung of section 4: tool
results already acted on become one-line stubs, except the most recent few and those of tools whose
results cannot be cheaply re-obtained. The demonstration runs both over the generated transcript of
transcript.py and prints tokens before and after each, and how much of the next request is still a
byte-identical prefix (what a prompt cache can reuse). The scratch directory is temporary.
"""
import re
import tempfile
from pathlib import Path

from transcript import ENC, request, result_name, shared_prefix, tokens, transcript

SAFE = re.compile(r"[^A-Za-z0-9._-]")


def offload_if_big(output, scratch, name, *, limit=4000):
    """A large tool output goes to disk; the window gets a pointer instead."""
    if len(output) <= limit:
        return output
    root = Path(scratch).resolve()
    path = (root / SAFE.sub("_", name)).resolve()
    if root not in path.parents:          # a model-supplied name must not escape
        raise ValueError("offload path escapes the scratch directory")
    root.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    lines = output.splitlines()
    return (f"[offloaded {len(lines)} lines to {path.name}; read it, or grep it "
            f"for the pattern you want]\nfirst 15 lines:\n"
            + "\n".join(lines[:15])
            + "\nlast 15 lines:\n" + "\n".join(lines[-15:]))


def clear_spent(messages, *, keep=3, exclude=("query_metrics", "create_ticket")):
    """Stub spent tool results, oldest first; keep the newest `keep` and every excluded tool's."""
    spots = [i for i, m in enumerate(messages) if isinstance(m["content"], list)
             and any(b.get("type") == "tool_result" for b in m["content"])]
    out, freed = list(messages), 0
    for i in spots[:-keep] if keep else spots:
        blocks = []
        for b in messages[i]["content"]:
            name = result_name(messages, b.get("tool_use_id"))
            text = b.get("content", "")
            if b.get("type") != "tool_result" or name in exclude or text.startswith("[cleared"):
                blocks.append(b)
                continue
            stub = f"[cleared: {name}, {len(text.splitlines())} lines; re-run the call if needed]"
            blocks.append({**b, "content": stub})
        new = {**messages[i], "content": blocks}
        if tokens(new) >= tokens(messages[i]):   # a stub longer than the result frees nothing
            continue
        freed += tokens(messages[i]) - tokens(new)
        out[i] = new
    return out, freed


def cached(old, new):
    """The byte-identical prefix the next request shares with the one before, the most a cache can return, as text."""
    return f"{shared_prefix(old, new):,} of {request(new):,} tokens ({shared_prefix(old, new) / request(new):.0%})"


if __name__ == "__main__":
    msgs = transcript()
    log = msgs[18]["content"][0]["content"]            # turn 9: the tests fail with a 2,000-line build log
    with tempfile.TemporaryDirectory() as scratch:
        pointer = offload_if_big(log, scratch, "../../turn 9.log")
        written = sorted(p.name for p in Path(scratch).iterdir())
    print(f"offload: a build log of {len(log.splitlines()):,} lines, {tokens(log):,} tokens, "
          f"becomes a pointer of {tokens(pointer):,} tokens")
    print(f"  4,000 characters of this log are {len(ENC.encode(log[:4000])):,} tokens")
    print(f"  the model-supplied name '../../turn 9.log' is written inside the scratch directory as {written[0]}")
    swapped = {**msgs[18], "content": [{**msgs[18]["content"][0], "content": pointer}]}
    print(f"  at the tool boundary, the next call sends {request(msgs[:18] + [swapped]):,} tokens, not "
          f"{request(msgs[:19]):,}, and shares {cached(msgs[:17], msgs[:18] + [swapped])} with the call before")
    later = msgs[:18] + [swapped] + msgs[19:41]
    print(f"  swapped in ten turns later instead, that call shares {cached(msgs[:39], later)} with the call before")
    upto = msgs[:81]                                   # the run as the call after turn 40 would send it
    cleared, freed = clear_spent(upto)
    first = next(i for i, (a, b) in enumerate(zip(upto, cleared)) if a != b)
    print("clear, after turn 40: keep the 3 newest results and every query_metrics and create_ticket result")
    print(f"  request: {request(upto):,} -> {request(cleared):,} tokens ({freed:,} freed); "
          f"first rewritten message: {first} of {len(upto)}")
    print(f"  the call after it shares {cached(msgs[:79], cleared)} with the call before; "
          f"without the clear, {cached(msgs[:79], upto)}")
