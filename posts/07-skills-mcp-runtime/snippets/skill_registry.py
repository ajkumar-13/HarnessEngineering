"""A progressive-disclosure skill registry: a catalogue of eight skills, two of them disclosed on demand.

Run from the series root:  uv run python posts/07-skills-mcp-runtime/snippets/skill_registry.py
Standard library only. prefix_cache.py imports SKILLS, BASE_TOOLS, TASKS and the registry from here.
"""
import re
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Skill:
    name: str
    description: str                           # the catalogue line, always resident
    triggers: list[str]                        # words that signal the task needs this skill
    tools: list = field(default_factory=list)  # the tool schemas it exposes (post 06)
    setup: Callable[[], None] = lambda: None   # optional lazy initialisation

class SkillRegistry:
    def __init__(self, base_tools, skills):
        self.base_tools = base_tools
        self.skills = skills
        self.loaded: set[str] = set()

    def catalogue(self) -> list[str]:
        # cheap: one line per skill, never a schema
        return [f"{s.name}: {s.description}" for s in self.skills]

    def matches(self, skill: Skill, task: str) -> bool:
        # word boundaries, not substrings: a "git" trigger must not fire on "legitimate"
        words = set(re.findall(r"[a-z0-9_]+", task.lower()))
        return any(t in words for t in skill.triggers)

    def tools_for(self, task: str) -> list:
        # progressive disclosure: base tools + only the skills this task triggers
        tools = list(self.base_tools)
        for skill in self.skills:
            if self.matches(skill, task):
                if skill.name not in self.loaded:
                    skill.setup()              # runs once, on first activation
                    self.loaded.add(skill.name)
                tools += skill.tools
        return tools                           # only these schemas go to the model

    def disclose(self, task: str) -> list:
        """Schemas for newly triggered skills, to APPEND to the conversation.

        The tools block itself never changes, so the cached prefix survives and
        every already-disclosed skill stays available for the rest of the run.
        """
        new = []
        for skill in self.skills:
            if self.matches(skill, task) and skill.name not in self.loaded:
                skill.setup()
                self.loaded.add(skill.name)
                new += skill.tools
        return new


def tool(name, description, **params):
    """A tool schema in the Anthropic Messages shape; every parameter is a required string."""
    return {"name": name, "description": description,
            "input_schema": {"type": "object",
                             "properties": {p: {"type": "string", "description": d} for p, d in params.items()},
                             "required": list(params)}}


BASE_TOOLS = [
    tool("bash", "Run one shell command in the workspace and return its stdout, stderr and exit code. "
         "Use for listing, searching and running programs; do not use it to edit files.",
         command="The command line to run, exactly as it would be typed."),
    tool("read_file", "Read a text file from the workspace and return its contents with line numbers.",
         path="Path relative to the workspace root."),
    tool("write_file", "Create or overwrite a text file in the workspace with the given contents.",
         path="Path relative to the workspace root.", content="The full new contents of the file."),
]

SKILLS = [
    Skill("pdf", "Fill, flatten and extract fields and tables from PDF files, invoices and forms.",
          ["pdf", "invoice", "form"],
          [tool("pdf_extract", "Extract the text, form fields and tables of a PDF as JSON. Use before "
                "reading any number from an invoice or a form; scanned pages come back as empty text.",
                path="Path of the PDF.", pages="Page range such as 1-3, or all."),
           tool("pdf_fill", "Fill the named form fields of a PDF from a JSON mapping and flatten the result.",
                path="Path of the PDF form.", mapping="JSON object from field name to value.",
                out="Path to write the filled PDF.")]),
    Skill("sql", "Run read-only SQL queries against the orders database and describe its tables.",
          ["sql", "database", "query"],
          [tool("sql_query", "Run one read-only SQL SELECT against the orders database and return at most "
                "200 rows as CSV. Write statements are rejected.", sql="A single SELECT statement."),
           tool("sql_schema", "List the columns, types and keys of one table in the orders database.",
                table="The table name.")]),
    Skill("browser", "Open web pages, read their text and follow links.", ["browser", "page", "url"],
          [tool("open_page", "Fetch a URL and return its readable text.", url="An absolute http or https URL."),
           tool("find_links", "List the links on the last opened page that match a phrase.",
                phrase="Text to look for in the link.")]),
    Skill("email", "Search the inbox, read messages and draft replies.", ["email", "inbox", "reply"],
          [tool("search_mail", "Search the inbox and return message ids, senders and subjects.",
                query="Search words."),
           tool("draft_reply", "Draft a reply to one message; drafts are never sent automatically.",
                message_id="The id of the message.", body="The reply text.")]),
    Skill("git", "Inspect history, diffs and branches of the repository.", ["git", "commit", "branch"],
          [tool("git_log", "Show recent commits touching a path.", path="A path in the repository."),
           tool("git_diff", "Show the diff between two revisions.", base="Base revision.", head="Head revision.")]),
    Skill("image", "Resize, crop and describe images.", ["image", "png", "photo"],
          [tool("image_resize", "Resize an image to the given width, keeping its aspect ratio.",
                path="Path of the image.", width="Width in pixels.")]),
    Skill("calendar", "Find free slots and create meetings.", ["calendar", "meeting"],
          [tool("free_slots", "List free slots for the given people on a date.",
                people="Comma-separated email addresses.", date="An ISO date.")]),
    Skill("translate", "Translate text between languages.", ["translate", "french", "german"],
          [tool("translate_text", "Translate text into the target language.", text="The text.",
                target="Target language code such as fr.")]),
]

TASKS = [
    "List the files in the reports folder.",
    "Extract the totals from invoice-march.pdf.",
    "Write the totals to totals.txt.",
    "Query the orders database for March.",
    "Compare the two sets of totals.",
    "Write a short summary to summary.txt.",
]


def names(tools):
    return ", ".join(t["name"] for t in tools) or "-"


if __name__ == "__main__":
    reg = SkillRegistry(BASE_TOOLS, SKILLS)
    print(f"catalogue: {len(reg.catalogue())} skills, one line each; base tools: {names(BASE_TOOLS)}")
    print()
    print(f"{'turn':>4}  {'task':<43}  {'swap: tools_for() sends':<31}  append: disclose() adds")
    swap, append = SkillRegistry(BASE_TOOLS, SKILLS), SkillRegistry(BASE_TOOLS, SKILLS)
    for turn, task in enumerate(TASKS, 1):
        sent = [t for t in swap.tools_for(task) if t not in BASE_TOOLS]
        new = append.disclose(task)
        print(f"{turn:>4}  {task:<43}  {'base + ' + names(sent):<31}  {names(new)}")
    print(f"loaded after the run: {', '.join(sorted(append.loaded))}; still dormant: "
          f"{len(SKILLS) - len(append.loaded)} of {len(SKILLS)}")
    print()
    task = "Check that the digital signature is legitimate."
    git = next(s for s in SKILLS if s.name == "git")
    naive = any(t in task.lower() for t in git.triggers)
    print(f"{task!r}: substring match fires git: {naive}; word match fires git: {reg.matches(git, task)}")
