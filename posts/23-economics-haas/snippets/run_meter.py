"""Post 23: a per-run cost and latency meter over one captured run, priced three ways, and cost per successful run.

Run from the series root:  uv run python posts/23-economics-haas/snippets/run_meter.py

The captured run is the series' running example (illustrative): twelve requests of 6,000 + 3,100 (n - 1) input
tokens and 600 output tokens each, two seconds of model time and one of tool time per iteration. It is written as
one JSON line per model call, each carrying the `usage` fields the Anthropic Messages API reports (`input_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`; the three input fields sum to the
request's input, per the prompt-caching page), to a temporary file, and read back before it is metered. Rates are
Claude Sonnet 4.6's (Anthropic pricing and prompt-caching pages, consulted October 2026). The companion meter
`CostMeter` is imported unchanged from code/26-coding-agent/src/coding_agent/cost.py and run on the same calls.
The ten-run set and the two harnesses of the last block are illustrative. Standard library only.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "26-coding-agent" / "src"))
from coding_agent.cost import CostMeter  # noqa: E402

FIRST, GROWTH, OUTPUT = 6_000, 3_100, 600   # the running example's sizes, illustrative

# Per-run cost and latency meter at Claude Sonnet 4.6's rates (Anthropic, "Pricing", consulted October 2026).
IN_PRICE, OUT_PRICE = 3.00 / 1e6, 15.00 / 1e6   # dollars per input and per output token
READ, WRITE = 0.1, {"5m": 1.25, "1h": 2.0}        # multipliers of base input


def meter_run(calls, budget_usd=None, ttl="5m"):
    cost = seconds = 0.0
    for i, u in enumerate(calls):            # u: one call's provider-reported usage
        step = (u["input_tokens"] * IN_PRICE
                + u["cache_creation_input_tokens"] * IN_PRICE * WRITE[ttl]
                + u["cache_read_input_tokens"] * IN_PRICE * READ
                + u["output_tokens"] * OUT_PRICE)
        if budget_usd is not None and cost + step > budget_usd:
            return cost, seconds, f"budget: refused iteration {i + 1}"
        cost, seconds = cost + step, seconds + u["model_seconds"] + u["tool_seconds"]
    return cost, seconds, "completed"


def capture(n, cached=True):
    """The usage records of an n-iteration run: with a breakpoint on the last block of every request, or none."""
    calls, prev = [], 0
    for i in range(n):
        sent = FIRST + GROWTH * i
        read, write = (prev, sent - prev) if cached else (0, 0)
        calls.append({"input_tokens": sent - read - write, "cache_creation_input_tokens": write,
                      "cache_read_input_tokens": read, "output_tokens": OUTPUT,
                      "model_seconds": 2.0, "tool_seconds": 1.0})
        prev = sent
    return calls


def round_trip(calls):
    """Write the calls as JSON lines and read them back, as a harness's run log would be."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "run.jsonl"
        path.write_text("".join(json.dumps(c) + "\n" for c in calls), encoding="utf-8")
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def companion(calls, budget_usd=None):
    """The capstone's CostMeter on the same calls: it is told total input and the cached part, and stops at the
    top of an iteration once spend has reached the ceiling."""
    m = CostMeter(budget_usd=budget_usd)
    done = 0
    for u in calls:
        if m.over_budget():
            break
        total = u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
        m.add(input_tokens=total, cached_tokens=u["cache_read_input_tokens"], output_tokens=u["output_tokens"],
              seconds=u["model_seconds"] + u["tool_seconds"])
        done += 1
    return m.cost(), done


TEN_RUNS = [(7, True), (9, True), (12, False), (8, True), (12, False),
            (10, True), (6, True), (12, False), (11, True), (9, True)]   # (iterations, passed), illustrative

HARNESSES = {  # illustrative: B's verification gate adds four iterations to every run
    "A, no gate": {"iterations": 12, "first_pass": 0.48, "review_minutes": 18, "escape": 0.14},
    "B, gate on every step": {"iterations": 16, "first_pass": 0.84, "review_minutes": 6, "escape": 0.04},
}
REVIEW_PER_HOUR = 90.0   # a placeholder loaded rate


def shipped(h):
    per_run = meter_run(capture(h["iterations"]))[0]
    per_accepted = per_run / h["first_pass"]
    review = h["review_minutes"] / 60 * REVIEW_PER_HOUR
    per_shipped = (per_accepted + review) / (1 - h["escape"])
    return per_run, per_accepted, review, per_shipped


def main():
    run = round_trip(capture(12))
    print(f"captured run: {len(run)} calls written as JSON lines and read back")
    for label, calls, ttl in (("no cache", round_trip(capture(12, cached=False)), "5m"),
                              ("rolling breakpoint, five-minute tier", run, "5m"),
                              ("rolling breakpoint, one-hour tier", run, "1h")):
        print("%-38s $%.4f  %.1fs  %s" % ((label,) + meter_run(calls, ttl=ttl)))
    print("%-38s $%.4f  %.1fs  %s" % (("ceiling $0.25, five-minute tier",) + meter_run(run, 0.25)))
    full, n = companion(run)
    capped, m = companion(run, budget_usd=0.25)
    print(f"companion CostMeter: ${full:.4f} for {n} calls (fresh input at 1.0x, no write premium)")
    print(f"companion with budget_usd=0.25: stops after {m} calls at ${capped:.4f} by its own count, "
          f"${meter_run(run[:m])[0]:.4f} at the write price")

    costs = [meter_run(capture(it))[0] for it, _ in TEN_RUNS]
    passed = sum(ok for _, ok in TEN_RUNS)
    win = [c for c, (_, ok) in zip(costs, TEN_RUNS) if ok]
    print(f"ten runs, {passed} passed: spend ${sum(costs):.3f}, ${sum(costs) / len(costs):.4f} per run, "
          f"${sum(costs) / passed:.4f} per successful run; a successful run alone averages ${sum(win) / passed:.4f}")
    print(f"{'harness':<24}{'per run':>9}{'per accepted':>14}{'review':>9}{'per shipped':>13}")
    rows = {k: shipped(h) for k, h in HARNESSES.items()}
    for k, (r, a, v, s) in rows.items():
        print(f"{k:<24}{'$%.3f' % r:>9}{'$%.3f' % a:>14}{'$%.2f' % v:>9}{'$%.2f' % s:>13}")
    (ra, _, _, sa), (rb, _, _, sb) = rows.values()
    print(f"B costs {rb / ra - 1:.0%} more per run and {sb / sa:.2f} times as much per unit shipped")

    assert round(meter_run(run)[0], 4) == 0.3293 and meter_run(run, 0.25)[2] == "budget: refused iteration 10"


if __name__ == "__main__":
    main()
