"""Post 19, Make it run: wrap the loop of post 03 in a controller that reserves budget before it spends, retries a
transient failure, and turns a guard exit into a handoff that a second run resumes from.

Run from the series root:  uv run python posts/19-loop-engineering/snippets/layered_loop.py

The loop is `run()` from code/03-agent-loop/src, imported unchanged. `run()` checks its budget after the call
it has already paid for, so the controller works at the call boundary instead: `Controlled` is a Model that
wraps the scripted model, refuses a call that would cross the ceiling before making it, and retries a
transient error with exponential backoff and jitter, counting attempts apart from iterations. The task is to
migrate thirteen modules, one tool call each, then answer. Token counts are the series' illustrative run
(post 23): request n of a run sends 6,000 + 3,100 (n - 1) input tokens, and each scripted response is billed
that much. The handoff uses post 08's four headings, is written atomically and read back before it counts,
and the second run is built from the file alone. Standard library only; no network.
"""
import os
import random
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "03-agent-loop" / "src"))
from agent_loop import DEFAULT_TOOLS, ScriptedModel, run, text_response, tool_response  # noqa: E402

FIRST, GROWTH = 6_000, 3_100      # illustrative: request n sends FIRST + GROWTH * (n - 1) input tokens
BUDGET = 200_000                  # the run ceiling, in input tokens
MODULES = [f"m{k:02d}" for k in range(1, 14)]


def request_size(n):
    return FIRST + GROWTH * (n - 1)


class TransientError(Exception):
    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


class BudgetReserve(Exception):
    """Exit (3), budget, taken before the call that would cross the ceiling."""


class RetriesExhausted(Exception):
    """The provider stayed down past the retry budget; the run ends as an error, not as a fifth exit."""


class Flaky:
    """The provider: fails some attempts of some calls with a transient error before answering them."""

    def __init__(self, model, failures):
        self.model, self.failures, self.calls = model, {k: list(v) for k, v in failures.items()}, 0

    def respond(self, system, messages, tools):
        pending = self.failures.get(self.calls + 1)
        if pending:
            raise TransientError(pending.pop(0))
        self.calls += 1
        return self.model.respond(system, messages, tools)


class Controlled:
    """The controller, at the call boundary of run(): reserve before spending, retry what is transient."""

    def __init__(self, model, budget, *, max_attempts=4, base=0.01, seed=19):
        self.model, self.budget, self.max_attempts, self.base = model, budget, max_attempts, base
        self.rng = random.Random(seed)
        self.spent, self.calls, self.retries, self.messages, self.refused = 0, 0, [], [], None

    def respond(self, system, messages, tools):
        self.messages = messages
        n = self.calls + 1
        need = request_size(n)                       # the history about to be sent: assembled, so known
        if self.spent + need > self.budget:          # exit (3), reserved: stop BEFORE the call that would breach it
            self.refused = (n, need)
            raise BudgetReserve(n)
        attempt = 0
        while True:
            try:
                resp = self.model.respond(system, messages, tools)
                break                                # one iteration, however many attempts it took
            except TransientError as err:            # 429, 529, a timeout: worth another attempt
                attempt += 1
                if attempt >= self.max_attempts:     # a retry budget, not a fifth exit: the run ends as an error
                    raise RetriesExhausted(n) from err
                delay = self.base * 2 ** (attempt - 1) * (1 + self.rng.random())   # backoff with jitter
                self.retries.append((n, attempt, err.kind, delay))
                time.sleep(delay)                    # spends wall-clock, not tokens
        self.calls, self.spent = n, self.spent + resp.tokens
        return resp


def script(modules, answer):
    """One tool call per module, then the answer; response n is billed as request n of its own run."""
    calls = [tool_response("echo", {"text": f"migrated {m}"}, id=f"tu_{n}", tokens=request_size(n))
             for n, m in enumerate(modules, 1)]
    return calls + [text_response(answer, tokens=request_size(len(modules) + 1))]


def controlled_run(model, task):
    """Run post 03's loop under the controller; return (stop reason, iterations, tokens, controller)."""
    ctl = Controlled(model, BUDGET)
    try:
        result = run(ctl, DEFAULT_TOOLS, task, max_iters=40)
        return result.stop_reason.value, result.iterations, ctl.spent, ctl
    except BudgetReserve:
        return "budget", ctl.calls, ctl.spent, ctl
    except RetriesExhausted:
        return "error", ctl.calls, ctl.spent, ctl


def migrated(messages):
    """What the transcript shows as done: the modules whose tool results came back."""
    return [b["content"].split()[-1] for m in messages if m["role"] == "user" and isinstance(m["content"], list)
            for b in m["content"] if b.get("type") == "tool_result"]


def write_handoff(path, text):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)                            # atomic: the old file or the new one, never half of each
    if path.read_text(encoding="utf-8") != text:     # writing is not the same as having written (post 08)
        raise RuntimeError("handoff did not land")


def read_handoff(path):
    text, fields, head = path.read_text(encoding="utf-8"), {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            head = line[3:]
            fields[head] = ""
        elif head and line:
            fields[head] = (fields[head] + " " + line).strip()
    return fields


def handoff_text(done, todo, reason, ctl):
    if reason == "budget":
        n, need = ctl.refused
        state = (f"stopped on budget, exit (3), before call {n}: {ctl.spent:,} of {BUDGET:,} tokens spent; "
                 f"call {n} would send {need:,}.")
    else:
        state = f"stopped on {reason} at call {ctl.calls + 1}: {ctl.spent:,} of {BUDGET:,} tokens spent."
    return ("# Handoff\n\n"
            f"## Spec\nMigrate modules {MODULES[0]} to {MODULES[-1]}; answer when all {len(MODULES)} are done.\n\n"
            f"## Done\n{', '.join(done)} ({len(done)} of {len(MODULES)}).\n\n"
            f"## Next\nMigrate {', '.join(todo)}, then answer.\n\n"
            f"## State\n{state}\n")


def demo():
    out = {}
    task = f"Migrate modules {MODULES[0]} to {MODULES[-1]}, one at a time, then answer."
    answer1 = f"All {len(MODULES)} modules migrated."
    # the companion alone, its budget checked after the call it has already paid for
    arrears = run(ScriptedModel(script(MODULES, answer1)), DEFAULT_TOOLS, task, max_iters=40, token_budget=BUDGET)
    out["arrears"] = (arrears.stop_reason.value, arrears.iterations, arrears.tokens_used)
    # run 1: the same task under the controller, with a rate limit and an overload on call 4
    flaky = Flaky(ScriptedModel(script(MODULES, answer1)), {4: ["rate_limit_error (429)", "overloaded_error (529)"]})
    reason, iters, spent, ctl = controlled_run(flaky, task)
    out["run1"], out["ctl1"] = (reason, iters, spent), ctl
    if reason == "completed":                       # nothing caught the run: no handoff is owed
        out["handoff"] = None
    else:                                            # a guard exit (or an error): hand off, then resume
        done = migrated(ctl.messages)
        todo = [m for m in MODULES if m not in done]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "handoff.md"
            write_handoff(path, handoff_text(done, todo, reason, ctl))
            fields = read_handoff(path)              # run 2 sees this file and nothing else from run 1
        out["handoff"] = fields
        nxt = fields["Next"].removeprefix("Migrate ").removesuffix(", then answer.").split(", ")
        resume = f"Resume from this handoff. Spec: {fields['Spec']} Done: {fields['Done']} Next: {fields['Next']}"
        reason2, iters2, spent2, ctl2 = controlled_run(ScriptedModel(script(nxt, answer1)), resume)
        out["run2"], out["next"] = (reason2, iters2, spent2), nxt
        out["answer2"] = next((b["text"] for m in reversed(ctl2.messages) if m["role"] == "assistant"
                               for b in m["content"] if b.get("type") == "text"), None)
    # the provider down for good on call 2: four attempts, then the run ends as an error
    down = Flaky(ScriptedModel(script(MODULES, answer1)), {2: ["overloaded_error (529)"] * 4})
    out["down"] = controlled_run(down, task)[:3]
    return out


if __name__ == "__main__":
    o = demo()
    print(f"illustrative run: request n sends {FIRST:,} + {GROWTH:,} (n - 1) input tokens; ceiling {BUDGET:,}")
    print(f"{'run':40}{'stop_reason':>12}{'iterations':>12}{'tokens':>10}")
    rows = [("companion run(), budget after the call", o["arrears"]), ("run 1, reserve before the call", o["run1"])]
    for label, (reason, iters, spent) in rows:
        print(f"{label:40}{reason:>12}{iters:>12}{spent:>10,}")
    c = o["ctl1"]
    if c.refused:
        n, need = c.refused
        print(f"  refused call {n}: {c.spent:,} spent + {need:,} next = {c.spent + need:,} > {BUDGET:,}")
    for call, attempt, kind, delay in c.retries:
        print(f"  call {call}, attempt {attempt}: {kind}, retried after {delay:.3f} s")
    if o["handoff"]:
        print(f"  handoff written, read back: Done {o['handoff']['Done']} Next {', '.join(o['next'])}")
        reason, iters, spent = o["run2"]
        print(f"{'run 2, fresh context from the handoff':40}{reason:>12}{iters:>12}{spent:>10,}")
        if o["answer2"]:
            print(f"  answer: {o['answer2']}")
    reason, iters, spent = o["down"]
    print(f"{'provider down on call 2, 4 attempts':40}{reason:>12}{iters:>12}{spent:>10,}")
    over = o["arrears"][2] - BUDGET
    if over > 0:
        print(f"arrears overshoot: {over:,} tokens, {100 * over / BUDGET:.1f}% past the ceiling")
