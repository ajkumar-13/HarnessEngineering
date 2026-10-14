"""Post 10, section 4: the first two teeth as files, with the rule staged for review.

Run from the series root:  uv run python posts/10-continual-learning-ratchet/snippets/propose_rule.py

propose_rule() appends the proposed memory-file line to AGENTS.proposed.md (a person moves accepted
lines into AGENTS.md) and the enforcement check to .checks/enforce.txt. The demo proposes Osmani's
worked example in a temporary directory and prints both files, then shows the live AGENTS.md was
not touched. Standard library only.
"""
import tempfile
from pathlib import Path


def propose_rule(cwd: str | Path, rule: str, why: str, check: str) -> None:
    """Turn a failure into two durable constraints: a memory-file line the model
    will read, and an enforcement check that catches a regression deterministically.

    The rule lands in a staging file; a person moves accepted lines into AGENTS.md.
    ``why`` is the provenance: the failure it came from, with a date or issue id.
    """
    proposed = Path(cwd, "AGENTS.proposed.md")
    with proposed.open("a", encoding="utf-8") as f:      # a person reviews this
        f.write(f"- {rule} [{why}]\n")

    enforce = Path(cwd, ".checks", "enforce.txt")
    enforce.parent.mkdir(parents=True, exist_ok=True)
    with enforce.open("a", encoding="utf-8") as f:       # a hook or reviewer reads this
        f.write(f"{check}\n")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        live = Path(d, "AGENTS.md")
        live.write_text("# Project rules\n- Use `uv add` to add a dependency. [#412, 2026-05-02]\n",
                        encoding="utf-8")
        before = live.read_text(encoding="utf-8")
        propose_rule(d, "Never comment out tests; delete them or fix them.",
                     "#455, 2026-06-08",
                     "pre-commit: fail if the diff adds '.skip(' or 'xit('")
        for name in ("AGENTS.proposed.md", ".checks/enforce.txt"):
            print(f"{name}:")
            print("  " + Path(d, name).read_text(encoding="utf-8").rstrip("\n"))
        print(f"AGENTS.md unchanged: {live.read_text(encoding='utf-8') == before}")
