"""Post 09, section 5: the rolling compactor, and the cut that keeps the request valid.

Run from the series root:  uv run python posts/09-context-management-loop/snippets/compact.py

compact() folds the head of the message list into one brief and keeps the last turns verbatim, cutting
only where no tool call is left open. summarise() is a deterministic stand-in for the model call a real
harness makes with the summarisation prompt of section 5: it keeps the named fields of that brief (the
goal verbatim, decisions with their reasons, files touched, the last check, the live readings that could
not be cleared, tickets opened, the next action) and drops everything else. The demonstration runs over
the generated transcript of transcript.py and prints the naive cut, the safe cut, tokens before and after,
and how much of the next request is still a byte-identical prefix.
"""
import re

from transcript import HEAD, TURNS, request, result_name, shared_prefix, transcript


def open_tool_uses(msgs):
    """Ids of tool_use blocks in msgs whose tool_result is not also in msgs."""
    used, answered = set(), set()
    for m in msgs:
        for b in m["content"] if isinstance(m["content"], list) else []:
            if b.get("type") == "tool_use":
                used.add(b["id"])
            elif b.get("type") == "tool_result":
                answered.add(b["tool_use_id"])
    return used - answered


def compact(messages, summarise, *, keep_last=6):
    """Fold the head into one brief, cutting only where no tool call is left open."""
    cut = max(1, len(messages) - keep_last)
    while cut > 1 and (open_tool_uses(messages[:cut])
                       or messages[cut]["role"] != "assistant"):
        cut -= 1
    head, tail = messages[:cut], messages[cut:]
    if len(head) < 2:
        return messages                       # nothing worth folding yet
    brief = {"role": "user", "content": [
        {"type": "text", "text": "[brief of earlier turns]\n" + summarise(head)}]}
    return [brief] + tail                     # user, then the assistant turn the tail starts with


def summarise(head):
    """A stand-in for the model's brief: the named fields of the section 5 contract, nothing else."""
    first = head[0]["content"] if isinstance(head[0]["content"], str) else head[0]["content"][0]["text"]
    old = dict(re.findall(r"^- (goal|files touched|last check|tickets): (.*)$", first, re.M))
    goal = old.get("goal", first)                   # a rolling brief carries the goal forward verbatim
    decisions = re.findall(r"^- decision: (.*)$", first, re.M)
    readings = re.findall(r"^- reading: (.*)$", first, re.M)
    files = [f for f in old.get("files touched", "none").split(", ") if f != "none"]
    tickets = [t for t in old.get("tickets", "none").split(", ") if t != "none"]
    checks = old.get("last check", "none run")
    for m in head[1:]:
        for b in m["content"] if isinstance(m["content"], list) else []:
            if b.get("type") == "text":
                decisions += re.findall(r"Decision: (.*?\.)(?=\s|$)", b["text"])
            elif b.get("type") == "tool_use" and b["name"] == "edit_file":
                files.append(b["input"]["path"])
            elif b.get("type") == "tool_result":
                name, text = result_name(head, b["tool_use_id"]), b["content"]
                if name == "run_tests":
                    checks = text.splitlines()[-1]
                elif name == "query_metrics":
                    p95 = [float(x) for x in re.findall(r"p95_parse_ms=([\d.]+)", text)]
                    at = re.search(r"T(\d\d:\d\d):", text).group(1)
                    readings.append(f"p95_parse_ms from {at}Z, max {max(p95)} ms over {len(p95)} samples")
                elif name == "create_ticket":
                    tickets.append(text)
    return "\n".join([f"- goal: {goal}"] + [f"- decision: {d}" for d in dict.fromkeys(decisions)][-6:]
                     + [f"- files touched: {', '.join(dict.fromkeys(files)) or 'none'}",
                        f"- last check: {checks}"] + [f"- reading: {r}" for r in readings]
                     + [f"- tickets: {', '.join(tickets) or 'none'}",
                        f"- next: continue from the last decision, {decisions[-1] if decisions else 'none yet'}"])


if __name__ == "__main__":
    msgs = transcript()[:2 * 40 + 1]                # the run as the model's 41st call would send it
    naive = msgs[-5:]
    orphans = sorted({b["tool_use_id"] for m in naive if isinstance(m["content"], list)
                      for b in m["content"] if b.get("type") == "tool_result"} - {
        b["id"] for m in naive if isinstance(m["content"], list) for b in m["content"]
        if b.get("type") == "tool_use"})
    print(f"naive cut, messages[-5:]: starts with a {naive[0]['role']} turn; orphaned tool_result: {orphans}")
    for keep_last in (5, 6):
        out = compact(msgs, summarise, keep_last=keep_last)
        print(f"compact(keep_last={keep_last}): {len(msgs)} -> {len(out)} messages; "
              f"the kept tail starts with an {out[1]['role']} turn; open tool calls: {sorted(open_tool_uses(out))}")
    out = compact(msgs, summarise)
    nxt = out + transcript()[81:83]
    print(f"request: {request(msgs):,} -> {request(out):,} tokens; the brief: {request(out[:1]) - HEAD:,} tokens")
    print(f"first call after it: {shared_prefix(msgs, out):,} of {request(out):,} tokens are a byte-identical prefix "
          f"({shared_prefix(msgs, out) / request(out):.0%}, tools and system prompt); the call after that: "
          f"{shared_prefix(out, nxt):,} of {request(nxt):,} ({shared_prefix(out, nxt) / request(nxt):.0%})")
    print(out[0]["content"][0]["text"])
