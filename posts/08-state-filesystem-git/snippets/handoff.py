"""Post 08, sections 6 and 7: a handoff file that survives a killed session, written so it cannot tear.

Run from the series root:  uv run python posts/08-state-filesystem-git/snippets/handoff.py

Session 1 works a four-step task in a temporary git repository, checkpoints after two verified steps, writes
the handoff, then commits a bad third step on its own say-so and is killed. Every object it held is gone.
Session 2 receives only the directory: it reads the handoff, finds that HEAD does not match the checkpoint the
handoff names, rolls the bad commit back, and resumes at the step the Next field names. A last part kills a
write half-way, once with a plain write and once with the atomic one. Uses git_checkpoint.py beside it.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_checkpoint import _git, checkpoint, new_repo, rollback, write  # noqa: E402

def write_atomic(path: Path, text: str) -> None:
    """Replace `path` in one step, so a reader never sees a half-written file."""
    tmp = path.with_suffix(path.suffix + ".tmp")   # same directory, same filesystem
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)                          # atomic within one filesystem
    if path.read_text(encoding="utf-8") != text:   # confirm the effect, do not infer it
        raise OSError(f"{path} does not hold what was written")

def write_handoff(cwd, *, spec, done, next_up, state) -> None:
    write_atomic(Path(cwd, "handoff.md"),
                 f"# Handoff\n\n## Spec\n{spec}\n\n## Done\n{done}\n\n"
                 f"## Next\n{next_up}\n\n## State\n{state}\n")

def read_handoff(cwd):
    """The handoff, or None when there is none: the caller must tell those apart."""
    path = Path(cwd, "handoff.md")
    return path.read_text(encoding="utf-8") if path.exists() else None


SPEC = "Parse the vendor export into rows, one object per line item."
STEPS = ["header detection", "type coercion", "multiline quoted fields", "negative amounts"]


class Killed(Exception):
    """The process dies here: nothing after this point runs, and nothing in memory survives."""


def do_step(cwd, step, broken=False):
    """The model's work on one step: append one function to src/parse.py (a broken one if told to)."""
    body = "    raise NotImplementedError\n" if broken else "    return line\n"
    src = Path(cwd, "src/parse.py").read_text(encoding="utf-8")
    write(cwd, "src/parse.py", src + f"\ndef {step.replace(' ', '_')}(line):\n{body}")


def sections(text):
    """{'Spec': ..., 'Done': ..., 'Next': ..., 'State': ...} from the handoff's ## headings."""
    parts = [p.split("\n", 1) for p in text.split("\n## ")[1:]]
    return {head.strip(): body.strip() for head, body in parts}


def session_one(cwd):
    new_repo(cwd)
    checkpoint(cwd, "scaffold")
    for step in STEPS[:2]:
        do_step(cwd, step)
    ref = checkpoint(cwd, "steps 1-2 verified")
    write_handoff(cwd, spec=SPEC, done="; ".join(STEPS[:2]) + ". 2 of 4 steps verified.",
                  next_up="; ".join(STEPS[2:]), state=f"branch main, last checkpoint {ref[:7]}")
    print(f"session 1: checkpoint {ref[:7]} after 2 of 4 steps, handoff written")
    do_step(cwd, STEPS[2], broken=True)
    bad = checkpoint(cwd, "step 3, unverified")
    print(f"session 1: committed {bad[:7]} on its own say-so, then killed")
    raise Killed


def session_two(cwd):
    text = read_handoff(cwd)
    if text is None:
        print("session 2: no handoff, starting fresh on purpose")
        return
    fields = sections(text)
    named = fields["State"].rsplit(" ", 1)[1]
    head = _git("rev-parse", "--short=7", "HEAD", cwd=cwd).stdout.strip()
    print(f"session 2: handoff names {named}, HEAD is {head}")
    if head != named:
        rollback(cwd, named)
        head = _git("rev-parse", "--short=7", "HEAD", cwd=cwd).stdout.strip()
        print(f"session 2: tree does not match the handoff; rolled back to {head}")
    todo = fields["Next"].split("; ")
    print(f"session 2: resumes at step {STEPS.index(todo[0]) + 1}, {todo[0]}")
    for step in todo:
        do_step(cwd, step)
    ref = checkpoint(cwd, "steps 3-4 verified")
    write_handoff(cwd, spec=fields["Spec"], done="all four steps. 4 of 4 steps verified.",
                  next_up="none", state=f"branch main, last checkpoint {ref[:7]}")
    broken = "NotImplementedError" in Path(cwd, "src/parse.py").read_text(encoding="utf-8")
    print(f"session 2: checkpoint {ref[:7]}, 4 of 4 steps, broken step left in the tree: {broken}")


def torn_writes(cwd):
    """Kill a rewrite of the handoff half-way: a plain write, then the atomic one."""
    old = "# Handoff\n\n" + "\n".join(f"## {h}\nold" for h in ("Spec", "Done", "Next", "State")) + "\n"
    new = old.replace("old", "new")
    path = Path(cwd, "handoff.md")
    path.write_text(old, encoding="utf-8")
    with path.open("w", encoding="utf-8") as f:     # what write_text does: truncate, then write
        f.write(new[:len(new) // 2])                 # the process dies half-way through
    left = path.read_text(encoding="utf-8")
    print(f"plain write killed:  {len(left)} of {len(new)} characters, a torn file")

    path.write_text(old, encoding="utf-8")
    replace = os.replace
    def die(*args):
        raise Killed
    os.replace = die                                 # the process dies between the two steps
    try:
        write_atomic(path, new)
    except Killed:
        pass
    finally:
        os.replace = replace
    left = path.read_text(encoding="utf-8")
    print(f"atomic write killed: {len(left)} of {len(old)} characters, the old file whole: {left == old}")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        try:
            session_one(tmp)
        except Killed:
            pass
        session_two(tmp)
    with tempfile.TemporaryDirectory() as tmp:
        torn_writes(tmp)
