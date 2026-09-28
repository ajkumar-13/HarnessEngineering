# Companion code README template

Every runnable companion lives at `code/NN-name/` and ships the same five things:

```
code/NN-name/
├── README.md
├── pyproject.toml
├── src/PACKAGE/          # the package the post names
└── tests/                # offline, no API key, no network
```

Companions in this series are **offline by design**. A scripted model and an injected
runner stand in for the network, so `python -m pytest -q` passes on a machine with no
keys. That is also the pedagogical point: you are testing *the harness*, and the model
is not the part under test.

---

## The shape

````markdown
# NN — <title matching the post's subject>

Companion code for **Harness Engineering, Post NN — "<post title>."**

One paragraph: what this code is and what shape of system it implements.

| Primitive | Module | From |
|-----------|--------|------|
| What it does, in the series' vocabulary | `module.py` | Post NN |

The whole thing is **offline by design**: <one sentence on how, and what to swap in
to make it live>.

## The idea

Two or three paragraphs, or a small ASCII diagram, explaining the mechanism the post
argues for. This is the part a reader compares against the post's prose, so every
identifier named here must exist.

## Quickstart

```bash
cd code/NN-name
python -m pytest -q          # offline; no API key needed
python -m PACKAGE            # the demo
```

To run it live:

```bash
pip install -e .
export ANTHROPIC_API_KEY=...
python -m PACKAGE --live
```

## Layout

```
src/PACKAGE/
├── __init__.py
├── __main__.py       # the demo
└── <module>.py       # one line each on what it holds
tests/
└── test_<name>.py    # N tests
```

## What the tests pin down

- One bullet per test group, saying **which claim in the post** it protects.
- Where a test cannot see something (a race, a real subprocess, a live API), say so
  explicitly. A suite that structurally cannot observe a property must not be
  described as proving it.

## What this deliberately does not do

The simplifications, and which post covers the real version.
````

---

## Rules

1. **Every identifier the post names must exist here, spelled the same way.** Post and
   companion drift is the most common defect found in review: wrong filenames, wrong
   class names, wrong test counts.
2. **State the test count, and keep it current.** It appears in the post, in this
   README, and in `README.md` at the repo root. All three must agree with
   `python -m pytest -q`.
3. **Never claim a suite "proves" an invariant it cannot observe.** A single-threaded
   test cannot prove a concurrency property; a test that injects a fake runner cannot
   prove anything about the real executor. Both mistakes shipped in this series and
   both hid real bugs.
4. **A test for a fixed bug must fail against the old code.** Check it, do not assume
   it. Revert the fix, watch it go red, restore the fix.
5. **No network, no API key, no clock, no randomness** in the default test path.
6. Mark the companion live in the root `README.md` companions table and in its
   "Live now" line with the passing test count.
