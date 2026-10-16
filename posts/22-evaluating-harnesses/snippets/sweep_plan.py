"""Post 22: what an eval sweep costs in runs, wall-clock and model spend, at each cadence.

Run from the series root:  uv run python posts/22-evaluating-harnesses/snippets/sweep_plan.py

A run is post 03's twelve-iteration example (snippets/run_cost.py there): 276,600 input tokens re-read, priced at
$3 per million, the Claude Sonnet 4.6 input rate (Anthropic pricing page, consulted October 2026). Output tokens are
left out, so the spend is the input side only; post 23 prices the whole run. Four minutes of wall-clock per run and
20 runs in parallel are illustrative. The last row is the task count ab_runner.py says a 5.4-point lift needs.
"""
import math

INPUT_TOKENS, RATE = 276_600, 3.00     # per run; dollars per million input tokens
MINUTES, PARALLEL = 4, 20              # illustrative

CADENCES = [  # (when, tasks, seeds, configs)
    ("every harness diff: smoke subset", 15, 1, 2),
    ("nightly and every model upgrade", 60, 3, 2),
    ("at release: held-out split", 30, 3, 1),
    ("sized to call a 5.4-point lift", 312, 3, 2),
]


def main():
    per_run = INPUT_TOKENS * RATE / 1e6
    print(f"one run: {INPUT_TOKENS:,} input tokens at ${RATE:.2f} per million = ${per_run:.2f}")
    print("cadence                             runs  machine-hours  wall-clock at 20-way  input spend")
    rows = []
    for when, tasks, seeds, configs in CADENCES:
        runs = tasks * seeds * configs
        hours = runs * MINUTES / 60
        wall = math.ceil(runs / PARALLEL) * MINUTES
        rows.append((when, runs, hours, wall, runs * per_run))
        spend = f"${runs * per_run:,.2f}"
        print(f"{when:34}  {runs:5,}  {hours:13.1f}  {wall:15,} min  {spend:>11}")
    return {"per_run": per_run, "rows": rows}


if __name__ == "__main__":
    main()
