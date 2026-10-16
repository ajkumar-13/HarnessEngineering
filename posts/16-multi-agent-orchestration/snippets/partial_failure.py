"""Post 16: one fan-out with failing workers, and what each partial-failure policy does with the hole.

Run from the series root:  uv run python posts/16-multi-agent-orchestration/snippets/partial_failure.py

A lead fans four documents out to four workers. The workers are deterministic stand-ins where a real harness
runs a model: each returns a one-line finding, except that the worker on doc-2 hits a rate limit on its first
attempt (a transient failure a retry clears) and the worker on doc-4 finds its document unreadable (a failure no
retry clears). The same fan-out is run once per policy the post names, each chosen before the fan-out (fail the
run; retry, then degrade with a marker; escalate to a human), and once with no policy, where the lead takes the
branch the code already has and synthesises whatever came back. Standard library only; no network, no disk.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

DOCS = ["doc-1", "doc-2", "doc-3", "doc-4"]
FINDINGS = {"doc-1": "uptime 99.95%", "doc-2": "two incidents", "doc-3": "no incidents", "doc-4": "one outage"}


class Worker:
    """Stands in for a worker agent. Counts attempts, so that a retry can clear a transient failure."""

    def __init__(self):
        self.attempts = {d: 0 for d in DOCS}

    def run(self, doc):
        self.attempts[doc] += 1
        if doc == "doc-2" and self.attempts[doc] == 1:
            raise TimeoutError("rate limited, retry after 2 s")
        if doc == "doc-4":
            raise ValueError("document unreadable: truncated PDF")
        return FINDINGS[doc]


def orchestrate(lead, worker, task, max_workers=4):
    """Fan out independent subtasks, keep the failures visible, then synthesise."""
    subtasks = lead.plan(task)                       # decompose into independent pieces
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pending = {pool.submit(worker.run, st): st for st in subtasks}
        for future in as_completed(pending):         # the block ends when the slowest one does
            subtask = pending[future]
            try:
                results.append({"subtask": subtask, "result": future.result()})
            except Exception as exc:                 # a failed worker is data, not a crash
                failures.append({"subtask": subtask, "error": repr(exc)})
    return lead.synthesise(task, results, failures)  # the hole is an argument, not a silence


def apply_policy(policy, results, failures, retry, gap_note, escalate):
    """Decide what the lead does with a partial result set. Chosen at design time."""
    if not failures:
        return results, None
    if policy == "fail":
        raise RuntimeError(f"{len(failures)} of {len(results) + len(failures)} subtasks failed")
    if policy == "retry_then_degrade":
        recovered, still_failed = retry(failures)
        return results + recovered, gap_note(still_failed)
    if policy == "escalate":
        return results, escalate(failures)
    raise ValueError(f"unknown partial-failure policy {policy!r}")


class Lead:
    """Stands in for the lead agent: a fixed split, and a synthesis that applies the policy it was given."""

    def __init__(self, policy, worker):
        self.policy, self.worker = policy, worker

    def plan(self, task):
        return list(DOCS)

    def retry(self, failed):
        recovered, still = [], []
        for f in failed:                             # one retry each: many worker failures are transient
            try:
                recovered.append({"subtask": f["subtask"], "result": self.worker.run(f["subtask"])})
            except Exception as exc:
                still.append({"subtask": f["subtask"], "error": repr(exc)})
        return recovered, still

    @staticmethod
    def gap_note(still_failed):
        return ("MISSING: " + ", ".join(f["subtask"] for f in still_failed)) if still_failed else None

    @staticmethod
    def escalate(failed):
        return "ESCALATED: " + ", ".join(f["subtask"] for f in failed) + " failed; paused for a human"

    def synthesise(self, task, results, failures):
        if self.policy is None:                      # no policy: the hole is silently averaged over
            kept, note = results, None
        else:
            kept, note = apply_policy(self.policy, results, failures, self.retry, self.gap_note, self.escalate)
        answer = "; ".join(f"{r['subtask']}: {r['result']}" for r in sorted(kept, key=lambda r: r["subtask"]))
        return len(kept), answer, note


def main():
    task = "Summarise the four quarterly service reports."
    print(f"{len(DOCS)} subtasks; doc-2 fails once (rate limit), doc-4 fails every time (unreadable)")
    for policy in (None, "fail", "retry_then_degrade", "escalate"):
        worker = Worker()
        label = policy or "no policy"
        try:
            kept, answer, note = orchestrate(Lead(policy, worker), worker, task)
        except RuntimeError as exc:
            print(f"{label:19} raised RuntimeError: {exc}")
            continue
        print(f"{label:19} {kept} of {len(DOCS)} kept; note: {note}")
        print(f"{'':19} answer: {answer}")
        if policy is None:
            print(f"{'':19} nothing in the answer says that {len(DOCS) - kept} of the {len(DOCS)} documents are "
                  "missing")
        else:
            print(f"{'':19} worker attempts: " + ", ".join(f"{d} {n}" for d, n in worker.attempts.items()))


if __name__ == "__main__":
    main()
