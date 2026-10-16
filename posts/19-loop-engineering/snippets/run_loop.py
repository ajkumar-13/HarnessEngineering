"""Post 19, the engineered loop: four layered exits around any step function, driven by four scripted runs.

Run from the series root:  uv run python posts/19-loop-engineering/snippets/run_loop.py

`run_loop` checks exit (1) first, then exit (3) in arrears (after the spend, as the companion in
code/03-agent-loop does), then exit (4) over a window of three identical states, and takes exit (2) when its
`for` runs out. The stop reasons are the series' spellings: completed, max_iters, budget, no_progress.
Each scripted run is written to reach one exit. Standard library only.
"""


def run_loop(step, goal_met, tokens_spent, *, max_iters=20, token_budget=200_000, window=3):
    """Drive `step` with four layered exits and return (stop reason, iterations).

    `tokens_spent` is required rather than optional: a meter that can be left
    out is a ceiling that silently defaults to off.
    """
    recent = []
    for i in range(1, max_iters + 1):                # exit (2): the bound on the for statement
        state = step()                               # one iteration of the loop
        if goal_met(state):                          # exit (1): checked first, the intended exit
            return "completed", i
        if tokens_spent() >= token_budget:           # exit (3): in arrears, after the spend
            return "budget", i
        recent = (recent + [state])[-window:]        # exit (4): the last `window` states identical
        if len(recent) == window and len(set(recent)) == 1:
            return "no_progress", i
    return "max_iters", max_iters


def scripted(states, tokens_per_step):
    """A step function that replays `states`, and a meter that charges `tokens_per_step` for each step."""
    it, spent = iter(states), [0]

    def step():
        spent[0] += tokens_per_step
        return next(it)

    return step, lambda: spent[0]


NEVER = lambda state: False  # noqa: E731

RUNS = [
    ("goal reached at step 5", list(range(1, 100)), 1_000, lambda state: state == 5, {}),
    ("50 tokens a step, budget 120", list(range(1, 100)), 50, NEVER, {"token_budget": 120}),
    ("the same state every step", [7] * 100, 1_000, NEVER, {}),
    ("new states, no goal, cap 6", list(range(1, 100)), 1_000, NEVER, {"max_iters": 6}),
]

if __name__ == "__main__":
    print(f"{'run':32}{'stop reason':>13}{'iterations':>12}")
    for label, states, per_step, goal, kw in RUNS:
        step, meter = scripted(states, per_step)
        reason, i = run_loop(step, goal, meter, **kw)
        print(f"{label:32}{reason:>13}{i:>12}")
