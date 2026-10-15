"""Post 13, Make it run: the plan's lab. A deny rule blocks a destructive command before it runs; a post-edit
test runner only reports a broken edit, which stays on disk.

Run from the series root:  uv run python posts/13-hooks-enforcement/snippets/block_vs_report.py

The hook system is the companion's, imported unchanged from code/13-hooks/src. Everything happens in a temporary
directory made under tempfile and deleted at the end. The executor is a stand-in for a shell: it performs
`rm -rf <dir>` with shutil.rmtree inside the temporary directory, so the demonstration deletes real files on
Windows and Linux alike. The post-edit tests run for real, in a subprocess of the same Python. Standard library only.
"""
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "13-hooks" / "src"))
from hook_system.hooks import HookRegistry, deny_list, gated_call, post_edit_tests  # noqa: E402

COMMAND = "rm -rf workspace"
ADDED_RULE = [(r"\brm\s+-(rf|fr)\s+workspace\b", "recursive delete of the workspace")]


def make_executor(cwd: Path, calls: list):
    """A stand-in shell for the one command this demo sends: rm -rf <dir>, jailed to cwd."""
    def execute(tool: str, args: str) -> str:
        calls.append(args)
        argv = shlex.split(args)
        if argv[:2] == ["rm", "-rf"] and len(argv) == 3:
            shutil.rmtree(cwd / argv[2], ignore_errors=True)
        return f"ran: {tool} {args}"
    return execute


def pre_tool(cwd: Path, registry: HookRegistry) -> tuple[str, bool, int]:
    """Make a workspace with a marker file, send the command through the gate, report what survived."""
    marker = cwd / "workspace" / "marker.txt"
    marker.parent.mkdir(exist_ok=True)
    marker.write_text("still here\n", encoding="utf-8")
    calls: list = []
    out = gated_call(registry, "bash", COMMAND, make_executor(cwd, calls))
    return out, marker.exists(), len(calls)


def run_tests(cwd: Path):
    """The project's test, run in a fresh interpreter against what is on disk now."""
    def run() -> tuple[bool, str]:
        r = subprocess.run([sys.executable, "-B", "-c", "import calc; assert calc.add(2, 2) == 4, 'add(2, 2) != 4'"],
                           cwd=cwd, capture_output=True, text=True)
        last = (r.stderr.strip().splitlines() or [""])[-1]
        return r.returncode == 0, last
    return run


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)

        # Pre-tool: the shipped list blocks only broad paths (/, ~, *), so this command is not on it.
        shipped = HookRegistry().add_pre_tool(deny_list())
        out, kept, calls = pre_tool(cwd, shipped)
        print(f"shipped deny-list:     {COMMAND!r} -> {out}")
        print(f"  executor calls: {calls}; marker file exists afterwards: {kept}")
        assert out.startswith("ran:") and calls == 1 and not kept

        # The lab's deny rule, added as a second pre-tool hook: the first block wins.
        guarded = HookRegistry().add_pre_tool(deny_list()).add_pre_tool(deny_list(ADDED_RULE))
        out, kept, calls = pre_tool(cwd, guarded)
        print(f"with the added rule:   {COMMAND!r} -> {out}")
        print(f"  executor calls: {calls}; marker file exists afterwards: {kept}")
        assert out.startswith("blocked:") and calls == 0 and kept

        # Post-edit: the edit is written first, then the hook runs the tests and reports.
        reports = HookRegistry().add_post_edit(post_edit_tests(run_tests(cwd)))
        broken = "def add(a, b):\n    return a - b\n"
        (cwd / "calc.py").write_text(broken, encoding="utf-8")
        problems = reports.after_edit("calc.py", broken)
        print("post-edit, calc.py written with a bug:")
        print(f"  report: {problems[0]}")
        on_disk = (cwd / "calc.py").read_text(encoding="utf-8") == broken
        print(f"  the broken edit is still on disk: {on_disk}")
        assert len(problems) == 1 and on_disk


if __name__ == "__main__":
    main()
