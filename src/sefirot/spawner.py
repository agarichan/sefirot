"""Sub-agent spawner - launches Claude Code sessions for tasks."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from sefirot.state import SefirotState
from sefirot.worktree import WorktreeManager


class Spawner:
    """Spawns sub-agent Claude Code sessions in isolated worktrees."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.state = SefirotState(root)
        self.worktree = WorktreeManager(root)

    def spawn(
        self,
        task_type: str,
        task_description: str,
        milestone_id: str | None = None,
    ) -> dict[str, str]:
        """Spawn a sub-agent for a new task.

        Returns dict with task_id, session_id, worktree_path.
        """
        # Create task
        task = self.state.create_task(
            title=task_description,
            task_type=task_type,
            milestone=milestone_id,
        )

        # Create worktree
        worktree_path = self.worktree.create(task.id)

        # Build prompt from agent config + task info
        prompt = self._build_prompt(task_type, task)

        # Launch claude in print mode
        result = subprocess.run(
            [
                "claude", "-p", prompt,
                "--output-format", "json",
                "--allowedTools", self._tools_for_type(task_type),
            ],
            cwd=str(worktree_path),
            capture_output=True,
            text=True,
        )

        # Extract session_id from output
        session_id = None
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                session_id = output.get("session_id")
            except (json.JSONDecodeError, KeyError):
                pass

        # Update task with session info
        self.state.update_task(
            task.id,
            status="in_progress",
            session_id=session_id,
            worktree=str(worktree_path),
        )

        return {
            "task_id": task.id,
            "session_id": session_id or "",
            "worktree_path": str(worktree_path),
        }

    def _build_prompt(self, task_type: str, task: "Task") -> str:  # noqa: F821
        """Build the prompt for a sub-agent from config + task."""
        agent_config = self.state.get_agent_config(task_type) or ""
        task_info = f"\n\n## Task: {task.id}\n\n**{task.title}**\n\n{task.body}"
        task_file_path = f".sefirot/tasks/{task.id}.md"
        instructions = (
            f"\n\nUpdate `{task_file_path}` with your progress. "
            f"If you have questions, add them under '## Questions' and "
            f"change the frontmatter status to 'blocked'. "
            f"When done, change status to 'completed' and list deliverables."
        )
        return agent_config + task_info + instructions

    def _tools_for_type(self, task_type: str) -> str:
        """Return allowed tools string based on agent type."""
        tools = {
            "implement": "Read,Edit,Write,Bash,Glob,Grep",
            "test": "Read,Write,Bash,Glob,Grep",
            "review": "Read,Glob,Grep",
            "spec": "Read,Glob,Grep",
        }
        return tools.get(task_type, "Read,Glob,Grep")
