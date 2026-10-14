"""The seam between context engineering and harness engineering, run offline.

one_call() is the unit of work of context engineering: one request object, one answer.
run_loop() is the unit of work of harness engineering: the same call inside a loop that
decides how many times to make it and when to stop. ScriptedModel stands in for a provider
API, so nothing here needs a key or a network.

Run from the series root:  uv run python posts/01-from-context-to-harness/snippets/harness_loop.py
"""

PREFIX, APPEND, WRITE = 4_000, 1_200, 400   # illustrative token sizes, section 6 of the post
SYSTEM = "You are a careful coding agent."
TOOLS = ["read_file", "run_tests", "edit_file"]


class ScriptedModel:
    """Answers like a provider API: a stop reason, content, the tool calls it asks for, and usage.

    It reads a file, runs the tests, then asks for the same failing edit on every turn
    after that: a doom loop. Turn n reads PREFIX + APPEND * (n - 1) tokens and writes WRITE.
    """

    SCRIPT = [("read_file", "app.py"), ("run_tests", "")]
    STUCK = ("edit_file", "app.py: the same patch again")

    def __init__(self, final_answer_on=None):
        self.final_answer_on = final_answer_on

    def create(self, system, tools, messages):
        turn = sum(m["role"] == "assistant" for m in messages) + 1
        usage = {"input": PREFIX + APPEND * (turn - 1), "output": WRITE}
        if turn == self.final_answer_on:
            return {"stop_reason": "end_turn", "content": "Done.", "tool_calls": [], "usage": usage}
        call = self.SCRIPT[turn - 1] if turn <= len(self.SCRIPT) else self.STUCK
        return {"stop_reason": "tool_use", "content": "", "tool_calls": [call], "usage": usage}


def run_tools(calls):
    return "; ".join(f"{name} -> ok" for name, _ in calls)


def one_call(model, task, memory=(), retrieved=()):
    # The whole job is this object: which layers, in which order, at what cost.
    request = {
        "system": SYSTEM,          # scaffold: the system prompt
        "tools": TOOLS,            # scaffold: what the model may reach for
        "messages": [*memory, *retrieved, {"role": "user", "content": task}],
    }
    return model.create(**request)


def run_loop(model, task, max_iters=12, token_budget=None, window=None):
    messages = [{"role": "user", "content": task}]
    read = written = 0
    recent = []
    for turn in range(1, max_iters + 1):                     # exit (2): the iteration cap
        resp = model.create(system=SYSTEM, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp["content"]})
        read += resp["usage"]["input"]
        written += resp["usage"]["output"]
        if resp["stop_reason"] == "end_turn":                # exit (1): a final answer
            return {"exit": "completed", "turn": turn, "read": read, "written": written}
        if token_budget and read + written >= token_budget:  # exit (3): the budget
            return {"exit": "budget", "turn": turn, "read": read, "written": written}
        recent = (recent + [resp["tool_calls"]])[-(window or 1):]
        if window and len(recent) == window and recent.count(recent[0]) == window:
            return {"exit": "no_progress", "turn": turn, "read": read, "written": written}  # (4)
        messages.append({"role": "user", "content": run_tools(resp["tool_calls"])})
    return {"exit": "max_iters", "turn": max_iters, "read": read, "written": written}


if __name__ == "__main__":
    answer = one_call(ScriptedModel(final_answer_on=1), "Fix the failing test in app.py.")
    print(f"one call: one request, one answer: {answer['content']!r}")
    for label, model, kwargs in [
        ("loop, model answers on turn 4", ScriptedModel(final_answer_on=4), {}),
        ("loop, doom loop, cap only", ScriptedModel(), {}),
        ("loop, doom loop, no-progress window of 3", ScriptedModel(), {"window": 3}),
    ]:
        r = run_loop(model, "Fix the failing test in app.py.", **kwargs)
        print(f"{label}: {r['exit']} on turn {r['turn']}, {r['read'] + r['written']:,} tokens")
