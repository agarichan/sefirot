"""Sub-agent spawner - launches Claude Code sessions for tasks."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from pathlib import Path

from sefirot.state import SefirotState
from sefirot.worktree import WorktreeManager

logger = logging.getLogger(__name__)


class Spawner:
    """Spawns sub-agent Claude Code sessions in isolated worktrees.

    Manages running processes internally and monitors them via an async loop.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.state = SefirotState(root)
        self.worktree = WorktreeManager(root)
        # task_id -> asyncio.subprocess.Process
        self._processes: dict[str, asyncio.subprocess.Process] = {}
        self._monitor_task: asyncio.Task | None = None

    async def spawn(
        self,
        task_type: str,
        task_description: str,
        milestone_id: str | None = None,
    ) -> dict[str, str]:
        """Spawn a sub-agent for a new task.

        Returns immediately with task_id and worktree_path.
        The sub-agent runs in the background.
        """
        # Create task
        task = self.state.create_task(
            title=task_description,
            task_type=task_type,
            milestone=milestone_id,
        )

        # Create worktree
        worktree_path = self.worktree.create(task.id)

        # Generate session ID upfront so we can resume immediately
        session_id = str(uuid.uuid4())

        # Build prompt from agent config + task info
        prompt = self._build_prompt(task_type, task)

        # Launch claude asynchronously with pre-assigned session ID
        # Remove CLAUDECODE env var to allow nested sessions
        # Pass prompt via stdin to avoid argument length issues
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        process = await asyncio.create_subprocess_exec(
            "claude", "-p",
            "--output-format", "json",
            "--session-id", session_id,
            "--allowedTools", self._tools_for_type(task_type),
            "--permission-mode", self._permission_for_type(task_type),
            cwd=str(worktree_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        # Send prompt via stdin and close it
        process.stdin.write(prompt.encode())
        await process.stdin.drain()
        process.stdin.close()
        await process.stdin.wait_closed()

        self._processes[task.id] = process

        # Update task status immediately with session_id
        self.state.update_task(
            task.id,
            status="in_progress",
            session_id=session_id,
            worktree=str(worktree_path),
        )

        # Ensure monitor loop is running
        self._ensure_monitor()

        return {
            "task_id": task.id,
            "session_id": session_id,
            "worktree_path": str(worktree_path),
            "status": "spawned",
        }

    def _ensure_monitor(self) -> None:
        """Start the monitor loop if not already running."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self, interval: float = 5.0) -> None:
        """Periodically check running processes for completion."""
        while self._processes:
            completed = []
            for task_id, process in self._processes.items():
                if process.returncode is not None:
                    completed.append(task_id)
                    continue
                # Non-blocking poll
                try:
                    await asyncio.wait_for(process.wait(), timeout=0.1)
                    completed.append(task_id)
                except asyncio.TimeoutError:
                    pass

            for task_id in completed:
                await self._handle_completion(task_id)

            await asyncio.sleep(interval)

    async def _handle_completion(self, task_id: str) -> None:
        """Handle a completed sub-agent process."""
        process = self._processes.pop(task_id, None)
        if process is None:
            return

        # Drain stdout/stderr
        try:
            await process.communicate()
        except Exception:
            pass

        # Determine final status from task file (sub-agent may have updated it)
        task = self.state.get_task(task_id)
        if task and task.status == "in_progress":
            # Sub-agent didn't update status itself; mark based on return code
            new_status = "completed" if process.returncode == 0 else "failed"
            self.state.update_task(task_id, status=new_status)

        # Enqueue notification
        self._enqueue_notification(task_id, process.returncode or 0)
        logger.info("Task %s finished (rc=%s)", task_id, process.returncode)

    def _enqueue_notification(self, task_id: str, returncode: int) -> None:
        """Add a completion notification to the queue."""
        queue_file = self.root / ".sefirot" / "queue.json"
        notifications: list = []
        if queue_file.exists():
            try:
                notifications = json.loads(queue_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                notifications = []

        from datetime import datetime

        ntype = "task_completed" if returncode == 0 else "task_failed"
        notifications.append({
            "type": ntype,
            "message": f"Task {task_id} {'completed' if returncode == 0 else 'failed'} (rc={returncode}).",
            "data": {"task_id": task_id},
            "timestamp": datetime.now().isoformat(),
        })
        queue_file.write_text(
            json.dumps(notifications, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def active_tasks(self) -> list[str]:
        """Return list of task_ids with running processes."""
        return [
            tid for tid, proc in self._processes.items()
            if proc.returncode is None
        ]

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

    def _permission_for_type(self, task_type: str) -> str:
        """Return permission mode based on agent type."""
        # All agents need at least Edit/Write for task file updates
        return "acceptEdits"

    def _tools_for_type(self, task_type: str) -> str:
        """Return allowed tools string based on agent type."""
        tools = {
            "implement": "Read,Edit,Write,Bash,Glob,Grep",
            "test": "Read,Edit,Write,Bash,Glob,Grep",
            "review": "Read,Edit,Write,Glob,Grep",
            "spec": "Read,Edit,Write,Glob,Grep",
        }
        return tools.get(task_type, "Read,Glob,Grep")
