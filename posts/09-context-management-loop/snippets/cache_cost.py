"""Post 09, section 7: what a compaction costs the prompt cache, deep against shallow.

Run from the series root:  uv run python posts/09-context-management-loop/snippets/cache_cost.py

Costs are in token-equivalents: tokens times their price relative to base input. The multipliers are
Claude Sonnet 4.6's on Anthropic's pricing and prompt-caching pages (consulted October 2026): base input
$3 per million tokens, output $15 (5x), a five-minute cache write $3.75 (1.25x), a cache read $0.30
(0.1x). The window sizes and the summary length are illustrative. The model of one compaction:

  without it, every later call reads the whole 160,000-token prefix from cache at 0.1x;
  with it, a summary call reads that same cached prefix warm at 0.1x and writes the summary as output,
  the first call after it writes the new, shorter prefix at 1.25x in place of the 0.1x read it would
  have made, and every later call reads the shorter prefix at 0.1x.
"""
import math

INPUT, OUTPUT, WRITE, READ = 3.00, 15.00, 3.75, 0.30            # $ per million tokens, Claude Sonnet 4.6
OUT_X, WRITE_X, READ_X = OUTPUT / INPUT, WRITE / INPUT, READ / INPUT
BEFORE, SUMMARY = 160_000, 5_000                                 # the session, and the brief a model writes


def event(after, warm=True):
    """Token-equivalents one compaction adds, BEFORE -> after, and what each later call saves."""
    head = BEFORE - after + SUMMARY                              # the tokens the summary replaces
    summary_call = (READ_X * BEFORE if warm else 1.0 * head) + OUT_X * SUMMARY
    write_premium = WRITE_X * after - READ_X * BEFORE            # first call: a write instead of a read
    return summary_call, write_premium, READ_X * (BEFORE - after)


def table():
    rows = {}
    for name, after in (("deep", 25_000), ("shallow", 130_000)):
        call, premium, saved = event(after)
        rows[name] = dict(after=after, read=READ_X * BEFORE, output=OUT_X * SUMMARY, premium=premium,
                          total=call + premium, saved=saved, calls=(call + premium) / saved)
    cold_call, premium, saved = event(25_000, warm=False)
    rows["deep, summary call cold"] = dict(total=cold_call + premium, saved=saved,
                                           calls=(cold_call + premium) / saved)
    return rows


def ten_steps():
    """The same 160,000 -> 25,000 in ten shallow compactions: the events alone, savings ignored."""
    step, total, size = (BEFORE - 25_000) / 10, 0.0, BEFORE
    for _ in range(10):
        after = size - step
        total += READ_X * size + OUT_X * SUMMARY + WRITE_X * after - READ_X * size
        size = after
    return total


if __name__ == "__main__":
    rows = table()
    print(f"multipliers: output {OUT_X:g}x, cache write {WRITE_X:g}x, cache read {READ_X:g}x of base input")
    print(f"{'line item':<52}{'deep':>10}{'shallow':>10}")
    print(f"{'session after the compaction (tokens)':<52}{rows['deep']['after']:>10,}{rows['shallow']['after']:>10,}")
    for key, label in (("read", "summary call: cached prefix read warm at 0.1x"),
                       ("output", f"summary call: {SUMMARY:,} output tokens at {OUT_X:g}x"),
                       ("premium", "first call after: write at 1.25x less read at 0.1x"),
                       ("total", "the compaction event"), ("saved", "saved on every later call")):
        print(f"{label:<52}{rows['deep'][key]:>10,.0f}{rows['shallow'][key]:>10,.0f}")
    print(f"{'calls to break even':<52}{rows['deep']['calls']:>10.1f}{rows['shallow']['calls']:>10.1f}")
    cold = rows["deep, summary call cold"]
    print(f"deep, summary call sent cold at 1x: event {cold['total']:,.0f}, break even after {cold['calls']:.1f} calls")
    print(f"deep event in dollars: ${rows['deep']['total'] * INPUT / 1e6:.2f}; "
          f"saved per later call: ${rows['deep']['saved'] * INPUT / 1e6:.4f}")
    ten = ten_steps()
    print(f"ten shallow compactions to the same 25,000: {ten:,.0f}, {ten / rows['deep']['total']:.1f} times one deep one")
    assert math.isclose(rows["deep"]["calls"], 56_250 / 13_500) and math.isclose(rows["shallow"]["calls"], 187_500 / 3_000)
