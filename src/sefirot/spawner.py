"""Sub-agent spawner - launches Claude Code sessions for tasks."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

from sefirot.state import SefirotState
from sefirot.worktree import WorktreeManager

logger = logging.getLogger(__name__)

# Max number of progress entries to keep per task
MAX_PROGRESS_ENTRIES = 20


class Spawner:
    """Spawns sub-agent Claude Code sessions in isolated worktrees.

    Manages running processes internally and streams progress via NDJSON.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.state = SefirotState(root)
        self.worktree = WorktreeManager(root)
        # task_id -> asyncio.subprocess.Process
        self._processes: dict[str, asyncio.subprocess.Process] = {}
        # task_id -> list of progress entries
        self._progress: dict[str, list[str]] = {}
        # task_id -> stream reader task
        self._readers: dict[str, asyncio.Task] = {}
        self._monitor_task: asyncio.Task | None = None

    async def spawn(
        self,
        task_type: str,
        task_description: str,
        milestone_id: str | None = None,
    ) -> dict[str, str]:
        """Spawn a sub-agent for a new task.

        Returns immediately with task_id and worktree_path.
        The sub-agent runs in the background with streamed progress.
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

        # Launch claude with stream-json for real-time progress
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        process = await asyncio.create_subprocess_exec(
            "claude", "-p",
            "--output-format", "stream-json",
            "--verbose",
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
        self._progress[task.id] = []

        # Start stream reader for this task
        self._readers[task.id] = asyncio.create_task(
            self._read_stream(task.id, process)
        )

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

    async def _read_stream(self, task_id: str, process: asyncio.subprocess.Process) -> None:
        """Read NDJSON stream from sub-agent and extract progress."""
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                try:
                    event = json.loads(line.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                entry = self._extract_progress(event)
                if entry:
                    progress = self._progress.get(task_id, [])
                    progress.append(entry)
                    # Keep only recent entries
                    if len(progress) > MAX_PROGRESS_ENTRIES:
                        progress = progress[-MAX_PROGRESS_ENTRIES:]
                    self._progress[task_id] = progress
        except Exception as e:
            logger.debug("Stream reader for %s ended: %s", task_id, e)

    def _extract_progress(self, event: dict) -> str | None:
        """Extract a human-readable progress line from a stream event."""
        etype = event.get("type")

        if etype == "assistant":
            message = event.get("message", {})
            content = message.get("content", [])
            for block in content:
                if block.get("type") == "tool_use":
                    tool = block.get("name", "?")
                    inp = block.get("input", {})
                    return self._summarize_tool_use(tool, inp)
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text:
                        # Truncate long text
                        if len(text) > 100:
                            text = text[:100] + "…"
                        return f"💬 {text}"
            return None

        if etype == "result":
            cost = event.get("total_cost_usd", 0)
            turns = event.get("num_turns", 0)
            duration = event.get("duration_ms", 0)
            return f"✅ 完了 (turns={turns}, {duration/1000:.1f}s, ${cost:.4f})"

        return None

    def _summarize_tool_use(self, tool: str, inp: dict) -> str:
        """Create a short summary of a tool use."""
        if tool in ("Read", "Glob", "Grep"):
            target = inp.get("file_path") or inp.get("pattern") or inp.get("path", "")
            return f"🔍 {tool}: {target}"
        if tool in ("Edit", "Write"):
            path = inp.get("file_path", "")
            return f"✏️ {tool}: {path}"
        if tool == "Bash":
            cmd = inp.get("command", "")
            if len(cmd) > 80:
                cmd = cmd[:80] + "…"
            return f"⚡ Bash: {cmd}"
        return f"🔧 {tool}"

    def get_progress(self, task_id: str) -> list[str]:
        """Get progress entries for a task."""
        return list(self._progress.get(task_id, []))

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

        # Wait for stream reader to finish
        reader = self._readers.pop(task_id, None)
        if reader and not reader.done():
            try:
                await asyncio.wait_for(reader, timeout=5.0)
            except (asyncio.TimeoutError, Exception):
                reader.cancel()

        # Drain stderr
        try:
            await process.stderr.read()
        except Exception:
            pass

        # Determine final status from task file (sub-agent may have updated it)
        task = self.state.get_task(task_id)
        if task and task.status == "in_progress":
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
