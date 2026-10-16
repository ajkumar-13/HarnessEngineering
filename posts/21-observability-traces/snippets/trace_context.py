"""Post 21, section 6: carry a span context into a child process with a W3C traceparent, built and parsed by hand.

Run from the series root:  uv run python posts/21-observability-traces/snippets/trace_context.py

The parent opens a root span and three iteration spans; on iteration 3 it launches a sub-agent as a separate
`sys.executable` process. The child reads TRACEPARENT from its environment, parses it, and opens its
`subagent.run` span as a child of the span named there, or as a new root when there is nothing to parse. Three
launches show the right wiring and the two silent failures: no header at all (a separate root trace) and a
header built once at start-up (the child lands under the wrong span). A fourth shows the queued case, where the
child opens its own root and records a span link to the span that enqueued it. Ids come from a seeded
generator; the header format is W3C Trace Context (Recommendation, 23 November 2021): version, trace-id,
parent-id, trace-flags. Standard library only; nothing touches the network.
"""
import json
import os
import random
import re
import subprocess
import sys

TRACEPARENT = re.compile(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")


def make_traceparent(trace_id, span_id, sampled=True):
    """version 00, the 32-hex trace id, the 16-hex id of the parent span, flags 01 when sampled."""
    return f"00-{trace_id}-{span_id}-{'01' if sampled else '00'}"


def parse_traceparent(header):
    """Return (trace_id, parent_id, sampled), or None for a missing or invalid header."""
    m = TRACEPARENT.match(header or "")
    if not m or m[1] == "ff" or set(m[2]) == {"0"} or set(m[3]) == {"0"}:
        return None
    return m[2], m[3], int(m[4], 16) & 1 == 1


def child(task, seed):
    """The sub-agent process: join the parent's trace if a valid header arrived, else start a new one."""
    rng = random.Random(seed)
    parent = parse_traceparent(os.environ.get("TRACEPARENT"))
    link = parse_traceparent(os.environ.get("TRACELINK"))
    span = {"name": "subagent.run", "span_id": f"{rng.getrandbits(64):016x}", "task": task,
            "trace_id": parent[0] if parent else f"{rng.getrandbits(128):032x}",
            "parent_id": parent[1] if parent else None,
            "links": [{"trace_id": link[0], "span_id": link[1]}] if link else []}
    print(json.dumps(span))


def launch(env_extra, seed):
    env = {k: v for k, v in os.environ.items() if k not in ("TRACEPARENT", "TRACELINK")}
    env.update(env_extra)
    out = subprocess.run([sys.executable, __file__, "--child", "summarise the failing tests", str(seed)],
                         env=env, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main():
    rng = random.Random(21)
    trace_id = f"{rng.getrandbits(128):032x}"
    spans = {"agent.run": f"{rng.getrandbits(64):016x}"}
    for k in (1, 2, 3):
        spans[f"iteration {k}"] = f"{rng.getrandbits(64):016x}"
    by_id = {v: k for k, v in spans.items()}
    at_startup = make_traceparent(trace_id, spans["iteration 1"])   # built once, before the loop started
    print(f"parent trace {trace_id}; the sub-agent is launched from iteration 3, span {spans['iteration 3']}")
    print(f"traceparent sent: {make_traceparent(trace_id, spans['iteration 3'])}")
    cases = [
        ("header built at spawn time", {"TRACEPARENT": make_traceparent(trace_id, spans["iteration 3"])}),
        ("no header sent", {}),
        ("header built at start-up", {"TRACEPARENT": at_startup}),
        ("queued: link, not parent", {"TRACELINK": make_traceparent(trace_id, spans["iteration 3"])}),
    ]
    print(f"{'launch':<28}{'same trace':>11}  child's parent        link")
    for seed, (name, env) in enumerate(cases, 1):
        span = launch(env, seed)
        same = span["trace_id"] == trace_id
        parent = by_id.get(span["parent_id"], "none, a new root") if span["parent_id"] else "none, a new root"
        link = by_id.get(span["links"][0]["span_id"]) if span["links"] else "none"
        print(f"{name:<28}{'yes' if same else 'no':>11}  {parent:<22}{link}")
    bad = ["00-" + "0" * 32 + "-" + spans["iteration 3"] + "-01", "ff-" + trace_id + "-" + spans["iteration 3"] + "-01",
           "00-" + trace_id.upper() + "-" + spans["iteration 3"] + "-01"]
    print("rejected headers (all-zero trace id, version ff, upper-case hex): "
          + ", ".join(str(parse_traceparent(h)) for h in bad))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], int(sys.argv[3]))
    else:
        main()
