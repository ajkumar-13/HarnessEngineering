"""Post 16: a read fan-out and a write fan-out, each run by one agent and by a lead with four workers.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/snippets/fan_out.py

Every agent here is a deterministic stand-in where a real harness calls a model: the workers parse their slice
with plain code and the lead merges with plain code, so the answers are exact and the run is repeatable. What the
snippet measures is what each role is shown. Every prompt is assembled as text and counted with tiktoken's
o200k_base encoding (Claude's tokenizer is not public), and priced at the Claude Sonnet 4.6 rates on Anthropic's
pricing and prompt caching pages, consulted October 2026: $3 per million input tokens, $15 per million output
tokens, a five-minute cache write at 1.25 times the input rate and a cache read at 0.1 times. Only the shared
prefix (the system prompt and the tool schemas, byte-identical in every role) is cached, the lead's first call
writes it, and every later call reads it; that ordering matters, because a cache entry becomes available only
after the first response begins, so workers dispatched at the same instant as the writer would all miss.
Wall-clock comes from time.perf_counter over a simulated latency per call (illustrative seconds, slept at
1/100 scale), so the parallel run really waits for its slowest worker (the time spent counting tokens is subtracted);
the measured time must agree with the
latency model within 15 per cent, which still tells the maximum of the workers from their sum. All counts are illustrative.
Apart from tiktoken fetching its encoding file once and caching it, nothing touches the network or the disk.
"""
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor

import tiktoken

ENC = tiktoken.get_encoding("o200k_base")
RATE_IN, RATE_OUT = 3.00, 15.00            # dollars per million tokens, Claude Sonnet 4.6
CACHE_WRITE, CACHE_READ = 1.25, 0.10       # multiples of the input rate, five-minute tier
MIN_CACHEABLE = 1024                       # Sonnet 4.6: shorter prefixes are not cached at all
SCALE = 100                                # simulated seconds are slept at 1/100 scale
PLAN_S, MERGE_S, RECONCILE_S = 5, 5, 15    # illustrative seconds for the lead's calls
WORKER_S = [10, 10, 10, 90]                # illustrative seconds per worker; one slice is slow


def tokens(text):
    return len(ENC.encode(text))


# ---- the shared prefix: the same bytes at the top of every role's prompt -----------------------------------

def tool(name, purpose, **params):
    props = {p: {"type": t, "description": d} for p, (t, d) in params.items()}
    return {"name": name, "description": purpose,
            "input_schema": {"type": "object", "properties": props, "required": sorted(props)}}


TOOLS = [
    tool("read_file", "Read a UTF-8 text file from the working tree and return its contents. Paths are relative "
         "to the repository root; a path outside it is refused before the read.",
         path=("string", "File path relative to the repository root."),
         max_bytes=("integer", "Stop after this many bytes; the default reads the whole file.")),
    tool("write_file", "Create or replace a text file in the working tree. The previous contents are kept in the "
         "checkpoint, so a write can be rolled back; files outside the working tree are refused.",
         path=("string", "File path relative to the repository root."),
         content=("string", "The complete new contents of the file.")),
    tool("edit_file", "Replace one exact occurrence of a string in a file. Fails if the string occurs zero times "
         "or more than once, so an edit never lands in the wrong place.",
         path=("string", "File path relative to the repository root."),
         old=("string", "The exact text to replace, including whitespace."),
         new=("string", "The replacement text.")),
    tool("list_dir", "List the entries of a directory with their sizes, sorted by name.",
         path=("string", "Directory path relative to the repository root.")),
    tool("search", "Search the working tree for a regular expression and return matching lines with their file "
         "and line number, at most 200 matches.",
         pattern=("string", "A Python regular expression."),
         glob=("string", "Restrict the search to paths matching this glob.")),
    tool("run_tests", "Run the project's test suite, or one test file, and return the summary line and the first "
         "failure's report. Times out after 300 seconds.",
         target=("string", "A test file or directory; empty runs everything.")),
    tool("fetch_doc", "Fetch one page of the project's internal documentation by its identifier and return it "
         "as plain text.",
         doc_id=("string", "The documentation page identifier.")),
    tool("report", "Return the final structured result of this task to the caller. Call it exactly once, last.",
         result=("object", "The result, in the shape the task asks for."),
         checked=("array", "What was actually checked to produce the result.")),
]
SYSTEM = (
    "You are an engineering agent working inside a harness. Work only through the tools listed below. Read "
    "before you write; prefer the smallest change that satisfies the task; never edit files outside the "
    "working tree; run the tests after any change to code. When the task asks for a structured result, return "
    "it through the report tool exactly once, together with the list of what you actually checked, because the "
    "caller weighs your result by that list. If something blocks the task, report the blocker instead of "
    "guessing. Follow the project's conventions document whenever it is provided; where it is silent, choose "
    "the option a reviewer would find least surprising and say that you chose it.\n\n"
    "Conventions for every tool call: paths are relative to the repository root; text is UTF-8; a tool error "
    "is an observation, not a reason to stop; a repeated identical call is a sign to change approach.\n"
)
PREFIX = SYSTEM + "\nTools:\n" + json.dumps(TOOLS, indent=2) + "\n"


# ---- the read task: count error codes in four service logs -------------------------------------------------

SERVICES = ["api", "auth", "billing", "search"]
LOG_LINES = [60, 60, 60, 240]              # the search log is four times longer: the slow worker


def make_log(service, n, seed):
    rng = random.Random(seed)
    lines = []
    for i in range(n):
        stamp = f"2026-10-16T08:{i // 60:02d}:{i % 60:02d}Z"
        if rng.random() < 0.15:
            code = rng.choice(["E101", "E204", "E307", "E410"])
            lines.append(f"{stamp} {service} ERROR {code} request {rng.randrange(10_000):04d} failed upstream")
        else:
            lines.append(f"{stamp} {service} INFO request {rng.randrange(10_000):04d} served in "
                         f"{rng.randrange(5, 400)} ms")
    return "\n".join(lines) + "\n"


LOGS = {s: make_log(s, n, k) for k, (s, n) in enumerate(zip(SERVICES, LOG_LINES))}
READ_TASK = "Count the error codes in the four service logs and report the totals per code and per service."


def count_errors(text):
    counts = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) > 3 and parts[2] == "ERROR":
            counts[parts[3]] = counts.get(parts[3], 0) + 1
    return dict(sorted(counts.items()))


def read_worker(service):
    """One worker, one slice: the structured result it returns, and what it checked."""
    result = {"service": service, "errors": count_errors(LOGS[service]),
              "checked": [f"{LOG_LINES[SERVICES.index(service)]} lines of logs/{service}.log"]}
    return json.dumps(result)


def read_merge(results):
    """The lead's merge: sums per code. Read results never contradict each other, so nothing to reconcile."""
    totals, per_service = {}, {}
    for r in map(json.loads, results):
        per_service[r["service"]] = sum(r["errors"].values())
        for code, n in r["errors"].items():
            totals[code] = totals.get(code, 0) + n
    return {"totals": dict(sorted(totals.items())), "per_service": per_service}, 0


def read_single():
    """One agent, one pass over all four logs."""
    whole = "".join(LOGS.values())
    per_service = {s: sum(count_errors(LOGS[s]).values()) for s in SERVICES}
    return {"totals": count_errors(whole), "per_service": per_service}


# ---- the write task: four features added to one shared settings file ---------------------------------------

CONVENTIONS = (
    "# Service settings conventions\n\n"
    + "".join(f"- Rule {i}: settings for the {f} feature live in the [{f}] table; every key carries a comment "
              f"naming its unit; a value that another feature also needs is defined once, in [shared], and "
              f"referenced, never copied.\n" for i, f in enumerate(
                  ["retry", "http", "logging", "cache", "auth", "metrics", "queue", "search"] * 4, 1))
)
FEATURES = ["retry", "http", "logging", "cache"]
WRITE_TASK = "Add retry, http, logging and cache settings to settings.toml, following the conventions document."
# What each feature needs, as (key, concept). A worker writes its own keys plus the shared ones it needs; the
# value it picks for a shared concept is its own implicit decision, made without seeing the other workers.
NEEDS = {
    "retry":   [("retry.attempts", "retry-count"), ("shared.timeout", "request-timeout")],
    "http":    [("http.pool_size", "pool"), ("shared.timeout", "request-timeout"),
                ("http.session_ttl_s", "session-lifetime")],
    "logging": [("logging.level", "log-level"), ("shared.date_format", "date-format")],
    "cache":   [("cache.size_mb", "cache-size"), ("shared.date_format", "date-format"),
                ("cache.session_minutes", "session-lifetime")],
}
CHOICES = {  # the value each worker would pick on its own, per concept
    "retry":   {"retry-count": "3", "request-timeout": '"30s"'},
    "http":    {"pool": "16", "request-timeout": "10", "session-lifetime": "3600"},
    "logging": {"log-level": '"info"', "date-format": '"iso8601"'},
    "cache":   {"cache-size": "256", "date-format": '"%d/%m/%Y"', "session-lifetime": "30"},
}
SECONDS_PER = {"session-lifetime": {"http.session_ttl_s": 1, "cache.session_minutes": 60}}


def write_worker(feature):
    """One worker: its edits to the shared file, as key = value lines with the concept each one encodes."""
    edits = [{"key": k, "value": CHOICES[feature][c], "concept": c} for k, c in NEEDS[feature]]
    return json.dumps({"feature": feature, "edits": edits, "checked": ["conventions.md", "settings.toml"]})


def write_merge(results):
    """The lead's key-level merge. Two workers writing one key with different values is a conflict the merge
    sees; two keys that encode one concept with different meanings merge cleanly, and only a reader who knows
    the concept can tell. The snippet knows, because each edit carries its concept."""
    merged, conflicts = {}, []
    for r in map(json.loads, results):
        for e in r["edits"]:
            if e["key"] in merged and merged[e["key"]] != e["value"]:
                conflicts.append(e["key"])
            merged.setdefault(e["key"], e["value"])
    by_concept = {}
    for r in map(json.loads, results):
        for e in r["edits"]:
            by_concept.setdefault(e["concept"], set()).add(e["key"])
    silent = []
    for concept, keys in sorted(by_concept.items()):
        if len(keys) > 1:
            seconds = {int(merged[k]) * SECONDS_PER[concept][k] for k in keys}
            if len(seconds) > 1:
                silent.append(concept)
    return merged, conflicts, silent


def write_single():
    """One agent decides each concept once, writes it once and reuses it, so nothing can disagree."""
    one_key = {"session-lifetime": "shared.session_ttl_s"}   # the first decision was in seconds
    decided, merged = {}, {}
    for feature in FEATURES:
        for key, concept in NEEDS[feature]:
            decided.setdefault(concept, CHOICES[feature][concept])
            merged.setdefault(one_key.get(concept, key), decided[concept])
    return merged


# ---- the two designs, run and billed ----------------------------------------------------------------------

class Bill:
    def __init__(self):
        self.calls, self.prefix, self.rest, self.out, self.seconds = 0, [], 0, 0, 0.0
        self.counting = 0.0                # real seconds spent in tiktoken, kept out of the wall-clock

    def call(self, prompt_after_prefix, output, seconds):
        began = time.perf_counter()
        self.calls += 1
        self.prefix.append(tokens(PREFIX))
        self.rest += tokens(prompt_after_prefix)
        self.out += tokens(output)
        self.seconds += seconds
        self.counting += time.perf_counter() - began

    def input_tokens(self):
        return sum(self.prefix) + self.rest

    def dollars(self, cached):
        p = self.prefix
        prefix_equiv = p[0] * CACHE_WRITE + sum(p[1:]) * CACHE_READ if cached else sum(p)
        return ((prefix_equiv + self.rest) * RATE_IN + self.out * RATE_OUT) / 1e6, prefix_equiv + self.rest


def wait(seconds):
    time.sleep(seconds / SCALE)


def run_single(task, material, answer):
    bill = Bill()
    started = time.perf_counter()
    for s in WORKER_S:                     # the same four pieces of work, one after another
        wait(s)
    output = json.dumps(answer)
    bill.call(f"Task: {task}\n\n{material}", output, sum(WORKER_S))
    return bill, (time.perf_counter() - started - bill.counting) * SCALE


def run_fan_out(task, slices, worker, merge, framing, shared_material="", reconcile=False):
    bill = Bill()
    started = time.perf_counter()
    plan = json.dumps([f"{task} Your slice: {name}." for name in slices])
    wait(PLAN_S)
    bill.call(f"You are the lead. Split this task into independent subtasks.\nTask: {task}", plan, PLAN_S)
    with ThreadPoolExecutor(max_workers=len(slices)) as pool:
        futures = [pool.submit(lambda n, s: (wait(s), worker(n))[1], name, s)
                   for name, s in zip(slices, WORKER_S)]
        results = [f.result() for f in futures]   # the block ends when the slowest worker does
    for (name, material), result, s in zip(slices.items(), results, WORKER_S):
        bill.call(f"{framing}\nSubtask: {task} Your slice: {name}.\n\n{shared_material}{material}", result, 0)
    bill.seconds += max(WORKER_S)
    merged = merge(results)
    wait(MERGE_S)
    joined = "\n".join(results)
    bill.call(f"You are the lead. Merge the workers' results.\nTask: {task}\n\n{joined}",
              json.dumps(merged[0]), MERGE_S)
    if reconcile:
        _, conflicts, silent = merged
        wait(RECONCILE_S)
        bill.call(f"You are the lead. These keys were written twice with different values: {conflicts}. "
                  f"Reconcile them against the conventions.\n\n{CONVENTIONS}\n{joined}",
                  json.dumps(merged[0]), RECONCILE_S)
    return bill, (time.perf_counter() - started - bill.counting) * SCALE, merged


def row(label, bill, measured, cached=False):
    dollars, equiv = bill.dollars(cached)
    assert abs(measured - bill.seconds) <= 0.15 * bill.seconds, (label, measured, bill.seconds)
    return (label, bill.calls, bill.input_tokens(), round(equiv), bill.out, dollars, bill.seconds)


def report(title, rows):
    print(title)
    print(f"{'design':28}{'calls':>6}{'input':>8}{'billed as':>11}{'output':>8}{'dollars':>10}{'seconds':>9}")
    for label, calls, inp, equiv, out, dollars, seconds in rows:
        print(f"{label:28}{calls:>6}{inp:>8,}{equiv:>11,}{out:>8,}{dollars:>10.4f}{seconds:>9,.0f}")


def main():
    assert tokens(PREFIX) >= MIN_CACHEABLE
    print(f"shared prefix (system prompt and {len(TOOLS)} tool schemas): {tokens(PREFIX):,} tokens")
    print(f"log slices: " + ", ".join(f"{s} {tokens(LOGS[s]):,}" for s in SERVICES) + " tokens")
    print(f"conventions document: {tokens(CONVENTIONS):,} tokens")
    print()

    read_framing = "You are a worker. Read only your slice and return the error counts with the report tool."
    single, t1 = run_single(READ_TASK, "".join(LOGS.values()), read_single())
    multi, t2, (merged, conflicts) = run_fan_out(READ_TASK, LOGS, read_worker, read_merge, read_framing)
    assert merged == read_single() and conflicts == 0
    reads = [row("single agent", single, t1), row("lead + 4 workers, uncached", multi, t2),
             row("lead + 4 workers, cached", multi, t2, cached=True)]
    report("read fan-out: count the error codes in four service logs", reads)
    print(f"merged result equals the single agent's: True; conflicts to reconcile: {conflicts}")
    print()

    files = {f: "" for f in FEATURES}
    write_framing = "You are a worker. Add your feature's settings to settings.toml and report your edits."
    single_w, t3 = run_single(WRITE_TASK, CONVENTIONS, write_single())
    multi_w, t4, (merged_w, conflicts_w, silent_w) = run_fan_out(
        WRITE_TASK, files, write_worker, write_merge, write_framing,
        shared_material=CONVENTIONS + "\nsettings.toml (current):\n[shared]\n", reconcile=True)
    writes = [row("single agent", single_w, t3), row("lead + 4 workers, uncached", multi_w, t4),
              row("lead + 4 workers, cached", multi_w, t4, cached=True)]
    report("write fan-out: four features added to one settings file", writes)
    print(f"keys written twice with different values: {len(conflicts_w)} ({', '.join(conflicts_w)})")
    print(f"concepts encoded twice with different meanings, merged cleanly: {len(silent_w)} "
          f"({', '.join(silent_w)})")
    return reads, writes, (conflicts_w, silent_w)


if __name__ == "__main__":
    main()
