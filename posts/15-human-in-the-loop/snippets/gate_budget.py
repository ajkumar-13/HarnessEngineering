"""Post 15: the arithmetic of a gate budget, at tool granularity and at argument granularity.

Run from the series root:  uv run python posts/15-human-in-the-loop/snippets/gate_budget.py

Every input is illustrative (a run of 180 tool calls, 34 of them writes, 3 of those outside the working tree,
15 seconds of reading per request, six runs in one reviewer's session). The one cited number is the point after
which Anthropic's study measured the lower human block rate: 50 or more prior prompts in a session ("Auto mode is
now the default in Claude Code", Anthropic, 7 August 2026). Standard library only.
"""
CALLS, WRITES, OUTSIDE_TREE = 180, 34, 3     # illustrative run
SECONDS_PER_REQUEST, RUNS = 15, 6            # illustrative reviewer
DECAY_AFTER = 50                             # cited: "after 50 or more prior prompts"


def budget(per_run):
    total = per_run * RUNS
    late = max(0, total - DECAY_AFTER)
    return total, total * SECONDS_PER_REQUEST, late


for label, per_run in (("tool granularity", WRITES), ("argument granularity", OUTSIDE_TREE)):
    total, seconds, late = budget(per_run)
    print(f"{label}: {per_run} requests per run of {CALLS} calls, "
          f"{per_run * SECONDS_PER_REQUEST:,} s of reading per run")
    print(f"  {RUNS} runs: {total:,} requests, {seconds:,} s ({seconds / 60:.1f} min); "
          f"past prompt {DECAY_AFTER}: {late:,} ({late / total:.0%})")
print(f"requests saved per run: {WRITES - OUTSIDE_TREE}")
