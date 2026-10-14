"""Post 06, section 6: what the run_tests definition costs per call, and what its schema refuses.

Run from the series root:  uv run python posts/06-tools-bash-code/snippets/run_tests_schema.py

The definition is the post's run_tests tool. Its size is counted with tiktoken's o200k_base encoding, an
estimate: each provider tokenises with its own vocabulary and wraps tool definitions in its own text. The run
(twelve tools of this size, forty turns) is illustrative. The rate is the Claude Sonnet 4.6 input rate, 3
dollars per million tokens, and a cache read is 0.1 times that (Anthropic pricing and prompt caching pages,
consulted October 2026). The two calls are checked with the companion's validate(), imported unchanged from
code/06-tools-and-bash/src/tools/schema.py.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "06-tools-and-bash" / "src"))
from tools import validate  # noqa: E402

RUN_TESTS = {
    "name": "run_tests",
    "description": "Run the suite and return the failures. Use after any code edit. "
                   "Do NOT use to read a file: use bash for that.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File or directory to test."},
            "scope": {"type": "string", "enum": ["unit", "integration", "all"]},
        },
        "required": ["path"],
        "additionalProperties": False,
    },
}
TOOLS, TURNS = 12, 40            # illustrative: a tool list of twelve such tools, a forty-turn run
RATE = 3.00                      # dollars per million input tokens, Claude Sonnet 4.6
CACHE_READ = 0.1                 # cache reads as a multiple of the input rate

one = len(tiktoken.get_encoding("o200k_base").encode(json.dumps(RUN_TESTS)))
block = one * TOOLS
run = block * TURNS
print(f"run_tests definition: {one} tokens (o200k_base estimate)")
print(f"{TOOLS} tools of that size: {block:,} tokens of tool block per call")
print(f"re-read on {TURNS} turns: {run:,} tokens per run")
print(f"at ${RATE:.2f}/M uncached: ${run * RATE / 1e6:.4f}; as cache reads: ${run * RATE * CACHE_READ / 1e6:.4f}")
for call in ({"path": "tests/", "scope": "unit"}, {"scope": "everything"}):
    problems = validate(call, RUN_TESTS["input_schema"])
    print(f"{json.dumps(call)} -> {'; '.join(problems) if problems else 'valid'}")
