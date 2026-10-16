"""Post 26, "Cost guardrails": what the demo's cost line is made of, and what the meter leaves out.

Run from the series root:  uv run python posts/26-capstone-coding-agent/snippets/cost_table.py

Imports CostMeter from code/26-coding-agent/src/coding_agent/cost.py unchanged. The rates are the Claude Sonnet 4.6
rates of Anthropic's pricing page (consulted October 2026): $3 per million input tokens, $15 per million output
tokens, a cache read at 0.1 times the input rate, a five-minute cache write at 1.25 times; the meter's defaults
are the same three numbers it uses (input, output, cache read) and it has no write term. The demo spends three
attempts of 2,000 input tokens (1,500 of them the cached prefix) and 300 output tokens each, the driver's default
tokens_per_attempt. The two larger run shapes (4,000 and 8,000 input tokens and 400 output tokens per attempt) keep
three attempts and a 75% cached prefix and are illustrative.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "26-coding-agent" / "src"))
from coding_agent import CostMeter  # noqa: E402

RATES = {"input": 3.00, "output": 15.00, "cache_read": 0.1, "cache_write_5m": 1.25}   # $ per million; multipliers
ATTEMPTS = 3


def meter(inp, cached, out, attempts=ATTEMPTS):
    """The companion's meter, fed `attempts` attempts of one shape."""
    m = CostMeter(input_price=RATES["input"], output_price=RATES["output"], cache_discount=RATES["cache_read"])
    for _ in range(attempts):
        m.add(input_tokens=inp, cached_tokens=cached, output_tokens=out)
    return m


def uncached(inp, out, attempts=ATTEMPTS):
    return attempts * (inp * RATES["input"] + out * RATES["output"]) / 1e6


def with_writes(inp, cached, out, writes, attempts=ATTEMPTS):
    """The same attempts priced with `writes` of them writing the prefix at 1.25x and the rest reading it."""
    fresh = (inp - cached) * RATES["input"]
    write = cached * RATES["input"] * RATES["cache_write_5m"]
    read = cached * RATES["input"] * RATES["cache_read"]
    return (attempts * (fresh + out * RATES["output"]) + writes * write + (attempts - writes) * read) / 1e6


def main():
    demo = meter(2000, 1500, 300)
    print(f"the demo, as the meter prices it: ${demo.cost():.4f} for {demo.input_tokens} in "
          f"({demo.cached_tokens} cached), {demo.output_tokens} out")
    share = demo.cached_tokens / demo.input_tokens
    out_dollars = demo.output_tokens * RATES["output"] / 1e6
    tokens = demo.input_tokens + demo.output_tokens
    print(f"cached share of input: {share:.0%}; output: {demo.output_tokens / tokens:.0%} of the tokens, "
          f"${out_dollars:.4f} = {out_dollars / demo.cost():.0%} of the money")
    print()
    print("run shape (3 attempts)          input : output       75% cached   no cache   penalty")
    for label, inp, out in (("the demo, generation-heavy", 2000, 300),
                            ("a context-heavy task", 4000, 400),
                            ("a long-horizon re-read", 8000, 400)):
        cached = inp * 3 // 4
        m = meter(inp, cached, out)
        u = uncached(inp, out)
        print(f"  {label:<29} {ATTEMPTS * inp:>6,} : {ATTEMPTS * out:<6,} ({ATTEMPTS * inp / (ATTEMPTS * out):4.1f} to 1)"
              f"   ${m.cost():.4f}     ${u:.4f}    {u / m.cost():.2f}x")
    print()
    print("the write side the meter omits (the demo's attempts, five-minute tier)")
    rows = (("as metered: every attempt reads", None),
            ("one write, then reads within five minutes", 1),
            ("a write every attempt, each more than five minutes apart", ATTEMPTS))
    u = uncached(2000, 300)
    for label, writes in rows:
        c = demo.cost() if writes is None else with_writes(2000, 1500, 300, writes)
        print(f"  {label:<57} ${c:.4f}  ({c / u - 1:+.0%} against no cache, ${u:.4f})")


if __name__ == "__main__":
    main()
