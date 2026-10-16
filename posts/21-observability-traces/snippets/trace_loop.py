"""Post 21, Make it run: instrument the loop of post 03, run it to each exit, and read every stop reason and
gate outcome back out of the exported spans.

Run from the series root:  uv run python posts/21-observability-traces/snippets/trace_loop.py

The loop is `run()` from code/03-agent-loop/src, imported unchanged. It cannot be edited, so the tracing sits
at its call boundary: `TracedModel` wraps the model and opens an `iteration` span and a `model.call` span on
every call, and `traced_tool` wraps each tool so its span records which layer decided the call (a deny-list
hook, an approval gate, a sandbox inside the tool, or nothing). `traced_run` opens the root `agent.run` span
and sets `stop.reason` in a `finally`, so a run that raises still says why it ended; a `verify.gate` span runs
the task's check after a final answer. Spans are written as JSON lines to a temporary file the moment they end,
the way an exporter ships them, and everything printed is read back from that file. Models, tools, the
approver and the checks are scripted stand-ins; no command runs and nothing touches the network. Token counts
are the series' illustrative run (post 23): call n sends 6,000 + 3,100 (n - 1) input tokens. Durations come
from a simulated clock, not a stopwatch, so every run prints the same numbers. Standard library only.
"""
import json
import random
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "03-agent-loop" / "src"))
from agent_loop import ScriptedModel, Tool, run, text_response, tool_response  # noqa: E402

VERSION = "h21.1"                      # tagged on every root span, so drift across versions is a query
FIRST, GROWTH = 6_000, 3_100           # illustrative: call n sends FIRST + GROWTH * (n - 1) input tokens


def request_size(n):
    return FIRST + GROWTH * (n - 1)


class Clock:
    """Simulated wall-clock: each operation advances it by a fixed, stated cost."""

    def __init__(self):
        self.now = 0.0

    def advance(self, seconds):
        self.now = round(self.now + seconds, 3)


class Tracer:
    """Spans with a name, ids, a parent, a start and an end, a status and attributes, exported as JSON lines."""

    def __init__(self, path, clock, seed=21):
        self.path, self.clock, self.rng, self.stack = path, clock, random.Random(seed), []

    def _hex(self, digits):
        return f"{self.rng.getrandbits(4 * digits):0{digits}x}"

    def start(self, name, **attributes):
        parent = self.stack[-1] if self.stack else None
        span = {"name": name, "trace_id": parent["trace_id"] if parent else self._hex(32),
                "span_id": self._hex(16), "parent_id": parent["span_id"] if parent else None,
                "start": self.clock.now, "end": None, "status": "ok", "attributes": dict(attributes)}
        self.stack.append(span)
        return span

    def end(self, span, status=None):
        while self.stack and self.stack[-1] is not span:   # close anything left open under it
            self.end(self.stack[-1], status)
        self.stack.pop()
        span["end"] = self.clock.now
        if status:
            span["status"] = status
        with open(self.path, "a", encoding="utf-8") as f:   # export on end, as an exporter does
            f.write(json.dumps(span, sort_keys=True) + "\n")

    def close_children(self, span):
        while self.stack and self.stack[-1] is not span:
            self.end(self.stack[-1])

    class _Span:
        def __init__(self, tracer, name, attributes):
            self.tracer, self.name, self.attributes = tracer, name, attributes

        def __enter__(self):
            self.span = self.tracer.start(self.name, **self.attributes)
            return self.span["attributes"]

        def __exit__(self, kind, err, tb):
            if err is not None:
                self.span["attributes"]["exception.type"] = kind.__name__
            self.tracer.end(self.span, "error" if err is not None else None)
            return False

    def span(self, name, **attributes):
        return Tracer._Span(self, name, attributes)


SECRET = re.compile(r"\bsk-[A-Za-z0-9-]{6,}")


def redact(args):
    """Redact at the instrumentation layer: a trace keeps every argument, which is where credentials leak."""
    return json.dumps({k: SECRET.sub("[redacted]", v) if isinstance(v, str) else v for k, v in args.items()},
                      sort_keys=True)


class TracedModel:
    """Wraps a Model: each call closes the last iteration span and opens the next, with a model.call inside."""

    def __init__(self, model, tracer, clock):
        self.model, self.tracer, self.clock, self.root = model, tracer, clock, tracer.stack[-1]
        self.calls = self.tokens = 0

    def respond(self, system, messages, tools):
        self.tracer.close_children(self.root)              # the previous iteration ends where this one starts
        self.calls += 1
        self.tracer.start("iteration", **{"iteration.index": self.calls})
        with self.tracer.span("model.call", **{"gen_ai.operation.name": "chat"}) as m:
            self.clock.advance(0.6 + request_size(self.calls) / 25_000)
            resp = self.model.respond(system, messages, tools)
            m["gen_ai.usage.input_tokens"] = resp.tokens
        self.tokens += resp.tokens
        return resp


DENY = re.compile(r"\brm\s+-rf\b|\bgit\s+push\s+--force\b")     # the hook's deny-list (post 13)
ALLOW = {"ls", "cat", "git", "pytest"}                            # the sandbox's allow-list (post 14)
SENSITIVE = {"deploy"}                                            # tools that need an approval (post 15)
COST = {"read_file": 0.12, "bash": 0.2, "run_tests": 7.8, "deploy": 1.5, "calculator": 0.05}


def traced_tool(tool, tracer, clock, outdir, approver=lambda name, args: False):
    """Wrap a tool so its span records which layer decided: blocked, denied, refused or ok."""

    def call(args):
        with tracer.span(f"tool.{tool.name}", **{"gen_ai.operation.name": "execute_tool",
                                                 "gen_ai.tool.name": tool.name}) as span:
            span["tool.args"] = redact(args)
            clock.advance(COST.get(tool.name, 0.1))
            if DENY.search(str(args.get("command", ""))):        # the hook, before the tool
                outcome, observation = "blocked", "blocked by hook: destructive command"
            elif tool.name in SENSITIVE and not approver(tool.name, args):   # the approval gate, out of band
                outcome, observation = "denied", "denied by approver"
            else:
                observation = tool.run(args)                      # the sandbox refuses inside the tool
                outcome = "refused" if observation.startswith("blocked:") else "ok"
            span["outcome"] = outcome
            if len(observation) > 200:                            # large output goes to disk; the span keeps the path
                path = outdir / f"{span_id(tracer)}.log"
                path.write_text(observation, encoding="utf-8")
                span["tool.output_path"], span["tool.output_bytes"] = path.name, len(observation.encode())
            return observation

    return Tool(tool.name, tool.description, call, tool.input_schema)


def span_id(tracer):
    return tracer.stack[-1]["span_id"]


def traced_run(tracer, clock, model, tools, task, *, check=None, **limits):
    """One instrumented run: the root span, the loop, the gate after a final answer, stop.reason in a finally."""
    root = tracer.start("agent.run", task=task, **{"harness.version": VERSION})
    stop, status, traced = "error", "error", TracedModel(model, tracer, clock)
    try:
        result = run(traced, tools, task, **limits)
        stop, status = result.stop_reason.value, None
        tracer.close_children(root)
        if check is not None and stop == "completed":
            what, passes = check
            with tracer.span("verify.gate", **{"verify.check": what}) as gate:
                clock.advance(1.2)
                gate["outcome"] = "pass" if passes(result.answer) else "fail"
        return result
    finally:
        root["attributes"]["stop.reason"] = stop                  # set even when the run raised
        root["attributes"]["gen_ai.usage.input_tokens"] = traced.tokens
        tracer.end(root, status)


# ---- the stand-in tools ----------------------------------------------------------------------------------

def _read(args):
    return "def parse(line):\n    return line.split(',')[1:]\n"


def _bash(args):
    program = args["command"].split()[0]
    if program not in ALLOW:
        return f"blocked: {program} is not on the allow-list"
    return f"(stand-in) {args['command']}"


def _tests(args):
    return "\n".join(f"tests/test_parser.py::test_case_{k:04d} PASSED" for k in range(1, 2001))


def _calc(args):
    return str(args.get("expression", ""))


TOOLS = [Tool("read_file", "Read a file.", _read), Tool("bash", "Run a command in the sandbox.", _bash),
         Tool("run_tests", "Run the test suite.", _tests), Tool("deploy", "Deploy a build.", lambda a: "deployed"),
         Tool("calculator", "Evaluate an expression.", _calc)]


class Down:
    """The provider: answers call 1, then fails every call. A ConnectionError is not one of the four exits."""

    def __init__(self, model):
        self.model, self.calls = model, 0

    def respond(self, system, messages, tools):
        self.calls += 1
        if self.calls > 1:
            raise ConnectionError("provider unreachable")
        return self.model.respond(system, messages, tools)


def scripted(steps):
    """A ScriptedModel whose call n reports the illustrative input size of call n."""
    out = []
    for n, step in enumerate(steps, 1):
        if isinstance(step, str):
            out.append(text_response(step, tokens=request_size(n)))
        else:
            out.append(tool_response(step[0], step[1], id=f"tu_{n}", tokens=request_size(n)))
    return ScriptedModel(out)


READ = ("read_file", {"path": "src/parser.py"})
RUNS = [
    ("1 gated, healthy", [READ, ("bash", {"command": "rm -rf build/"}),
                          ("bash", {"command": "curl -H 'Authorization: Bearer sk-live-4f9a2c71' https://example.com"}),
                          ("run_tests", {}), ("deploy", {"env": "production"}),
                          "Fixed the off-by-one in parser.py; the suite passes."],
     dict(check=("tests pass", lambda answer: True))),
    ("2 doom loop, exit (4) on", [READ] * 12, dict(no_progress_window=3)),
    ("3 doom loop, exit (4) off", [READ] * 12, dict(no_progress_window=13)),
    ("4 growing context", [("calculator", {"expression": f"{k} * 7"}) for k in range(1, 13)],
     dict(token_budget=100_000)),
    ("5 provider down", [READ, READ, "unreachable"], dict(provider="down")),
    ("6 ungated answer", [READ, "Done: parser fixed."], dict()),
]


def DOWNSTREAM(task):
    """The check a later stage runs on run 6's claimed fix: the stand-in suite still fails."""
    return "fail" if task.startswith("6") else "pass"


def read_back(path):
    """Rebuild every run's tree from the exported file alone."""
    spans = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
    traces = {}
    for s in spans:
        traces.setdefault(s["trace_id"], []).append(s)
    return spans, traces


def tree(spans):
    kids = {}
    for s in spans:
        kids.setdefault(s["parent_id"], []).append(s)
    for v in kids.values():
        v.sort(key=lambda s: (s["start"], s["name"] != "model.call"))
    out = []

    def walk(s, depth):
        out.append((depth, s))
        for c in kids.get(s["span_id"], []):
            walk(c, depth + 1)

    walk(kids[None][0], 0)
    return out


def label(s):
    a = s["attributes"]
    keys = ["stop.reason", "iteration.index", "gen_ai.usage.input_tokens", "outcome", "tool.args",
            "tool.output_bytes"]
    if s["name"] == "agent.run":
        keys = ["stop.reason"]
    bits = [f"{k.split('.')[-1] if k != 'stop.reason' else k}={a[k]:,}" if isinstance(a.get(k), int)
            else f"{k}={a[k]}" for k in keys if k in a]
    if s["status"] == "error":
        bits.append(f"status=error {a.get('exception.type', '')}".rstrip())
    return " ".join(bits)


def demo(path):
    results = {}
    for name, steps, opts in RUNS:
        opts = dict(opts)
        clock = Clock()
        tracer = Tracer(path, clock, seed=len(results) + 21)
        outdir = Path(path).parent
        tools = [traced_tool(t, tracer, clock, outdir) for t in TOOLS]
        model = Down(scripted(steps)) if opts.pop("provider", None) == "down" else scripted(steps)
        try:
            results[name] = traced_run(tracer, clock, model, tools, f"run {name}", **opts).stop_reason.value
        except ConnectionError:
            results[name] = "raised"
    return results


def summarise(path):
    spans, traces = read_back(path)
    rows = []
    for spans_of_run in traces.values():
        root = next(s for s in spans_of_run if s["parent_id"] is None)
        gate = [s["attributes"]["outcome"] for s in spans_of_run if s["name"] == "verify.gate"]
        tools = sorted((s for s in spans_of_run if s["name"].startswith("tool.")), key=lambda s: s["start"])
        rows.append(dict(task=root["attributes"]["task"][4:], stop=root["attributes"]["stop.reason"],
                         iters=sum(s["name"] == "iteration" for s in spans_of_run),
                         tokens=root["attributes"]["gen_ai.usage.input_tokens"],
                         gate=gate[0] if gate else "none", outcomes=[s["attributes"]["outcome"] for s in tools],
                         spans=len(spans_of_run), seconds=root["end"] - root["start"], all=spans_of_run))
    return spans, rows


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "spans.jsonl"
        returned = demo(path)
        spans, rows = summarise(path)
        size = path.stat().st_size
        print(f"{len(spans)} spans in {len(rows)} traces exported to spans.jsonl, {size:,} bytes; "
              "everything below is read back from the file")
        print(f"{'run':<26}{'stop.reason':>12}{'iterations':>11}{'input tokens':>13}{'verify.gate':>12}"
              "  tool outcomes")
        for r in rows:
            seen = ", ".join(f"{n} {o}" if n > 1 else o for o, n in _runs(r["outcomes"])) or "none"
            print(f"{r['task']:<26}{r['stop']:>12}{r['iters']:>11}{r['tokens']:>13,}{r['gate']:>12}  {seen}")
        for r, (name, value) in zip(rows, returned.items()):
            assert r["task"] == name and (r["stop"] == value or (value == "raised" and r["stop"] == "error"))
        first = rows[0]
        print(f"\nrun 1, {first['spans']} spans, {first['seconds']:.1f} s simulated:")
        for depth, s in tree(first["all"]):
            print(f"{'  ' * depth}{s['name']:<{24 - 2 * depth}}{s['end'] - s['start']:>6.2f} s  {label(s)}")
        doom = rows[2]
        bytes_doom = sum(len(json.dumps(s, sort_keys=True)) + 1 for s in doom["all"])
        print(f"\nrun 3 skeleton: {doom['spans']} spans, {bytes_doom:,} bytes, "
              f"{bytes_doom / doom['spans']:.0f} bytes a span")
        down = rows[4]
        broke = [s for s in down["all"] if s["status"] == "error"]
        ungated = rows[5]
        late = DOWNSTREAM(ungated["task"])
        print(f"run 6: stop.reason={ungated['stop']}, verify.gate spans: {ungated['gate']}; "
              f"the downstream check, run afterwards: {late}")
        print("run 5 spans with status=error: " + ", ".join(s["name"] for s in sorted(broke, key=lambda s: -s["start"]))
              + f"; root stop.reason={down['stop']}")


def _runs(items):
    out = []
    for x in items:
        if out and out[-1][0] == x:
            out[-1] = (x, out[-1][1] + 1)
        else:
            out.append((x, 1))
    return out


if __name__ == "__main__":
    main()
