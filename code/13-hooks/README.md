# Hooks (Post 13)

A small hook system: a **pre-tool deny-list** and **post-edit checks** that gate an agent run. Companion to [Harness Engineering, Post 13 — Hooks & deterministic enforcement](../../posts/13-hooks-enforcement/index.md).

## Run

```bash
python -m hook_system    # demo: blocks rm -rf and a force-push, catches a broken edit
python -m pytest -q      # offline test suite (no API key, no network)
```

## What it shows

- **`deny_list()`** — a pre-tool hook that blocks a class of dangerous command (`rm -rf`, force-push, `DROP TABLE`, fork bomb, `mkfs`) before it runs.
- **`HookRegistry.check_tool`** — runs every pre-tool hook; the first block wins (fail-closed on a match).
- **`gated_call(registry, tool, args, execute)`** — runs the hooks, then executes only if allowed. A blocked call never reaches `execute`.
- **`post_edit_tests(run_tests)`** — a post-edit hook that runs tests after a `.py` file changes and reports a failure: the verification loop of [Post 11](../../posts/11-verification-loops/index.md), made automatic and non-optional.

## What's deliberately left out

- **A real sandbox.** A deny-list stops known-dangerous commands; *bounding* what any command can reach is the sandbox of [Post 14](../../posts/14-permissions-sandboxes/index.md).
- **Session-start and pre-commit hooks.** The same registry pattern extends to them.
- **An escape hatch.** Production hooks need a sanctioned, logged way to allow a reviewed exception.

MIT licensed.
