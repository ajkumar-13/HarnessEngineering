"""Post 09: the generated transcript every other snippet of the post runs over.

Run from the series root:  uv run python posts/09-context-management-loop/snippets/transcript.py

One coding task, turn by turn, in the shape the Anthropic Messages API uses: an assistant message
carrying a tool_use block, then a user message carrying its tool_result. Everything is generated
here with a fixed seed, so every run prints the same numbers; no model is called and nothing touches
the network. The sizes are illustrative. Tokens are counted with tiktoken's cl100k_base encoding, an
OpenAI tokenizer standing in for the provider's own, one message at a time; a request is the tools,
then the system prompt, then the messages, in the order the provider renders them.
"""
import json
import random

import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")
WINDOW = 200_000                       # an illustrative window, in tokens
TURNS = 140
LOG_TURNS = (9, 30, 51, 72, 93, 114)           # the test run fails and prints a 2,000-line build log

SYSTEM = "\n".join(
    ["You are a coding agent working in one repository. Follow the rules below on every turn."]
    + [f"Rule {i}: {r}" for i, r in enumerate([
        "Read a file before you edit it, and edit only the lines the task needs.",
        "Run the test suite after every edit and report the result.",
        "Never edit a test to make it pass; fix the code under test.",
        "Query production metrics only through query_metrics; never guess a number.",
        "Open a ticket with create_ticket for anything outside the task.",
        "State each decision and its reason in one line beginning 'Decision:'.",
    ] * 4, 1)])
TOOLS = [
    {"name": "read_file", "description": "Read a file of the repository.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "grep", "description": "Search the repository for a pattern.",
     "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}},
    {"name": "edit_file", "description": "Replace a range of lines in a file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "start": {"type": "integer"},
                                                       "end": {"type": "integer"}, "text": {"type": "string"}},
                      "required": ["path", "start", "end", "text"]}},
    {"name": "run_tests", "description": "Run the test suite and return its output.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "query_metrics", "description": "Read a live production metric (timestamped, not repeatable).",
     "input_schema": {"type": "object", "properties": {"metric": {"type": "string"}}, "required": ["metric"]}},
    {"name": "create_ticket", "description": "Open a ticket in the tracker (a side effect).",
     "input_schema": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}},
]
GOAL = ("Fix the failing parser test in src/parser.py without changing the public API, and keep "
        "p95 parse latency under 40 ms in production.")
FILES = ["src/parser.py", "src/lexer.py", "src/ast.py", "src/errors.py", "src/cli.py"]
REASONS = ["the failing case recurses through it", "the last edit has to be checked",
           "latency must stay under budget", "the index error points there", "the fold must accept any arity"]


def source(rng, path, limit=3_900):
    """One page of a file read: the read tool returns at most about 4,000 characters per call."""
    out, size, i = [], 0, rng.randint(0, 300)
    while True:
        f = rng.choice(["parse", "lex", "emit", "check", "fold", "visit"])
        line = (f"    def {f}_{i}(self, node, depth={rng.randint(0, 9)}):  # {path}:{i + 1}" if i % 6 == 0 else
                f"        value = self.{f}(node.children[{rng.randint(0, 5)}], depth + {rng.randint(1, 3)})")
        if size + len(line) + 1 > limit:
            return "\n".join(out)
        out.append(line)
        size, i = size + len(line) + 1, i + 1


def patch(rng, n):
    """n lines of new code: what the model writes into an edit_file call (history, never a tool result)."""
    return "\n".join(f"        node = self.fold_{rng.randint(0, 99)}(node, depth=depth + {rng.randint(1, 3)})  "
                     f"# keeps arity {rng.randint(1, 6)}" for _ in range(n))


def build_log(rng, turn):
    """A failing CI run: 2,000 lines of compile and test chatter, the error at the end."""
    lines = [f"[{turn:02d}:{i // 60:02d}:{i % 60:02d}] compiling module_{rng.randint(100, 999)}.py ... ok "
             f"({rng.randint(3, 90)} ms)" for i in range(1_990)]
    lines += ["FAILED tests/test_parser.py::test_nested_brackets", "    assert parse('[[1]]') == [[1]]",
              "E   IndexError: list index out of range", "src/parser.py:212: in fold_210",
              "    value = self.fold(node.children[5], depth + 1)", "", "1 failed, 311 passed in 42.81s",
              "error: test suite failed", "exit status 1", "build 7 failed"]
    return "\n".join(lines)


def metric(rng, turn):
    """A timestamped production snapshot: a short table no later call can reproduce."""
    rows = [f"2026-07-22T{10 + turn // 60:02d}:{turn % 60:02d}:{s:02d}Z p95_parse_ms={rng.uniform(30, 48):.1f} "
            f"p99_parse_ms={rng.uniform(50, 90):.1f} rps={rng.randint(800, 1400)} host=api-{h}"
            for s in range(0, 60, 5) for h in (1, 2, 3)]
    return "\n".join(rows)


def turn_pair(rng, k):
    """Turn k: the assistant's reasoning and tool call, then the tool's result."""
    path = FILES[k % len(FILES)]
    if k in LOG_TURNS:
        name, args, result = "run_tests", {}, build_log(rng, k)
    elif k % 4 == 0:
        name, args, result = "query_metrics", {"metric": "p95_parse_ms"}, metric(rng, k)
    elif k == 31:
        name, args, result = "create_ticket", {"title": "lexer allocates per token"}, "created ENG-4471"
    elif k % 4 == 1:
        name, args, result = "edit_file", {"path": path, "start": 200 + k, "end": 214 + k,
                                           "text": patch(rng, rng.randint(110, 160))}, \
            f"edited {path}: lines {200 + k} to {214 + k} replaced"
    elif k % 4 == 2:
        name, args, result = "grep", {"pattern": f"fold_{k}"}, "\n".join(
            f"{rng.choice(FILES)}:{rng.randint(1, 400)}: value = self.fold_{k}(node)" for _ in range(24))
    else:
        name, args, result = "read_file", {"path": path}, source(rng, path)
    thought = (f"Turn {k}. The last result narrows the fault to {path}. "
               + " ".join(rng.choice(["The nested case recurses one level too deep.",
                                      "The index assumes six children.", "Latency is within budget.",
                                      "The lexer is not the cause.", "The fold must accept any arity."])
                          for _ in range(rng.randint(12, 18)))
               + f" Decision: {' '.join(filter(None, [name, args.get('path') or args.get('metric')]))}"
                 f" now, because {rng.choice(REASONS)}.")
    tid = f"tu_{k:02d}"
    return ({"role": "assistant", "content": [{"type": "text", "text": thought},
                                              {"type": "tool_use", "id": tid, "name": name, "input": args}]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tid, "content": result}]})


def transcript(turns=TURNS, seed=9):
    """The goal, then one (assistant, user) pair per turn: the raw run, nothing managed."""
    rng = random.Random(seed)
    msgs = [{"role": "user", "content": GOAL}]
    for k in range(1, turns + 1):
        msgs.extend(turn_pair(rng, k))
    return msgs


_COUNTS = {}


def tokens(obj):
    """Tokens of one message (or the tools, or the system prompt), rendered as JSON text."""
    text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    if text not in _COUNTS:
        _COUNTS[text] = len(ENC.encode(text))
    return _COUNTS[text]


HEAD = tokens(TOOLS) + tokens(SYSTEM)      # what renders before the messages


def request(msgs):
    """Input tokens of one request: tools, system prompt, then every message."""
    return HEAD + sum(tokens(m) for m in msgs)


def shared_prefix(old, new):
    """Tokens at the front of the next request that are byte-identical to this one: the cacheable part."""
    n = HEAD
    for a, b in zip(old, new):
        if a != b:
            break
        n += tokens(a)
    return n


def result_name(msgs, tool_use_id):
    """The tool name behind a tool_result, read off the tool_use that asked for it."""
    for m in msgs:
        for b in m["content"] if isinstance(m["content"], list) else []:
            if b.get("type") == "tool_use" and b["id"] == tool_use_id:
                return b["name"]
    return None


if __name__ == "__main__":
    msgs = transcript()
    share = {}
    for m in msgs:
        for b in m["content"] if isinstance(m["content"], list) else []:
            if b.get("type") == "tool_result":
                name = result_name(msgs, b["tool_use_id"])
                share[name] = share.get(name, 0) + tokens(m)
    total = request(msgs)
    print(f"{TURNS} turns, {len(msgs)} messages; tools and system prompt: {HEAD:,} tokens")
    print(f"whole run as one request: {total:,} tokens against an illustrative window of {WINDOW:,}")
    for name, n in sorted(share.items(), key=lambda kv: -kv[1]):
        print(f"  {name:<14}{n:>9,} tokens of tool results")
    print(f"tool results: {sum(share.values()) / total:.0%} of the request")
