"""Post 08, section 3: what one 2,000-line build log costs a run, left in the window or offloaded to disk.

Run from the series root:  uv run python posts/08-state-filesystem-git/snippets/offload_cost.py

The log is generated here: 2,000 lines of 50 characters. Its token count uses the illustrative rule of about
four characters to the token; the pointer left in its place is counted the same way. The log is the result of
iteration 3 of a run capped at 12, so, as in post 03's run_cost.py, it is re-sent on every request after that
turn. The rate is $3 per million input tokens, the Claude Sonnet 4.6 input rate post 03 uses (Anthropic's pricing
page, consulted October 2026); output tokens are left out. Standard library only.
"""
LINES, CHARS_PER_LINE, CHARS_PER_TOKEN = 2_000, 50, 4    # the last is an illustrative rule, not a tokenizer
ARRIVES, CAP, RATE = 3, 12, 3.00                         # turn, max_iters, $ per million input tokens

log = "".join(f"[{i:05d}] compiling module_{i % 97:02d}.c ... ok".ljust(CHARS_PER_LINE - 1) + "\n"
              for i in range(LINES))
pointer = "wrote 2,000 lines to scratch/build.log; grep it for errors."


def tokens(text):
    return round(len(text) / CHARS_PER_TOKEN)


def carried(size):
    """Input tokens one tool result adds to the run: re-sent on every request after the turn it arrived."""
    resent = CAP - ARRIVES
    return resent, size * resent


if __name__ == "__main__":
    print(f"log: {LINES:,} lines, {len(log):,} characters, about {tokens(log):,} tokens; "
          f"pointer: {len(pointer)} characters, about {tokens(pointer)} tokens")
    print(f"{'':22}{'tokens':>8}{'requests':>10}{'carried':>10}{'at $3/M':>10}")
    rows = []
    for label, text in (("left in the window", log), ("offloaded, pointer", pointer)):
        resent, total = carried(tokens(text))
        rows.append(total)
        print(f"{label:22}{tokens(text):>8,}{resent:>10}{total:>10,}{total * RATE / 1e6:>10.4f}")
    print(f"ratio: {rows[0] / rows[1]:,.0f} to 1")
