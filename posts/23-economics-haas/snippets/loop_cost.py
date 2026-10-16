"""Post 23: what one run of the agent loop costs, uncached, with a cached static head, and with a rolling breakpoint.

Run from the series root:  uv run python posts/23-economics-haas/snippets/loop_cost.py

The run is the series' running example, illustrative rather than measured: the first request sends 6,000 input
tokens, and each turn appends about 600 tokens of model output and 2,500 of tool result, so request n sends
6,000 + 3,100 (n - 1) tokens; every iteration emits 600 output tokens. Rates are Anthropic's for Claude Sonnet 4.6
and Claude Haiku 4.5 (pricing and prompt-caching pages, consulted October 2026); re-derive them before use.
Three ways of paying for the same requests:
  uncached     every input token at the base rate;
  static head  a 5,000-token head of tool schemas and system prompt written once at 1.25x and read at 0.1x on
               every later request, everything else at the base rate;
  rolling      a breakpoint on the last block of each request, so everything the previous request sent is read
               at 0.1x and only the tokens new since then are written, at 1.25x (the five-minute tier).
Standard library only.
"""
RATES = {  # dollars per million tokens, and multipliers of base input (Anthropic pricing page, October 2026)
    "sonnet-4.6": {"input": 3.00, "output": 15.00},
    "haiku-4.5": {"input": 1.00, "output": 5.00},
    "write_5m": 1.25, "write_1h": 2.0, "read": 0.1,
}
FIRST, GROWTH, OUTPUT, HEAD = 6_000, 3_100, 600, 5_000   # tokens, illustrative
MODEL_SECONDS, TOOL_SECONDS = 2.0, 1.0                    # per iteration, illustrative


def requests(n):
    """Input tokens sent by each of n requests."""
    return [FIRST + GROWTH * i for i in range(n)]


def iteration_costs(n, mode, model="sonnet-4.6"):
    """Dollars for each of n iterations, input and output, under one way of paying."""
    base, out = RATES[model]["input"] / 1e6, RATES[model]["output"] / 1e6
    costs, prev = [], 0
    for i, sent in enumerate(requests(n)):
        if mode == "uncached":
            dollars = sent * base
        elif mode == "static head":
            head = HEAD * base * (RATES["write_5m"] if i == 0 else RATES["read"])
            dollars = head + (sent - HEAD) * base
        elif mode == "rolling":
            dollars = prev * base * RATES["read"] + (sent - prev) * base * RATES["write_5m"]
        else:
            raise ValueError(mode)
        costs.append(dollars + OUTPUT * out)
        prev = sent
    return costs


def run_cost(n, mode, model="sonnet-4.6"):
    return sum(iteration_costs(n, mode, model))


def cumulative(n, mode):
    """Cumulative dollars after each iteration: the series the post's hero chart is drawn from."""
    total, out = 0.0, []
    for c in iteration_costs(n, mode):
        total += c
        out.append(total)
    return out


def main():
    base, out = RATES["sonnet-4.6"]["input"] / 1e6, RATES["sonnet-4.6"]["output"] / 1e6
    for n in (12, 40):
        sent = requests(n)
        print(f"{n} iterations: last request {sent[-1]:,} tokens; input {sum(sent):,}, of which "
              f"{sum(sent[:-1]):,} already sent the turn before; output {n * OUTPUT:,}")
        for mode in ("uncached", "static head", "rolling"):
            print(f"  {mode:<12} ${run_cost(n, mode):.3f}")
    u12, r12, u40, r40 = (run_cost(n, m) for n in (12, 40) for m in ("uncached", "rolling"))
    print(f"growth from 12 to 40 iterations: uncached {u40 / u12:.1f}x, rolling {r40 / r12:.1f}x, "
          f"uncached per iteration {(u40 / 40) / (u12 / 12):.1f}x")
    print(f"saved by the rolling breakpoint: {1 - r12 / u12:.0%} at 12 iterations, {1 - r40 / u40:.0%} at 40; "
          f"by the static head: {1 - run_cost(12, 'static head') / u12:.0%} at 12")
    print(f"input side only at 12 iterations: rolling ${r12 - 12 * OUTPUT * out:.3f}, "
          f"uncached ${u12 - 12 * OUTPUT * out:.3f}")

    unc, rol = iteration_costs(12, "uncached"), iteration_costs(12, "rolling")
    print(f"one iteration: uncached ${unc[0]:.3f} first, ${unc[-1]:.3f} twelfth; "
          f"rolling ${rol[0]:.4f} first, ${rol[-1]:.4f} twelfth")
    print(f"a 600-token narration at iteration 3: ${600 * out:.3f} to generate, "
          f"{600 * 9:,} tokens re-read on 9 later turns, ${600 * 9 * base:.4f} uncached")
    log = 12_000
    print(f"a 12,000-token test log at iteration 3, in requests 4 to 12: {log * 9:,} input tokens, "
          f"${log * 9 * base:.3f} uncached ({log * 9 * base / u12:.0%} of the run), "
          f"${log * base * RATES['write_5m'] + log * 8 * base * RATES['read']:.3f} on a rolling breakpoint")

    moved = [3, 5, 7, 9]   # iterations 4, 6, 8 and 10, taken out of the warm conversation
    sent = requests(12)
    cheap = sum(sent[i] for i in moved) * RATES["haiku-4.5"]["input"] / 1e6 \
        + len(moved) * OUTPUT * RATES["haiku-4.5"]["output"] / 1e6
    warm = sum(rol[i] for i in moved)
    print(f"routing iterations 4, 6, 8 and 10 to Claude Haiku 4.5 uncached: {sum(sent[i] for i in moved):,} input "
          f"tokens, ${cheap:.3f}, against ${warm:.3f} left warm on Claude Sonnet 4.6")
    print(f"latency: 12 iterations of {MODEL_SECONDS:.0f} s model and {TOOL_SECONDS:.0f} s tool is "
          f"{12 * (MODEL_SECONDS + TOOL_SECONDS):.0f} s; at iteration 12 a warm cache leaves "
          f"{GROWTH:,} of {sent[-1]:,} tokens to prefill")

    if (FIRST, GROWTH, OUTPUT, HEAD) != (6_000, 3_100, 600, 5_000):
        return                                  # a variation: the post's values no longer apply
    assert [round(run_cost(12, m), 3) for m in ("uncached", "static head", "rolling")] == [0.938, 0.793, 0.329]
    assert (round(u40, 2), round(r40, 2)) == (8.33, 1.60)


if __name__ == "__main__":
    main()
