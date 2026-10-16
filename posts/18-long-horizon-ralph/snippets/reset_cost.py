"""Post 18, section 4: what the frozen prefix costs over fifty resets, by cache tier and by the gap between reads.

Run from the series root:  uv run python posts/18-long-horizon-ralph/snippets/reset_cost.py

Rates are Claude Sonnet 4.6's on Anthropic's pricing and prompt-caching pages (consulted October 2026): base input
$3 per million tokens, a five-minute cache write 1.25x base, a one-hour write 2x, a cache read (hit or refresh)
0.1x. A cache entry lives five minutes (or an hour) from the START of the last request that wrote or read it,
and every read refreshes it. The prefix size, the iteration count and the calls per iteration are illustrative.

Two models of one loop. "Re-entry only" prices the first call of each iteration, the one that rebuilds the
context after a reset, and nothing else. "With calls inside" adds the calls an iteration makes after it; those
follow each other within seconds, so in every cached row they read the prefix warm. "Cold" means the re-entry
call starts more than the cache lifetime after the last read, for example because the driver's end-to-end gate
ran for about eight minutes between iterations.
"""
PREFIX, ITERS, CALLS = 12_000, 50, 20          # tokens; iterations; model calls per iteration (illustrative)
BASE = 3.00 / 1e6                              # dollars per input token, Claude Sonnet 4.6
WRITE_5M, WRITE_1H, READ = 1.25, 2.0, 0.1      # multipliers of base input

ROWS = (("no cache configured", "any gap", None, None),
        ("five-minute tier", "under 5 minutes", WRITE_5M, False),
        ("five-minute tier", "about 8 minutes", WRITE_5M, True),
        ("one-hour tier", "about 8 minutes", WRITE_1H, False))


def cost(write, cold, calls):
    """Dollars for the frozen prefix over ITERS iterations of `calls` calls each."""
    one = PREFIX * BASE
    if write is None:
        return ITERS * calls * one, None, None
    writes = ITERS if cold else 1              # cold: every re-entry writes the prefix again
    reads = ITERS * calls - writes
    return writes * write * one + reads * READ * one, writes, reads


def table():
    return [(tier, gap, cost(w, cold, 1), cost(w, cold, CALLS)) for tier, gap, w, cold in ROWS]


if __name__ == "__main__":
    one = PREFIX * BASE
    print(f"frozen prefix {PREFIX:,} tokens, {ITERS} iterations, ${BASE * 1e6:.2f} per million input tokens "
          f"(Claude Sonnet 4.6)")
    print(f"one full read ${one:.4f}; five-minute write ${one * WRITE_5M:.4f}; one-hour write ${one * WRITE_1H:.4f}; "
          f"cache read ${one * READ:.4f}")
    print(f"{'tier':<20}{'re-entry gap':<17}{'writes':>7}{'reads':>7}{'re-entry only':>15}"
          f"{'with ' + str(CALLS) + ' calls inside':>23}")
    rows = table()
    for tier, gap, (c1, w1, r1), (c20, _, _) in rows:
        print(f"{tier:<20}{gap:<17}{'n/a' if w1 is None else w1:>7}{'n/a' if r1 is None else r1:>7}"
              f"{'$' + format(c1, '.2f'):>15}{'$' + format(c20, '.2f'):>23}")
    none1, warm1, cold1, hour1 = (r[2][0] for r in rows)
    none20, warm20, cold20, hour20 = (r[3][0] for r in rows)
    print("(writes and reads count the re-entry calls)")
    print(f"re-entry only: a cold five-minute tier costs {cold1 / none1 - 1:.0%} more than no cache at all")
    print(f"with {CALLS} calls inside: cold re-entries cost {cold20 / warm20 - 1:.0%} more than warm ones, "
          f"and {1 - cold20 / none20:.0%} less than no cache")
    assert [round(r[2][0], 2) for r in rows] == [1.80, 0.22, 2.25, 0.25]
    assert round(cold1 / none1 - 1, 2) == 0.25
