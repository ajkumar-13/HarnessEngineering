# 13 - Hooks

The runnable companion to [13 - Hooks and deterministic enforcement: guardrails as code](../../posts/13-hooks-enforcement/index.md). A small hook system in plain Python with no runtime dependencies: a **pre-tool deny-list** that blocks a command before it runs, and a **post-edit check** that runs tests after a Python file changes and reports a failure.

## What is here

| File | What it is |
|------|-----------|
| `src/hook_system/hooks.py` | `Decision` and `ALLOW`, `deny_list()`, `post_edit_tests()`, `HookRegistry` and `gated_call()`. |
| `src/hook_system/__main__.py` | An offline demo, `python -m hook_system`. |
| `tests/test_hooks.py` | Nine tests: the deny-list blocking and allowing, the first block winning, a blocked call never executing, and the post-edit hook reporting, staying clean and ignoring non-Python files. No API key and no network. |

## Quickstart (offline, no API key)

From this directory:

```bash
uv run --extra dev pytest -q      # the nine tests
uv run python -m hook_system      # the demo
```

The demo prints:

```text
'ls -la'             -> ran: bash ls -la
'rm -rf /'           -> blocked: recursive delete of a broad path
'git push --force'   -> blocked: force-push
edit -> ok
edit -> tests failed after editing math_utils.py: assertion failed: BUG marker present
```

## What it shows

- **`deny_list()`** builds a pre-tool hook from five patterns (`rm -rf` on a broad path, a force-push, `DROP TABLE`, a fork bomb, `mkfs`), compiled once and case-insensitively; a match returns a `Decision` that blocks with a reason.
- **`HookRegistry.check_tool`** runs every pre-tool hook in order; the first block wins.
- **`HookRegistry.after_edit`** runs every post-edit hook and collects every problem.
- **`gated_call(registry, tool, args, execute)`** runs the pre-tool hooks, then executes only if allowed. A blocked call never reaches `execute`; its reason is returned as the observation.
- **`post_edit_tests(run_tests)`** is a post-edit hook that runs only for `.py` files and reports a failure: the verification gate of [11 - Verification loops: tests, self-critique, fail-fast](../../posts/11-verification-loops/index.md), made automatic. It reports; it cannot undo the edit.

## Left out on purpose

- **A real sandbox.** The deny-list matches spellings: it blocks `rm -rf /` and lets `rm -fr /` and `rm -rf workspace` through. Bounding what any command can reach is the sandbox of [14 - Permissions, sandboxes, and security: the AI control plane](../../posts/14-permissions-sandboxes/index.md). The post's `snippets/near_miss.py` scores the shipped patterns on eight near misses.
- **Session-start and pre-commit hooks.** The same registry pattern extends to them.
- **An escape hatch.** Production hooks need a named, single-use, logged override; the post's `snippets/override.py` shows one wrapped around this deny-list.

MIT licensed.
