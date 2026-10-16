"""Post 22: the harness A/B runner, the paired difference with its interval, and whether the result is callable.

Run from the series root:  uv run python posts/22-evaluating-harnesses/snippets/ab_runner.py

Every number is computed and illustrative: the arms are stand-ins, not agents. A task is a resolve probability p,
spread evenly over 0.05 to 0.95 across the set (a fixed, seeded draw). Harness A runs the task once and keeps what
it gets. Harness B is A plus a verification gate: the gate costs a check, catches three wrong results in ten,
and then the task is attempted once more. The model is the same in both arms, so B is at least as good on every
task, and its true lift is known in closed form, mean over tasks of CATCH * (1 - p) * p, which a real A/B never
knows. Each run is drawn from its own seeded stream, so the output is reproducible.

Tokens are input tokens re-read per attempt: 276,600, the twelve-iteration run of post 03's run_cost.py, plus an
illustrative 20,000 for the gate's check; dollars at $3 per million input tokens, the Claude Sonnet 4.6 rate
(Anthropic pricing page, consulted October 2026). The interval is a t interval on the per-task paired differences,
with a bootstrap over tasks beside it as a check; a result is callable when its interval excludes zero. Standard
library only (statistics, random, math); no scipy.
"""
import math
import random
import statistics
from math import comb

TASKS, SEEDS, CATCH = 60, 3, 0.3
ATTEMPT, GATE, RATE = 276_600, 20_000, 3.00      # input tokens per attempt and per check; dollars per million
CONFIGS = {"A": {"verify_gate": False},          # Harness A: no verification gate
           "B": {"verify_gate": True}}           # Harness B: plus a verification gate
Z95, Z80 = 1.959964, 0.841621                    # two-sided 5% and one-sided 20% normal quantiles


def make_tasks(n, salt="set-v1"):
    """A fixed, versioned task set: n resolve probabilities spread over 0.05 to 0.95."""
    rng = random.Random(f"tasks|{salt}")
    ps = [0.05 + 0.9 * i / (n - 1) for i in range(n)]
    rng.shuffle(ps)
    return ps


def run(p, config, rng):
    """One run of a task under one harness config, with the model held fixed: (resolved, input tokens)."""
    ok, tokens = rng.random() < p, ATTEMPT
    if config["verify_gate"]:
        tokens += GATE
        if not ok and rng.random() < CATCH:      # the gate catches a wrong result: one more attempt
            ok, tokens = rng.random() < p, tokens + ATTEMPT
    return ok, tokens


# A/B two harness configs on one fixed task set, every task once per seed, the model held fixed.
def ab(tasks, seeds, salt="sweep-1"):
    rows = []
    for t, p in enumerate(tasks):                        # fixed, versioned, never edited
        row = {}
        for name, config in CONFIGS.items():
            runs = [run(p, config, random.Random(f"{salt}|{t}|{s}|{name}")) for s in range(seeds)]
            row[name] = (sum(ok for ok, _ in runs), sum(tokens for _, tokens in runs))
        rows.append(row)                                 # resolved of `seeds`, and tokens, per arm
    return rows


def t95(df):
    """Two-sided 95% Student t quantile by the Cornish-Fisher expansion (exact to three decimals from df = 10)."""
    z = Z95
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def sign_test(wins_a, wins_b):
    """Two-sided p-value on the discordant pairs: could this split be a coin flip?"""
    n, k = wins_a + wins_b, min(wins_a, wins_b)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def paired(rows, seeds):
    """The per-task paired differences, B minus A, and the mean lift with its 95% t interval."""
    d = [(r["B"][0] - r["A"][0]) / seeds for r in rows]
    lift, se = statistics.mean(d), statistics.stdev(d) / math.sqrt(len(d))
    half = t95(len(d) - 1) * se
    return d, lift, lift - half, lift + half


def bootstrap(d, reps=2000, salt="boot"):
    """A percentile interval from resampling tasks with replacement, as a check on the t interval."""
    rng = random.Random(salt)
    means = sorted(statistics.mean(rng.choices(d, k=len(d))) for _ in range(reps))
    return means[int(0.025 * reps)], means[int(0.975 * reps) - 1]


def callable_(low, high):
    return "callable" if low > 0 or high < 0 else "not callable"


def power_by_simulation(n_tasks, seeds, reps=200):
    """How often a fresh experiment of this size calls the lift in B's favour."""
    called = 0
    for rep in range(reps):
        rows = ab(make_tasks(n_tasks, salt=f"rep{rep}"), seeds, salt=f"rep{rep}")
        called += paired(rows, seeds)[2] > 0
    return called / reps


def main():
    tasks = make_tasks(TASKS)
    rows = ab(tasks, SEEDS)
    runs = TASKS * SEEDS
    print(f"{TASKS} tasks x {SEEDS} seeds = {runs} runs per arm; the model is held fixed")
    print("arm  resolved   rate   input tokens/run  cost/resolved")
    rate, cost_per = {}, {}
    for arm in "AB":
        solved, tokens = sum(r[arm][0] for r in rows), sum(r[arm][1] for r in rows)
        rate[arm], cost_per[arm] = solved / runs, tokens * RATE / 1e6 / solved
        print(f"  {arm}  {solved:3d}/{runs}  {rate[arm]:6.1%}  {tokens / runs:16,.0f}  ${cost_per[arm]:.2f}")

    wins_b = sum(r["B"][0] > r["A"][0] for r in rows)
    wins_a = sum(r["A"][0] > r["B"][0] for r in rows)
    print(f"B-only wins {wins_b}, A-only wins {wins_a}, ties {TASKS - wins_a - wins_b}; "
          f"sign test p = {sign_test(wins_a, wins_b):.2f}")
    d, lift, low, high = paired(rows, SEEDS)
    naive = math.sqrt(sum(rate[a] * (1 - rate[a]) for a in "AB") / runs)
    b_low, b_high = bootstrap(d)
    truth = CATCH * statistics.mean((1 - p) * p for p in tasks)
    print(f"measured lift {lift * 100:+.1f} points; standard error {naive * 100:.1f} points with runs as "
          f"independent, {statistics.stdev(d) / math.sqrt(TASKS) * 100:.1f} paired by task")
    print(f"95% interval on the paired lift: {low * 100:+.1f} to {high * 100:+.1f} points "
          f"(bootstrap {b_low * 100:+.1f} to {b_high * 100:+.1f})")
    print(f"true lift, from the stand-ins' definition: {truth * 100:+.1f} points")
    print(f"verdict: {callable_(low, high)}")

    needed = math.ceil(((Z95 + Z80) * statistics.stdev(d) / truth) ** 2)
    print(f"sizing: detecting the true lift four times in five takes about {needed} tasks at {SEEDS} seeds")
    p_small, p_big = power_by_simulation(TASKS, SEEDS), power_by_simulation(needed, SEEDS)
    print(f"called in B's favour over 200 fresh experiments: {TASKS} tasks {p_small:.0%}, {needed} tasks {p_big:.0%}")

    unpaired = Z95 * math.sqrt(2 * 0.5 * 0.5 / 50)
    print(f"unpaired, 50 different tasks per arm near 50%: 95% interval +/- {unpaired * 100:.1f} points")
    print(f"one seed, 60 tasks, B-only 8 against A-only 4: lift {(8 - 4) / 60 * 100:+.1f} points, "
          f"sign test p = {sign_test(4, 8):.3f}; split 10 to 2: p = {sign_test(2, 10):.3f}")
    return {"tasks": tasks, "rows": rows, "d": d, "rate": rate, "cost_per": cost_per, "lift": lift, "low": low,
            "high": high, "boot": (b_low, b_high), "naive": naive, "truth": truth, "wins": (wins_a, wins_b),
            "needed": needed, "power": (p_small, p_big), "unpaired": unpaired}


if __name__ == "__main__":
    main()
