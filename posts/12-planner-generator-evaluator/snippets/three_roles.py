"""Post 12: three roles, one sprint contract, and an evaluator that has no write tools.

Run from the series root:  uv run python posts/12-planner-generator-evaluator/snippets/three_roles.py

A planner, a generator and an evaluator build one small feature, a `parse()` for a two-column export. Each
role is a deterministic stand-in where a real harness calls a model: the planner drafts a fixed list of
criteria, the generator replays three scripted versions of the file, one per attempt, and the judge applies a
fixed rule to the one criterion that needs judgement. The contract is agreed and frozen before the first
attempt; every criterion that code can settle is routed to code (a unit test, a schema check, an annotation
check, a short script), and only the judged one reaches the evaluator. The evaluator's tools come from a
registry that holds no write tool, so its attempt to write the fix is refused by the registry, not by an
instruction. Tokens are counted with tiktoken's o200k_base encoding over the stand-in prompts (Claude's
tokenizer is not public) and priced at $3 and $15 per million input and output tokens, the Claude Sonnet 4.6
rates (Anthropic pricing page, consulted October 2026): the counts and the multiple are illustrative.
Apart from tiktoken fetching its encoding file once and caching it, nothing touches the network or the disk.
"""
import hashlib
import inspect
import re
from dataclasses import dataclass
from types import MappingProxyType

import tiktoken

ENC = tiktoken.get_encoding("o200k_base")
RATE_IN, RATE_OUT = 3.00, 15.00            # dollars per million tokens, Claude Sonnet 4.6
TASK = "Add parse(rows) to parse.py: turn 'name,amount' lines into records, and log the change in CHANGELOG.md."
CHANGELOG = "# Changelog\n\n- 0.1.0: first release\n"
MALFORMED = ["bolt,3", "widget"]           # the second row has one field where two are expected


# ---- the tool registries: what each role is allowed to call --------------------------------------------

class Tools:
    """One role's tools. A call outside the registry is refused before it runs."""

    def __init__(self, role, repo, allowed):
        self.role, self.repo, self.allowed = role, repo, frozenset(allowed)
        self.writes = 0

    def call(self, name, *args):
        if name not in self.allowed:
            raise PermissionError(f"{name} is not in the {self.role}'s registry")
        return getattr(self, "_" + name)(*args)

    def _read_file(self, path):
        return self.repo[path]

    def _write_file(self, path, text):
        self.repo[path] = text
        self.writes += 1


# ---- the contract ------------------------------------------------------------------------------------------

@dataclass
class Criterion:
    number: int
    text: str
    verifier: str                          # who settles it: code of some kind, or the evaluator
    check: object = None                   # check(work) -> (ok, detail); None when the criterion is judged


@dataclass
class Contract:
    criteria: list

    def digest(self):
        """A fingerprint of the agreed text: the same digest on every attempt means nobody moved the bar."""
        text = "\n".join(f"{c.number}. {c.text}" for c in self.criteria)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]

    def render(self):
        return "\n".join(f"{c.number}. {c.text} [{c.verifier}]" for c in self.criteria)


def load(work):
    """Import the generated parse.py into a fresh namespace."""
    ns = {"__name__": "work"}
    exec(work["parse.py"], ns)
    return ns


def error_message(work):
    try:
        load(work)["parse"](MALFORMED)
    except ValueError as exc:
        return str(exc)
    return None


def empty_list(work):
    out = load(work)["parse"]([])
    return out == [], f"parse([]) returned {out!r}"


def names_the_row(work):
    msg = error_message(work)
    return msg is not None and re.search(r"\brow 2\b", msg) is not None, f"the error for row 2 reads {msg!r}"


def matches_schema(work):
    rows = load(work)["parse"](["bolt,3", "nut,12"])
    ok = all(set(r) == {"name", "amount"} and isinstance(r["name"], str)
             and isinstance(r["amount"], int) for r in rows)
    return ok, f"parse returned {rows!r}"


def annotated(work):
    funcs = [f for n, f in load(work).items()
             if inspect.isfunction(f) and f.__module__ == "work" and not n.startswith("_")]
    bare = [f.__name__ for f in funcs
            if "return" not in f.__annotations__
            or any(p not in f.__annotations__ for p in inspect.signature(f).parameters)]
    return not bare, f"unannotated: {', '.join(bare)}"


def one_changelog_line(work):
    added = [line for line in work["CHANGELOG.md"].splitlines()[len(CHANGELOG.splitlines()):] if line.strip()]
    return len(added) == 1, f"{len(added)} new lines in CHANGELOG.md"


def understandable(work):
    """The judge's stand-in rule for criterion 6: the message names the row, what was expected and what was found."""
    msg = error_message(work)
    named = msg is not None and "row 2" in msg
    ok = named and "expected" in msg and "got" in msg
    detail = ("the message names the row and says what was expected and what was found" if ok
              else "the message names the row but not what is wrong with it" if named
              else "the message does not say which row is wrong")
    return ok, named, detail


DRAFT = [
    ("parse([]) returns []", "unit test", empty_list),
    ("a malformed row raises ValueError naming the row number", "unit test", names_the_row),
    ('every row matches {"name": str, "amount": int}', "schema check", matches_schema),
    ("every public function is annotated", "annotation check", annotated),
    ("CHANGELOG.md gains exactly one line", "script", one_changelog_line),
    ("the error a user sees is understandable without the source", "evaluator", None),
    ("the code is clean", "evaluator", None),
]
VAGUE = ("clean", "good", "nice", "elegant")


def plan(task):
    """The planner's stand-in: a fixed draft of numbered criteria for this task."""
    return [Criterion(i, text, verifier, check) for i, (text, verifier, check) in enumerate(DRAFT, 1)]


def review(draft):
    """The evaluator's side of the negotiation: refuse a judged criterion that names nothing observable."""
    kept, refused = [], []
    for c in draft:
        (refused if c.check is None and any(w in c.text for w in VAGUE) else kept).append(c)
    return kept, refused


# ---- the generator: three scripted versions of parse.py, one per attempt ----------------------------------

VERSIONS = [
    '''def parse(rows: list[str]) -> list[dict]:
    out = []
    for line in rows:
        name, amount = line.split(",")
        out.append({"name": name, "amount": amount})
    return out
''',
    '''def parse(rows: list[str]) -> list[dict]:
    out = []
    for i, line in enumerate(rows, 1):
        fields = line.split(",")
        if len(fields) != 2:
            raise ValueError(f"row {i}")
        out.append({"name": fields[0], "amount": int(fields[1])})
    return out
''',
    '''def parse(rows: list[str]) -> list[dict]:
    out = []
    for i, line in enumerate(rows, 1):
        fields = line.split(",")
        if len(fields) != 2:
            raise ValueError(f"row {i}: expected 2 fields, name and amount; got {len(fields)}: {line!r}")
        out.append({"name": fields[0], "amount": int(fields[1])})
    return out
''',
]


# ---- the loop ----------------------------------------------------------------------------------------------

@dataclass
class Verdict:
    """The evaluator's answer: the sibling of post 11's VerifyResult, renamed
    because a judged verdict is an opinion where `ok` is a fact."""

    accepted: bool
    report: str = ""


@dataclass
class Sprint:
    """The outcome of a sprint: the last work, and whether it was accepted."""

    work: object
    attempts: int
    accepted: bool
    report: str = ""


def run_sprint(planner, generator, evaluator, task, *, max_revisions=3):
    """Plan once, then generate and independently evaluate until the contract is met."""
    contract = planner(task)                        # decompose + acceptance criteria, up front
    feedback, work = None, None
    for attempt in range(1, max_revisions + 2):
        work = generator(task, contract, feedback)  # build to the contract, not to "good enough"
        verdict = evaluator(work, contract)         # SEPARATE agent: grades work vs the contract
        if verdict.accepted:
            return Sprint(work, attempt, accepted=True)
        feedback = verdict.report                   # the named failures, handed back to the generator
    return Sprint(work, max_revisions + 1, accepted=False, report=feedback)


def grade(contract, work, evaluator):
    """Settle every criterion the cheapest way it can be settled."""
    failures = []
    for c in contract.criteria:
        if c.check is not None:              # objective: a test, a schema, a script
            ok, detail = c.check(work)
        else:                                # judged: the only ones worth a model call
            ok, detail = evaluator(c, work)
        if not ok:
            failures.append(f"criterion {c.number} unmet: {detail}")
    return Verdict(accepted=not failures, report="\n".join(failures))


# ---- wiring the stand-ins together, and counting what each call would cost ---------------------------------

CALLS = []                                  # (role, prompt, output) for every model call the run makes


def model_call(role, prompt, output):
    CALLS.append((role, prompt, output))
    return output


def main():
    repo = {"parse.py": "", "CHANGELOG.md": CHANGELOG}
    gen_tools = Tools("generator", repo, {"read_file", "write_file"})
    eval_tools = Tools("evaluator", repo, {"read_file"})
    log = []

    def planner(task):
        draft = plan(task)
        model_call("planner", f"Write numbered acceptance criteria for this task.\n{task}",
                   "\n".join(f"{c.number}. {c.text}" for c in draft))
        kept, refused = review(draft)
        model_call("evaluator", "Agree these criteria or refuse any you cannot judge:\n"
                   + "\n".join(f"{c.number}. {c.text}" for c in draft),
                   "\n".join(f"refuse {c.number}: names nothing observable" for c in refused))
        for c in refused:
            print(f"evaluator refuses draft criterion {c.number}, {c.text!r}: names nothing observable")
        contract = Contract(kept)
        print(f"contract frozen before attempt 1: {len(kept)} criteria, digest {contract.digest()}")
        for c in kept:
            print(f"  {c.number}  {c.verifier:<16} {c.text}")
        return contract

    def generator(task, contract, feedback):
        n = len([c for c in CALLS if c[0] == "generator"])
        prompt = "\n\n".join([task, contract.render(), feedback or "", gen_tools.call("read_file", "parse.py")])
        source = model_call("generator", prompt, VERSIONS[n])
        gen_tools.call("write_file", "parse.py", source)
        if gen_tools.call("read_file", "CHANGELOG.md") == CHANGELOG:
            gen_tools.call("write_file", "CHANGELOG.md", CHANGELOG + "- 0.2.0: parse() change for the export\n")
        return MappingProxyType(dict(repo))       # the work as the evaluator will see it: read-only

    def judge(criterion, work):
        prompt = "\n\n".join([criterion.text, eval_tools.call("read_file", "parse.py"), repr(error_message(work))])
        ok, named, detail = understandable(work)
        model_call("evaluator", prompt, ("PASS: " if ok else "NEEDS_WORK: ") + detail)
        if not ok and named:                       # a helpful evaluator reaches for the fix itself
            try:
                eval_tools.call("write_file", "parse.py", VERSIONS[-1])
            except PermissionError as exc:
                log.append(f"evaluator write_file refused: {exc}")
        return ok, detail

    def evaluator(work, contract):
        verdict = grade(contract, work, judge)
        attempt = len([c for c in CALLS if c[0] == "generator"])
        unmet = [line.split(" unmet")[0].split()[-1] for line in verdict.report.splitlines()]
        print(f"attempt {attempt}  {'PASS' if verdict.accepted else 'NEEDS_WORK':<10}  digest {contract.digest()}"
              + (f"  unmet: {', '.join(unmet)}" if unmet else ""))
        for line in verdict.report.splitlines():
            print(f"    {line}")
        for line in log:
            print(f"    {line}")
        log.clear()
        return verdict

    sprint = run_sprint(planner, generator, evaluator, TASK)
    print(f"sprint accepted: {sprint.accepted} after {sprint.attempts} attempts; "
          f"files written: generator {gen_tools.writes}, evaluator {eval_tools.writes}")

    def cost(calls):
        tin = sum(len(ENC.encode(p)) for _, p, _ in calls)
        tout = sum(len(ENC.encode(o)) for _, _, o in calls)
        return len(calls), tin, tout, (tin * RATE_IN + tout * RATE_OUT) / 1e6

    single = [("one agent", "\n\n".join([TASK, CHANGELOG]), VERSIONS[-1] + "- 0.2.0: parse() change\n")]
    print()
    print(f"{'':<12}{'calls':>6}{'input':>8}{'output':>8}{'dollars':>10}")
    rows = [(role, cost([c for c in CALLS if c[0] == role])) for role in ("planner", "generator", "evaluator")]
    rows += [("three roles", cost(CALLS)), ("one agent", cost(single))]
    for name, (n, tin, tout, usd) in rows:
        print(f"{name:<12}{n:>6}{tin:>8,}{tout:>8,}{usd:>10.5f}")
    print(f"multiple: {rows[3][1][3] / rows[4][1][3]:.1f} times one agent's dollars (illustrative)")


if __name__ == "__main__":
    main()
