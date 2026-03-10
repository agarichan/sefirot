"""CLI entry point for sefirot."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click


def _find_root() -> Path:
    """Find project root (directory containing .git/)."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").is_dir():
            return parent
    return cwd


def _find_milestones_file(root: Path, task_dir: str | None) -> Path:
    """Find milestones.json in task directory."""
    if task_dir:
        return root / task_dir / "milestones.json"
    # Auto-discover
    candidates = sorted((root / "docs" / "tasks").glob("*/milestones.json"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        return root / "docs" / "tasks" / "milestones.json"  # will not exist → triggers error
    # Multiple - try to find active one
    for c in candidates:
        try:
            data = json.loads(c.read_text(encoding="utf-8"))
            if any(not m.get("done") for m in data.get("milestones", [])):
                return c
        except (json.JSONDecodeError, OSError):
            continue
    return candidates[-1]


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(verbose: bool) -> None:
    """Sefirot - Claude Code multi-agent orchestration framework."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


# --- Loop command (core) ---


@main.command()
@click.option("--from-skill", is_flag=True, help="Called from Claude Code skill (enables question queue)")
@click.option("--milestone", "-m", type=int, default=None, help="Run specific milestone only")
@click.option("--dry-run", is_flag=True, help="Show execution plan without running")
@click.option("--max-parallel", type=int, default=8, help="Max concurrent builders")
@click.option("--model", default="opus", help="Claude model to use")
@click.option("--task-dir", default=None, help="Task directory containing milestones.json (auto-discovered if omitted)")
def loop(
    from_skill: bool,
    milestone: int | None,
    dry_run: bool,
    max_parallel: int,
    model: str,
    task_dir: str | None,
) -> None:
    """Run the Planner → Builder → Verifier loop."""
    from sefirot.loop import LoopEngine

    root = _find_root()
    engine = LoopEngine(
        root,
        task_dir=task_dir,
        from_skill=from_skill,
        milestone=milestone,
        dry_run=dry_run,
        max_parallel=max_parallel,
        model=model,
    )
    rc = engine.run()
    sys.exit(rc)


# --- List command ---


@main.command(name="list")
@click.option("--active", is_flag=True, help="Show only tasks with incomplete milestones")
@click.option("--no-milestones", is_flag=True, help="Show only task dirs without milestones.json")
def list_cmd(active: bool, no_milestones: bool) -> None:
    """List task directories and their status."""
    root = _find_root()
    tasks_root = root / "docs" / "tasks"
    if not tasks_root.is_dir():
        click.echo("No docs/tasks/ directory found. Run /plan and /milestone first.", err=True)
        sys.exit(1)

    # Collect all task directories (any subdirectory under docs/tasks/)
    task_dirs = sorted(d for d in tasks_root.iterdir() if d.is_dir())
    if not task_dirs:
        click.echo("No task directories found. Run /plan first.", err=True)
        sys.exit(1)

    found = False
    for d in task_dirs:
        task_dir = d.relative_to(root)
        ms_file = d / "milestones.json"

        if not ms_file.exists():
            if active:
                continue
            # Find design doc for display
            design_docs = [f.name for f in d.glob("*.md")]
            docs_str = ", ".join(design_docs) if design_docs else "no docs"
            click.echo(f"{task_dir}  [NO MILESTONES]  ({docs_str})")
            found = True
            continue

        if no_milestones:
            continue

        try:
            data = json.loads(ms_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            if not active:
                click.echo(f"{task_dir}  (error reading file)")
                found = True
            continue

        milestones = data.get("milestones", [])
        done = sum(1 for m in milestones if m.get("done"))
        total = len(milestones)
        is_complete = done == total

        if active and is_complete:
            continue

        status_str = "COMPLETE" if is_complete else f"{done}/{total}"
        goal = data.get("goal", "") or (milestones[0].get("goal", "") if milestones else "")
        click.echo(f"{task_dir}  [{status_str}]  {goal[:60]}")
        found = True

    if not found:
        if no_milestones:
            click.echo("All task directories have milestones.json.", err=True)
        elif active:
            click.echo("No active tasks found.", err=True)
        else:
            click.echo("No task directories found.", err=True)


# --- Status command ---


@main.command()
@click.option("--task-dir", default=None, help="Task directory containing milestones.json (auto-discovered if omitted)")
def status(task_dir: str | None) -> None:
    """Show milestones.json status summary."""
    root = _find_root()
    ms_file = _find_milestones_file(root, task_dir)

    if not ms_file.exists():
        click.echo("No milestones.json found. Run /plan and /milestone first.", err=True)
        sys.exit(1)

    data = json.loads(ms_file.read_text(encoding="utf-8"))
    milestones = data.get("milestones", [])

    for ms in milestones:
        done_mark = "DONE" if ms.get("done") else "    "
        tasks = ms.get("tasks", [])
        done_tasks = sum(1 for t in tasks if t.get("done"))
        click.echo(
            f"[{done_mark}] Milestone {ms['milestone']}: {ms.get('goal', '')[:60]}"
            f"  ({done_tasks}/{len(tasks)} tasks)"
        )
        for t in tasks:
            t_mark = "x" if t.get("done") else " "
            click.echo(f"  [{t_mark}] W{t.get('wave', '?')} {t['id']}: {t.get('description', '')[:50]}")

    questions = data.get("questions", [])
    if questions:
        click.echo(f"\nPending questions: {len(questions)}")
        for q in questions:
            click.echo(f"  - [{q.get('agent', '?')}] {q.get('question', '')[:60]}")


# --- Questions command (for debugging) ---


@main.command()
@click.option("--task-dir", default=None, help="Task directory containing milestones.json (auto-discovered if omitted)")
def questions(task_dir: str | None) -> None:
    """Show and optionally clear pending questions."""
    root = _find_root()
    ms_file = _find_milestones_file(root, task_dir)

    if not ms_file.exists():
        click.echo("No milestones.json found.", err=True)
        sys.exit(1)

    data = json.loads(ms_file.read_text(encoding="utf-8"))
    questions = data.get("questions", [])

    if not questions:
        click.echo("No pending questions.")
        return

    for i, q in enumerate(questions, 1):
        click.echo(f"{i}. [{q.get('agent', '?')}/{q.get('task_id', '?')}] {q.get('question', '')}")

    if click.confirm("\nClear all questions?"):
        data["questions"] = []
        ms_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        click.echo("Questions cleared.")


if __name__ == "__main__":
    main()
