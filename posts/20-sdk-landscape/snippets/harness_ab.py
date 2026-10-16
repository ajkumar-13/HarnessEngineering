"""Post 20: a small harness A/B over twenty fixed tasks, five seeds each, and why it does not settle the choice.

Run from the series root:  uv run python posts/20-sdk-landscape/snippets/harness_ab.py

The two arms are the two shapes of two_shapes.py with one model held fixed. Harness A is code/24's loop, which
accepts the model's first final answer. Harness B is the hand-wired graph with one more node: a cheap check that
the answer appears in the file the agent read, and one retry when it does not. The model is a stand-in that reads
the file and then answers; on each answer it errs with a per-task probability, and an error is either a made-up
value (which B's check catches) or a value misread from the wrong line (which it does not). Every draw is seeded,
so the run is reproducible. Because the stand-in is defined, the true lift of B over A is known in closed form,
and the script prints it beside what twenty tasks measure. The grader compares the answer with the expected
value: an outcome check, separate from B's check. Tokens are counted with tiktoken's o200k_base encoding (Claude's
tokenizer is not public) and priced at $3 and $15 per million input and output tokens, the Claude Sonnet 4.6
rates (Anthropic pricing page, consulted October 2026); wall-clock is simulated at 2.0 s per model call and 0.1 s
per tool call, not measured. Every number is computed and illustrative. The real A/B runner is post 22's.
"""
import importlib.util
import math
import random
import statistics
import sys
from math import comb
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("two_shapes", HERE / "two_shapes.py")
shapes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shapes)
from minimal_harness import text_response, tool_response  # noqa: E402  (on the path two_shapes set)

SEEDS = 5
CATCHABLE = 0.4                  # share of wrong answers that are made up, and so fail B's check
RATE_IN, RATE_OUT = 3.00, 15.00  # dollars per million tokens, Claude Sonnet 4.6
CALL_S, TOOL_S = 2.0, 0.1        # simulated seconds per model call and per tool call
T_19 = 2.093                     # two-sided 95% t quantile, 19 degrees of freedom
ERR = [0.0, 0.0, 0.05, 0.05, 0.1, 0.1, 0.15, 0.2, 0.25, 0.3,
       0.3, 0.35, 0.4, 0.45, 0.5, 0.5, 0.6, 0.7, 0.8, 0.9]   # per-task error rate of one answer
KEYS = ["version", "port", "owner", "region"]


def make_task(i):
    values = {"version": f"{i % 4 + 1}.{i % 7}.{i}", "port": str(8000 + 37 * i),
              "owner": ["ana", "bo", "chen", "dev", "eli"][i % 5], "region": ["eu", "us", "ap"][i % 3]}
    key = KEYS[i % 4]
    path = f"service_{i:02d}.cfg"
    (shapes.WORKDIR / path).write_text("".join(f"{k} = {v}\n" for k, v in values.items()), encoding="utf-8")
    return {"id": f"t{i:02d}", "path": path, "key": key, "expected": values[key],
            "misread": values[KEYS[(i + 1) % 4]], "question": f"What is the {key} in {path}? Answer with the value only.",
            "err": ERR[i]}


class StandIn:
    """Reads the file on its first call, then answers; each answer is wrong with the task's error rate."""

    def __init__(self, task, seed, arm):
        self.task, self.seed, self.arm, self.answers = task, seed, arm, 0

    def respond(self, system, messages, tools):
        if len(messages) == 1:
            return tool_response("read_file", {"path": self.task["path"]})
        self.answers += 1
        draw = random.Random(f"{self.task['id']}|{self.seed}|{self.arm}|{self.answers}")
        if draw.random() >= self.task["err"]:
            return text_response(self.task["expected"])
        return text_response("9.9.9" if draw.random() < CATCHABLE else self.task["misread"])


def check(state):
    """B's extra node: the answer must appear in what the agent read; one retry if it does not."""
    observed = state["messages"][2]["content"][0]["content"]
    if state["answer"] in observed or state["retries"] >= 1:
        return state
    note = {"role": "user", "content": "check failed: that value does not appear in the file you read; read it again"}
    return {**state, "answer": None, "retries": state["retries"] + 1, "messages": state["messages"] + [note]}


def run_arm(arm, task, seed):
    model = shapes.Counting(StandIn(task, seed, arm))
    if arm == "A":
        answer = shapes.run(model, shapes.registry, task["question"], system=shapes.SYSTEM, max_iters=6).answer
    else:
        app = shapes.build_graph(model, [shapes.READ_FILE], check=check).compile({})
        answer = app.invoke(shapes.new_state(task["question"]), f"{task['id']}-{seed}")["answer"]
    cost = (model.tokens_in * RATE_IN + model.tokens_out * RATE_OUT) / 1e6
    return {"ok": answer == task["expected"], "tokens": model.tokens_in + model.tokens_out, "cost": cost,
            "seconds": model.calls * CALL_S + TOOL_S}


def sign_test(wins_a, wins_b):
    """Two-sided p-value on the discordant pairs (post 22's test)."""
    n, k = wins_a + wins_b, min(wins_a, wins_b)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def main():
    tasks = [make_task(i) for i in range(20)]
    runs = {arm: {t["id"]: [run_arm(arm, t, s) for s in range(SEEDS)] for t in tasks} for arm in "AB"}
    per_task = {arm: [sum(r["ok"] for r in runs[arm][t["id"]]) for t in tasks] for arm in "AB"}

    print(f"{len(tasks)} tasks x {SEEDS} seeds = {len(tasks) * SEEDS} runs per arm; the model is held fixed")
    print("arm  resolved   rate  tokens/run  cost/run   cost/resolved  seconds/run")
    rate = {}
    for arm in "AB":
        flat = [r for t in tasks for r in runs[arm][t["id"]]]
        solved = sum(r["ok"] for r in flat)
        rate[arm] = solved / len(flat)
        cost = sum(r["cost"] for r in flat)
        print(f"  {arm}  {solved:3d}/{len(flat)}  {rate[arm]:6.1%}  {statistics.mean(r['tokens'] for r in flat):10.0f}"
              f"  ${cost / len(flat):.5f}  ${cost / solved:.5f}       {statistics.mean(r['seconds'] for r in flat):5.1f}")

    print(f"per task, resolved of {SEEDS} (A/B): " + " ".join(f"{a}/{b}" for a, b in zip(per_task["A"], per_task["B"])))
    wins_b = sum(b > a for a, b in zip(per_task["A"], per_task["B"]))
    wins_a = sum(a > b for a, b in zip(per_task["A"], per_task["B"]))
    print(f"B-only wins {wins_b}, A-only wins {wins_a}, ties {len(tasks) - wins_a - wins_b}; "
          f"sign test p = {sign_test(wins_a, wins_b):.2f}")

    lift = rate["B"] - rate["A"]
    naive = math.sqrt(sum(rate[a] * (1 - rate[a]) for a in "AB") / (len(tasks) * SEEDS))
    diffs = [(b - a) / SEEDS for a, b in zip(per_task["A"], per_task["B"])]
    paired = statistics.stdev(diffs) / math.sqrt(len(tasks))
    low, high = lift - T_19 * paired, lift + T_19 * paired
    truth = CATCHABLE * statistics.mean(e * (1 - e) for e in ERR)   # caught once, then right on the retry
    print(f"measured lift {lift * 100:+.1f} points; naive standard error {naive * 100:.1f} points "
          f"(runs as independent), paired by task {paired * 100:.1f} points")
    print(f"95% interval on the paired lift: {low * 100:+.1f} to {high * 100:+.1f} points")
    print(f"true lift, from the stand-in's definition: {truth * 100:+.1f} points")
    needed = math.ceil(((1.96 + 0.84) * statistics.stdev(diffs) / truth) ** 2)   # 5% two-sided, 80% power
    verdict = "not callable" if low <= 0 <= high else "callable"
    print(f"verdict: {verdict}; detecting the true lift four times in five would take about {needed} tasks")
    return {"tasks": tasks, "per_task": per_task, "rate": rate, "lift": lift, "low": low, "high": high,
            "truth": truth, "wins": (wins_a, wins_b), "needed": needed}


if __name__ == "__main__":
    main()
