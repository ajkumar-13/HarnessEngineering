# Verification loop (Post 11)

A test-driven self-correction loop: **generate → verify → retry to green**. Companion to [Harness Engineering, Post 11 — Verification loops](../../posts/11-verification-loops/index.md).

## Run

```bash
python -m verification_loop     # demo: a mock model converges to a correct is_prime
python -m pytest -q             # offline test suite (no API key, no network)
```

## What it shows

- **`solve(generate, verify, max_attempts=5)`** — the loop. `generate(feedback)` proposes a candidate given the last failure report; `verify(candidate)` returns a `VerifyResult`. Success is silent (the candidate is returned as soon as a check passes); failure is verbose (its `report` is fed back into `generate`).
- **`checks.test_cases(fn_name, cases)`** — build ground truth from ordinary Python: a verifier that runs `(args, expected)` cases against a namespace and reports the first failures (a raised exception is reported, not propagated).
- The **`max_attempts` cap** is the no-progress stop condition (Post 03, exit ④) applied to correction: a fix-it loop with no cap is a doom loop.

`solve` returns a `Solution` carrying `verified`; a caller that must not ship unverified work checks it before using `candidate`.

## What's deliberately left out

- **A real model.** `generate` is a plain callable; swap in an LLM call to make it live.
- **A sandbox.** The demo builds candidates in-process; running *untrusted* generated code belongs behind the sandbox of [Post 14](../../posts/14-permissions-sandboxes/index.md).
- **A non-optional gate.** Enforcing "no exit without a passing check" as deterministic code is [Post 13](../../posts/13-hooks-enforcement/index.md).

MIT licensed.
