"""MCP server - provides sefirot tools to Claude Code."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from sefirot.state import SefirotState
from sefirot.daemon import SefirotDaemon
from sefirot.spawner import Spawner
from sefirot.worktree import WorktreeManager


def _find_root() -> Path:
    """Find project root containing .sefirot/."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".sefirot").is_dir():
            return parent
    return cwd


mcp = FastMCP("sefirot")

# Lazy-initialized singletons
_root: Path | None = None
_state: SefirotState | None = None
_daemon: SefirotDaemon | None = None
_spawner: Spawner | None = None
_worktree: WorktreeManager | None = None


def _get_root() -> Path:
    global _root
    if _root is None:
        _root = _find_root()
    return _root


def _get_state() -> SefirotState:
    global _state
    if _state is None:
        _state = SefirotState(_get_root())
    return _state


def _get_spawner() -> Spawner:
    global _spawner
    if _spawner is None:
        _spawner = Spawner(_get_root())
    return _spawner


def _get_worktree() -> WorktreeManager:
    global _worktree
    if _worktree is None:
        _worktree = WorktreeManager(_get_root())
    return _worktree


def _ensure_daemon() -> None:
    global _daemon
    if _daemon is None:
        _daemon = SefirotDaemon(_get_root())
        _daemon.start_in_thread()


@mcp.tool()
async def sefirot_spawn(type: str, task_description: str, milestone_id: str = "") -> str:
    """Spawn a sub-agent in an isolated git worktree.

    Args:
        type: Agent type - one of: implement, test, review, spec
        task_description: What the sub-agent should do
        milestone_id: Optional milestone ID to associate with
    """
    _ensure_daemon()
    spawner = _get_spawner()
    result = await spawner.spawn(
        task_type=type,
        task_description=task_description,
        milestone_id=milestone_id or None,
    )
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def sefirot_status(filter: str = "") -> str:
    """Get all task statuses.

    Args:
        filter: Optional status filter (pending, in_progress, blocked, completed, failed)
    """
    state = _get_state()
    spawner = _get_spawner()
    active = set(spawner.active_tasks())

    tasks = state.list_tasks(status=filter or None)
    result = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "type": t.type,
            "milestone": t.milestone,
            "session_id": t.session_id,
            "process_running": t.id in active,
        }
        for t in tasks
    ]
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def sefirot_queue() -> str:
    """Get the notification queue (blocked tasks, context reset suggestions, etc.)."""
    _ensure_daemon()
    root = _get_root()
    queue_file = root / ".sefirot" / "queue.json"

    if not queue_file.exists():
        return json.dumps([])

    notifications = json.loads(queue_file.read_text(encoding="utf-8"))
    # Clear the queue after reading
    queue_file.write_text("[]", encoding="utf-8")
    return json.dumps(notifications, ensure_ascii=False)


@mcp.tool()
async def sefirot_checkpoint(milestone_id: str, summary: str) -> str:
    """Record a milestone completion and save state snapshot.

    Args:
        milestone_id: The milestone ID being completed
        summary: Summary of what was accomplished
    """
    state = _get_state()
    state.add_decision(
        f"Milestone {milestone_id} completed: {summary}",
        context="checkpoint",
    )
    return json.dumps({"status": "ok", "milestone_id": milestone_id})


@mcp.tool()
async def sefirot_decide(decision: str, context: str = "") -> str:
    """Log a decision to decisions.md.

    Args:
        decision: The decision that was made
        context: Why this decision was made
    """
    state = _get_state()
    state.add_decision(decision, context)
    return json.dumps({"status": "ok"})


@mcp.tool()
async def sefirot_merge(task_id: str) -> str:
    """Merge a completed task's worktree into the main branch.

    Args:
        task_id: The task ID to merge (e.g., TASK-001)
    """
    state = _get_state()
    worktree = _get_worktree()

    task = state.get_task(task_id)
    if task is None:
        return json.dumps({"error": f"Task {task_id} not found"})
    if task.status != "completed":
        return json.dumps({"error": f"Task {task_id} is not completed (status: {task.status})"})

    try:
        output = worktree.merge(task_id)
        worktree.remove(task_id)
        return json.dumps({"status": "merged", "output": output})
    except RuntimeError as e:
        return json.dumps({"error": str(e)})


def run_server() -> None:
    """Run the MCP server (stdio transport)."""
    _ensure_daemon()
    mcp.run()
