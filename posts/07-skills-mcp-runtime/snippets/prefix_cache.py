"""Append against swap: how much of each request a prefix cache can reuse, in token counts.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/snippets/prefix_cache.py
The six-turn run of skill_registry.py is rendered three ways (eager, swap, append) as the provider renders a
request: tools, then system, then messages. Tokens are counted with tiktoken's o200k_base encoding, a stand-in
(Claude's tokenizer is not public), so every count is illustrative. A request reuses the cache only when the
previous request is an exact prefix of it; otherwise nothing is reused, because a change to the tool
definitions invalidates the entire cache (Anthropic, "Tool use with prompt caching"). The run is small and the
snippet ignores the provider's minimum cacheable length; the comparison, not the size, is the point.
"""
import json

import tiktoken

from skill_registry import BASE_TOOLS, SKILLS, TASKS, SkillRegistry

enc = tiktoken.get_encoding("o200k_base")
READ, WRITE = 0.1, 1.25  # cache read and five-minute cache write, as multiples of the base input rate (Anthropic pricing)
REPLY = "Done. {task} The result is in the observation above."  # an illustrative one-line model reply

SYSTEM = ("You are a careful operations agent working in a sandboxed workspace. Use the tools to act; report "
          "what you did in one short paragraph.\n\nSkills you can call on (loaded when a task needs them):\n")


def toks(text: str) -> list[int]:
    return enc.encode(text)


def request(tools: list, catalogue: list[str], messages: list[str]) -> list[int]:
    """Tokens of one request, rendered block by block: tools, then system, then messages."""
    out = toks(json.dumps(tools))
    out += toks(SYSTEM + "\n".join(f"- {line}" for line in catalogue))
    for m in messages:
        out += toks(m)
    return out


def run(strategy: str) -> list[tuple[int, int]]:
    """(request tokens, tokens reused from the cache) for each turn of the run."""
    reg = SkillRegistry(BASE_TOOLS, SKILLS)
    every = BASE_TOOLS + [t for s in SKILLS for t in s.tools]
    history, prev, rows = [], [], []
    for task in TASKS:
        if strategy == "eager":
            tools = every
            history.append(task)
        elif strategy == "swap":
            tools = reg.tools_for(task)
            history.append(task)
        else:                                   # append: the tools block never changes
            tools = BASE_TOOLS
            history.append(task)
            new = reg.disclose(task)
            if new:
                history.append(json.dumps({"tool_reference": new}))
        req = request(tools, reg.catalogue(), history)
        reused = len(prev) if req[:len(prev)] == prev else 0
        rows.append((len(req), reused))
        history.append(REPLY.format(task=task))
        prev = req
    return rows


def billed(rows) -> float:
    """Input token-equivalents: reused tokens at the read rate, every other token written at the write rate."""
    return sum(reused * READ + (n - reused) * WRITE for n, reused in rows)


if __name__ == "__main__":
    reg = SkillRegistry(BASE_TOOLS, SKILLS)
    schemas = [t for s in SKILLS for t in s.tools]
    per_schema = sum(len(toks(json.dumps(t))) for t in schemas) / len(schemas)
    per_line = sum(len(toks(f"- {line}\n")) for line in reg.catalogue()) / len(SKILLS)
    print(f"skill schemas: {len(schemas)}, {per_schema:.0f} tokens each on average; "
          f"catalogue lines: {len(SKILLS)}, {per_line:.0f} tokens each")
    print()
    results = {s: run(s) for s in ("eager", "swap", "append")}
    print("turn   eager: sent  reused    swap: sent  reused    append: sent  reused")
    for i in range(len(TASKS)):
        cells = "    ".join(f"{results[s][i][0]:>11,}  {results[s][i][1]:>6,}" for s in results)
        print(f"{i + 1:>4}  {cells}")
    print()
    for s, rows in results.items():
        sent = sum(n for n, _ in rows)
        reused = sum(r for _, r in rows)
        eq = billed(rows)
        print(f"{s:<7} sent {sent:>6,}  reused {reused:>6,} ({reused / sent:.0%})  "
              f"billed as {eq:>6,.0f} token-equivalents")
    print(f"swap / append billed: {billed(results['swap']) / billed(results['append']):.2f} times")
