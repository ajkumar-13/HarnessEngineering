# 11 - Verification loop

The runnable companion to [11 - Verification loops: tests, self-critique, fail-fast](../../posts/11-verification-loops/index.md). A test-driven self-correction loop, generate, verify, retry to green, in plain Python with no runtime dependencies.

## What is here

| File | What it is |
|------|-----------|
| `src/verification_loop/loop.py` | `VerifyResult`, `Solution` and `solve(generate, verify, *, max_attempts=5)`: the loop. |
| `src/verification_loop/checks.py` | `test_cases(fn_name, cases)`: ground truth built from ordinary `(args, expected)` pairs. |
| `src/verification_loop/__main__.py` | An offline demo, `python -m verification_loop`. |
| `tests/` | Nine tests: the loop retrying to green, the report threaded back, the cap, and the verifier reporting rather than raising. No API key and no network. |

## Quickstart (offline, no API key)

From this directory:

```bash
uv run python -m verification_loop     # a scripted model converges to a correct is_prime
uv run --extra dev pytest -q           # the nine tests
```

The demo hands `solve` a scripted model that proposes three `is_prime` implementations (no lower bound, then faster but still no lower bound, then correct) and checks each against seven cases. It prints:

```text
verified after 3 attempt(s)
```

## What it shows

- **`solve(generate, verify, *, max_attempts=5)`** is the loop. `generate(feedback)` proposes a candidate given the last failure report (`None` on the first attempt); `verify(candidate)` returns a `VerifyResult`. Success is silent: the candidate is returned as soon as a check passes. Failure is verbose: its `report` is fed back into `generate`.
- **`test_cases(fn_name, cases)`** builds a verifier from `(args, expected)` cases run against a namespace, and reports every failing case; a candidate that raises is reported, not propagated.
- **The `max_attempts` cap** is exit (2), iteration cap, of [03 - The agent loop: ReAct, control loops, and stopping](../../posts/03-the-agent-loop/index.md) applied to correction: a fix-it loop with no cap is a doom loop. The loop has no exit (4), no progress; the post's `snippets/same_report_exit.py` adds one as a proposal.
- **`solve` returns a `Solution` carrying `verified`** rather than raising when the attempts run out; a caller that must not ship unverified work checks it before using `candidate`.

## Left out on purpose

- **A real model.** `generate` is a plain callable; a call to a large language model (LLM) that reads `feedback` makes it live.
- **A sandbox.** The demo runs candidates in-process; running untrusted generated code belongs behind the sandbox of [14 - Permissions, sandboxes, and security: the AI control plane](../../posts/14-permissions-sandboxes/index.md).
- **A non-optional gate.** Enforcing "no exit without a passing check" as deterministic code is [13 - Hooks and deterministic enforcement: guardrails as code](../../posts/13-hooks-enforcement/index.md).

MIT licensed.
