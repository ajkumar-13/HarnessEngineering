"""The coordination tax of orchestration, priced with Anthropic's cited token multipliers.

Run from the series root:  uv run python posts/02-anatomy-of-a-harness/snippets/coordination_tax.py

The multipliers are cited: agents use about 4x the tokens of a chat interaction and multi-agent
systems about 15x (Anthropic, "How we built our multi-agent research system", 13 June 2025).
The 40,000-token chat is illustrative. Standard library only; no network.
"""

CHAT_TOKENS = 40_000  # illustrative: the chat form of one task

# shape, multiplier over one chat (cited, Anthropic 2025)
SHAPES = [
    ("one chat turn", 1),
    ("single agent in a loop", 4),
    ("orchestrator with sub-agents", 15),
]


def rows(chat_tokens=CHAT_TOKENS):
    """(shape, multiplier, tokens, tokens above the chat) for each shape."""
    return [(shape, m, m * chat_tokens, (m - 1) * chat_tokens) for shape, m in SHAPES]


def coordination_tax(chat_tokens=CHAT_TOKENS):
    """Tokens the orchestrator spends above the single agent, and that gap in chats."""
    single = 4 * chat_tokens
    multi = 15 * chat_tokens
    return multi - single, (multi - single) / chat_tokens


if __name__ == "__main__":
    print(f"{'shape':<30}{'multiplier':>11}{'tokens':>10}{'above chat':>12}")
    for shape, m, tokens, above in rows():
        print(f"{shape:<30}{str(m) + 'x':>11}{tokens:>10,}{above:>12,}")
    tax, chats = coordination_tax()
    print(f"coordination tax, orchestrator over single agent: {tax:,} tokens, {chats:.0f} chats")
