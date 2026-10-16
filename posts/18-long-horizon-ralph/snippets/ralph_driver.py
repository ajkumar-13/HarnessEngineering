"""Post 18, Make it run: a Ralph driver on a three-task spec, with a mock model in a fresh process each iteration.

Run from the series root:  uv run python posts/18-long-horizon-ralph/snippets/ralph_driver.py

Each scenario builds a temporary git repository holding a three-criterion spec (spec/feature_list.json), a
status file the acceptance gate writes (spec/status.json) and a stand-in system prompt (PROMPT.md). The driver
then runs the "agent" once per iteration as a NEW PROCESS (this same file with --agent), so nothing in memory
crosses the reset: the agent re-reads the spec, the status file, its handoff file and the git log, does one
task, commits it and rewrites the handoff. The agent is a deterministic stand-in for a model; a real loop runs
a model there. After each iteration the driver, not the agent, decides:

  the spec's bytes changed            -> stop, spec_moved (the guard's own name; a human must look)
  every criterion's check passes      -> stop, exit (1) completed (the gate ran the checks itself)
  no new commit for stale_cap rounds  -> stop, exit (4) no_progress, defined on commits
  max_iters iterations used           -> stop, exit (2) max_iters

The agent's own claim (the handoff's Done field) is printed beside the gate's verdict and never read for
convergence. Token counts are tiktoken cl100k_base counts of the toy's own text, so they are illustrative.
Standard library plus tiktoken; git and the running interpreter are the only subprocesses.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SPEC, STATUS, HANDOFF = Path("spec/feature_list.json"), Path("spec/status.json"), Path("handoff.md")
FEATURES = [
    {"id": "add", "description": "add(a, b) returns the sum", "check": "from calc import add; assert add(2, 3) == 5"},
    {"id": "sub", "description": "sub(a, b) returns the difference", "check": "from calc import sub; assert sub(5, 3) == 2"},
    {"id": "mul", "description": "mul(a, b) returns the product", "check": "from calc import mul; assert mul(4, 3) == 12"},
]
PROMPT = ("You are one iteration of a long-running build. Read spec/feature_list.json, spec/status.json, "
          "handoff.md and the git log. Pick the first criterion the status file marks failing, implement only "
          "that, commit it, and rewrite handoff.md. Never edit anything under spec/.\n")


GIT_ENV = dict(os.environ, GIT_AUTHOR_DATE="2026-10-16T12:00:00+00:00",   # fixed dates: the same hashes,
               GIT_COMMITTER_DATE="2026-10-16T12:00:00+00:00")           # so the same token counts, every run


def git(repo, *args):
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=GIT_ENV)
    if out.returncode != 0:                       # every git return code is checked (post 08)
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


# --------------------------------------------------------------------------- the agent: one fresh process
def tokens(text):
    import tiktoken
    return len(tiktoken.get_encoding("cl100k_base").encode(text))


def write_atomic(path, text):
    """Post 08's rule: replace in one step, then read it back before it counts as written."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    if path.read_text(encoding="utf-8") != text:
        raise OSError(f"{path} does not hold what was written")


def agent(mode):
    """Everything this function knows, it reads from disk: there is no other way in."""
    repo = Path.cwd()
    frozen = (repo / "PROMPT.md").read_text(encoding="utf-8") + (repo / SPEC).read_text(encoding="utf-8")
    status = json.loads((repo / STATUS).read_text(encoding="utf-8"))
    handoff = (repo / HANDOFF).read_text(encoding="utf-8") if (repo / HANDOFF).exists() else ""
    calc = (repo / "calc.py").read_text(encoding="utf-8")
    volatile = (repo / STATUS).read_text(encoding="utf-8") + handoff + git(repo, "log", "--oneline") + calc
    spec = json.loads((repo / SPEC).read_text(encoding="utf-8"))
    task = next(f for f in spec["features"] if not status[f["id"]])
    funcs = dict(re.findall(r"def (\w+)\(a, b\):\n    return (.+)\n", calc))
    note = ""
    if task["id"] == "mul" and mode in ("moves-goalposts", "stalls"):
        if mode == "moves-goalposts":           # cannot satisfy the criterion, so it edits the criterion
            spec["features"][2]["check"] = "assert True"
            (repo / SPEC).write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
            note = "rewrote the mul check"
        else:
            note = "blocked on mul, no commit"   # gives up this round and commits nothing
    else:
        if task["id"] == "sub" and "sub" not in funcs:
            funcs["sub"] = "a + b"               # first attempt is wrong, and the agent says it is done
        else:
            funcs[task["id"]] = {"add": "a + b", "sub": "a - b", "mul": "a * b"}[task["id"]]
        calc = "".join(f"def {f['id']}(a, b):\n    return {funcs[f['id']]}\n\n"
                       for f in spec["features"] if f["id"] in funcs)
        (repo / "calc.py").write_text(calc, encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", f"{task['id']}: implement")
        note = f"claims {task['id']} done"
    head = git(repo, "rev-parse", "--short", "HEAD")
    done = [f["id"] for f in spec["features"] if status[f["id"]] or (f["id"] == task["id"] and "claims" in note)]
    text = (f"# Handoff\n\n## Spec\nspec/feature_list.json, read-only\n\n## Done\n{', '.join(done) or 'nothing'}\n\n"
            f"## Next\n{'mul, still blocked' if 'blocked' in note else 'the first criterion status.json marks failing'}\n\n"
            f"## State\nbranch main, HEAD {head}\n\n## Decisions\none criterion per iteration\n\n"
            f"## Open questions\n{'mul cannot be met as written' if 'mul' in note else 'none'}\n")
    write_atomic(repo / HANDOFF, text)
    work = calc + text
    print(json.dumps({"note": note, "frozen": tokens(frozen), "volatile": tokens(volatile), "work": tokens(work),
                      "prefix_sha": hashlib.sha256(frozen.encode()).hexdigest()}))


# --------------------------------------------------------------------------- the driver
def new_repo(root):
    repo = Path(root)
    (repo / "spec").mkdir()
    (repo / SPEC).write_text(json.dumps({"features": FEATURES}, indent=2) + "\n", encoding="utf-8")
    (repo / STATUS).write_text(json.dumps({f["id"]: False for f in FEATURES}) + "\n", encoding="utf-8")
    (repo / "PROMPT.md").write_text(PROMPT, encoding="utf-8")
    (repo / "calc.py").write_text("", encoding="utf-8")
    (repo / ".gitignore").write_text("handoff.md\n*.tmp\n__pycache__/\n", encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    for key, value in (("user.name", "ralph-demo"), ("user.email", "ralph@example.invalid"),
                       ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
        git(repo, "config", key, value)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "initialiser: spec, status, prompt")
    return repo


def commits(repo):
    return int(git(repo, "rev-list", "--count", "HEAD"))


def spec_hash(repo):
    return hashlib.sha256((repo / SPEC).read_bytes()).hexdigest()


def gate(repo):
    """The acceptance gate: run every criterion's check in a fresh interpreter, and write the pass bits."""
    spec = json.loads((repo / SPEC).read_text(encoding="utf-8"))
    status = {f["id"]: subprocess.run([sys.executable, "-B", "-c", f["check"]], cwd=repo,
                                      capture_output=True).returncode == 0
              for f in spec["features"]}
    (repo / STATUS).write_text(json.dumps(status) + "\n", encoding="utf-8")
    return status


def ralph(repo, run_agent, *, max_iters=50, stale_cap=3, log=print):
    stale = 0
    for i in range(1, max_iters + 1):
        goalposts, before = spec_hash(repo), commits(repo)
        report = run_agent(repo)                      # a new process: the fresh context
        if spec_hash(repo) != goalposts:
            return i, "spec_moved"                    # the agent changed what done means
        status = gate(repo)                           # the driver runs the checks; the report is not read
        new = commits(repo) - before
        log(i, report, new, status)
        if all(status.values()):
            return i, "completed"                     # exit (1), decided by the gate
        stale = 0 if new else stale + 1
        if stale >= stale_cap:
            return i, "no_progress"                   # exit (4), on commits
    return max_iters, "max_iters"                     # exit (2)


def agent_process(mode):
    def run(repo):
        out = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--agent", mode], cwd=repo,
                             capture_output=True, text=True, check=True)
        return json.loads(out.stdout)
    return run


EXITS = {"completed": "exit (1), completed", "max_iters": "exit (2), max_iters",
         "no_progress": "exit (4), no_progress", "spec_moved": "guard, spec_moved"}


def scenario(mode, *, max_iters=50, quiet=False):
    rows = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        repo = new_repo(tmp)

        def log(i, report, new, status):
            handoff = (repo / HANDOFF).read_text(encoding="utf-8")
            claimed = handoff.split("## Done\n")[1].split("\n")[0]
            rows.append(dict(i=i, new=new, total=commits(repo), passing=sum(status.values()), claimed=claimed,
                             **report))
            if not quiet:
                gate_says = ", ".join(f"{k} {'pass' if v else 'fail'}" for k, v in status.items())
                print(f"  {i:>2}  {report['note']:<25}  +{new} commit  rev-list {commits(repo)}  "
                      f"handoff done: {claimed:<13} gate: {gate_says}")

        it, reason = ralph(repo, agent_process(mode), max_iters=max_iters, log=log)
        if not quiet:
            print(f"  stopped after iteration {it}: {EXITS[reason]}")
        if reason == "spec_moved":
            moved = gate(repo)
            print(f"  the gate run on the moved spec would pass {sum(moved.values())} of {len(moved)}")
    return rows, it, reason


def run_all():
    out = {}
    for title, mode, cap in (("an honest agent, one wrong claim on the way", "honest", 50),
                             ("an agent that cannot do mul and edits its check", "moves-goalposts", 50),
                             ("an agent that cannot do mul and stops committing", "stalls", 50),
                             ("the honest agent under max_iters=3", "honest", 3)):
        print(f"{title} (mode {mode}, max_iters={cap}):")
        out[(mode, cap)] = scenario(mode, max_iters=cap)
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["--agent"]:
        agent(sys.argv[2])
        sys.exit(0)
    results = run_all()
    rows, it, reason = results[("honest", 50)]
    assert (it, reason) == (4, "completed") and [r["new"] for r in rows] == [1, 1, 1, 1]
    assert [r["passing"] for r in rows] == [1, 1, 2, 3] and rows[1]["claimed"] == "add, sub"
    assert len({r["prefix_sha"] for r in rows}) == 1
    assert results[("moves-goalposts", 50)][1:] == (4, "spec_moved")
    assert results[("stalls", 50)][1:] == (6, "no_progress")
    assert results[("honest", 3)][1:] == (3, "max_iters")
    frozen = rows[0]["frozen"]
    single = frozen + sum(r["volatile"] + r["work"] for r in rows)
    print("windows, honest run (tokens: frozen prefix + volatile re-entry -> end of iteration):")
    for r in rows:
        print(f"  {r['i']:>2}  {frozen} + {r['volatile']} = {frozen + r['volatile']} -> "
              f"{frozen + r['volatile'] + r['work']}")
    print(f"frozen prefix byte-identical in every iteration: True ({frozen} tokens)")
    print(f"largest Ralph window: {max(frozen + r['volatile'] + r['work'] for r in rows)} tokens; "
          f"one context carrying all {len(rows)} iterations: {single} tokens")
