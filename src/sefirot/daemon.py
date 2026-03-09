"""File watcher daemon - monitors .sefirot/tasks/ for changes."""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

from sefirot.state import SefirotState, parse_frontmatter


class TaskWatcher(FileSystemEventHandler):
    """Watches task files for status changes, especially 'blocked'."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.state = SefirotState(root)
        self._known_statuses: dict[str, str] = {}
        self._load_initial_statuses()

    def _load_initial_statuses(self) -> None:
        for task in self.state.list_tasks():
            self._known_statuses[task.id] = task.status

    def on_modified(self, event: FileModifiedEvent) -> None:  # type: ignore[override]
        if not isinstance(event, FileModifiedEvent):
            return
        path = Path(event.src_path)
        if not path.name.startswith("TASK-") or not path.name.endswith(".md"):
            return

        task_id = path.stem
        try:
            text = path.read_text(encoding="utf-8")
            meta, _ = parse_frontmatter(text)
        except Exception:
            return

        new_status = meta.get("status", "")
        old_status = self._known_statuses.get(task_id, "")

        if new_status != old_status:
            self._known_statuses[task_id] = new_status
            if new_status == "blocked":
                self._enqueue_notification(
                    "task_blocked",
                    f"Task {task_id} is blocked and waiting for input.",
                    {"task_id": task_id, "session_id": meta.get("session_id", "")},
                )
            elif new_status == "completed":
                self._enqueue_notification(
                    "task_completed",
                    f"Task {task_id} has been completed.",
                    {"task_id": task_id},
                )
            elif new_status == "failed":
                self._enqueue_notification(
                    "task_failed",
                    f"Task {task_id} has failed.",
                    {"task_id": task_id},
                )

    def _enqueue_notification(
        self, ntype: str, message: str, data: dict | None = None
    ) -> None:
        queue_file = self.root / ".sefirot" / "queue.json"
        notifications: list = []
        if queue_file.exists():
            try:
                notifications = json.loads(queue_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                notifications = []

        notifications.append({
            "type": ntype,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        })
        queue_file.write_text(
            json.dumps(notifications, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


class SefirotDaemon:
    """Background daemon that watches task files."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.observer = Observer()
        self.handler = TaskWatcher(root)

    def start(self) -> None:
        tasks_dir = self.root / ".sefirot" / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        self.observer.schedule(self.handler, str(tasks_dir), recursive=False)
        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join()

    def start_in_thread(self) -> threading.Thread:
        """Start daemon in a background thread. Returns the thread."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
