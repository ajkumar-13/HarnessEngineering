"""Post 10, section 2: what carrying a memory file costs in money, at a named rate.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/snippets/line_cost.py

Rates: Claude Opus 5 on Anthropic's "Pricing" page, consulted 14 October 2026: base input $5 per
million tokens, a 5-minute cache write at 1.25 times that ($6.25), a cache read at 0.1 times ($0.50).
The file's size (40 lines at about 20 tokens a line) and the call count (100 a day for a year)
are illustrative. The file rides in the prefix of every model call, so it is priced per call. Standard library only.
"""
LINES, TOKENS_PER_LINE = 40, 20                 # illustrative
INPUT, WRITE, READ = 5.00, 6.25, 0.50           # dollars per million tokens, Claude Opus 5
CALLS = 100 * 365                               # illustrative: 100 model calls a day for a year

tokens = LINES * TOKENS_PER_LINE
per_session = {"uncached input": INPUT, "cache write": WRITE, "cache read": READ}
print(f"memory file: {LINES} lines x {TOKENS_PER_LINE} tokens = {tokens} tokens")
for label, rate in per_session.items():
    print(f"  one call, {label:<14} {tokens} x ${rate:.2f} / 1e6 = ${tokens * rate / 1e6:.4f}")
print(f"a year at {CALLS} calls:")
print(f"  every call a cache read:  ${CALLS * tokens * READ / 1e6:,.2f}")
print(f"  every call uncached:      ${CALLS * tokens * INPUT / 1e6:,.2f}")
