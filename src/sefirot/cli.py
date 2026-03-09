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
def loop(
    from_skill: bool,
    milestone: int | None,
    dry_run: bool,
    max_parallel: int,
    model: str,
) -> None:
    """Run the Planner → Builder → Verifier loop."""
    from sefirot.loop import LoopEngine

    root = _find_root()
    engine = LoopEngine(
        root,
        from_skill=from_skill,
        milestone=milestone,
        dry_run=dry_run,
        max_parallel=max_parallel,
        model=model,
    )
    rc = engine.run()
    sys.exit(rc)


# --- Status command ---


@main.command()
def status() -> None:
    """Show milestones.json status summary."""
    root = _find_root()
    ms_file = root / "milestones.json"

    if not ms_file.exists():
        click.echo("No milestones.json found. Run /plan and /gen-milestones first.", err=True)
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
def questions() -> None:
    """Show and optionally clear pending questions."""
    root = _find_root()
    ms_file = root / "milestones.json"

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
