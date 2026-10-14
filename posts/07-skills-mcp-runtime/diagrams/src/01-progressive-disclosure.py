"""Post 07, hero (sections 3 and 6): one six-turn run, two skills disclosed on demand and appended.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/diagrams/src/01-progressive-disclosure.py
Writes posts/07-skills-mcp-runtime/diagrams/01-progressive-disclosure.svg.
A section 4 timeline of hrn_fig_design.md: turns left to right; the request drawn top to bottom in the order the
provider renders it (tools, system, messages); state green for the skills that are loaded; the base tools are act
orange. Everything is computed by the post's snippets: which skill loads on which turn comes from
SkillRegistry.disclose() over TASKS (snippets/skill_registry.py), and the tokens sent and reused per turn from
run("append") in snippets/prefix_cache.py, whose counts are illustrative (tiktoken o200k_base as a stand-in).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\admin\Desktop\series-standard\tools")
POST = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(POST / "snippets"))
from figkit import Box, Figure  # noqa: E402
from skill_registry import BASE_TOOLS, SKILLS, TASKS, SkillRegistry  # noqa: E402
from prefix_cache import run  # noqa: E402

BODY = (POST / "index.md").read_text(encoding="utf-8")

# which skill each turn discloses, from the registry itself
reg = SkillRegistry(BASE_TOOLS, SKILLS)
disclosed = {}
for turn, task in enumerate(TASKS, 1):
    for t in reg.disclose(task):
        disclosed.setdefault(turn, []).append(t["name"])
assert disclosed == {2: ["pdf_extract", "pdf_fill"], 4: ["sql_query", "sql_schema"]}, disclosed
assert sorted(reg.loaded) == ["pdf", "sql"] and len(SKILLS) == 8
assert [t["name"] for t in BASE_TOOLS] == ["bash", "read_file", "write_file"]
rows = run("append")
assert rows == [(405, 0), (667, 405), (693, 667), (861, 693), (885, 861), (910, 885)], rows

# the short task words under each turn, each a word of that turn's task
WORDS = ["reports", "invoice PDF", "totals.txt", "database", "compare", "summary"]
for w, task in zip(WORDS, TASKS):
    assert all(part.lower() in task.lower() for part in w.split()), (w, task)
for phrase in ("eight skills, dormant, one line each", "the harness loads the `pdf` skill",
               "a task about the orders database loads `sql`", "still dormant: 6 of 8"):
    assert phrase in BODY, phrase

fig = Figure(
    "01-progressive-disclosure", "Skills load when a task asks, and stay appended",
    "A timeline of six turns of one run. Rows show the request in the order it is rendered. The tools block holds "
    "bash, read_file and write_file on every turn; the system prompt holds the catalogue of 8 skills, one line each. "
    "Under messages, the pdf skill's schemas pdf_extract and pdf_fill are appended on turn 2, when the task names an "
    "invoice PDF, and stay to turn 6; the sql skill's sql_query and sql_schema are appended on turn 4, when the task "
    "names the database. Tokens sent per turn: 405, 667, 693, 861, 885, 910; reused from the cache: 0, 405, 667, "
    "693, 861, 885. Below, the 8 skills on disk, pdf and sql loaded, 6 dormant. Illustrative counts.",
    subtitle="One run of snippets/skill_registry.py; tokens from prefix_cache.py (illustrative counts).",
    data_w=True)

X0, CW = 240, 112                      # first turn column and column width
def col(k):                            # Box of turn k's column (1-based) across a row
    return X0 + CW * (k - 1)

# turn headings and task words
for k, word in enumerate(WORDS, 1):
    cx = col(k) + CW // 2
    fig.text(cx, 124, f"turn {k}", "head", anchor="middle")
    fig.text(cx, 144, word, "note", anchor="middle")

# tokens sent and reused, per turn
fig.text(40, 172, "tokens sent", "note")
fig.text(40, 192, "reused from cache", "note")
for k, (sent, reused) in enumerate(rows, 1):
    cx = col(k) + CW // 2
    fig.text(cx, 172, f"{sent:,}", "label", anchor="middle")
    fig.text(cx, 192, f"{reused:,}", "label", anchor="middle", color="state")

# the request, top to bottom: tools, system, messages
RIGHT = col(7)
fig.text(40, 232, "tools block", "label")
fig.card(X0, 208, RIGHT - X0, 36, color="act")
fig.text((X0 + RIGHT) // 2, 232, "bash, read_file, write_file", "code", anchor="middle")
fig.text(40, 276, "system prompt", "label")
fig.card(X0, 252, RIGHT - X0, 36)
fig.text((X0 + RIGHT) // 2, 276, "catalogue: 8 skills, one line each", "label", anchor="middle")
fig.text(40, 320, "messages", "label")
BANDS = {2: (296, "pdf_extract, pdf_fill"), 4: (340, "sql_query, sql_schema")}
for turn, (y, names) in BANDS.items():
    assert names.split(", ") == disclosed[turn]
    fig.card(col(turn), y, RIGHT - col(turn), 36, color="state")
    fig.text((col(turn) + RIGHT) // 2, y + 24, names, "code", anchor="middle")

# the catalogue on disk; pdf and sql sit under the turns that load them
ORDER = ["browser", "email", "git", "pdf", "image", "sql", "calendar", "translate"]
assert sorted(ORDER) == sorted(s.name for s in SKILLS)
fig.text(40, 408, "on disk", "label")
for i, name in enumerate(ORDER):
    x = 40 + 108 * i
    loaded = name in reg.loaded
    fig.card(x, 420, 96, 36, color="state" if loaded else None)
    fig.text(x + 48, 444, name, "label" if loaded else "note", anchor="middle")
for name, turn, top in (("pdf", 2, 332), ("sql", 4, 376)):
    cx = 40 + 108 * ORDER.index(name) + 48
    assert col(turn) < cx < RIGHT
    fig.arrow((cx, 420), (cx, top), color="state")

fig.caption("Disclosed schemas join the end of the request, so its front never changes and stays cached.")
fig.write()
