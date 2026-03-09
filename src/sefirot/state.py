"""State management for .sefirot/ directory.

Handles reading/writing Markdown files with YAML frontmatter.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown text."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return meta, body


def render_frontmatter(meta: dict[str, Any], body: str) -> str:
    """Render metadata and body back to frontmatter markdown."""
    yaml_str = yaml.dump(meta, default_flow_style=False, allow_unicode=True).rstrip()
    return f"---\n{yaml_str}\n---\n{body}"


@dataclass
class Task:
    id: str
    title: str
    status: str = "pending"
    type: str = "implement"
    session_id: str | None = None
    worktree: str | None = None
    milestone: str | None = None
    created: str = ""
    updated: str = ""
    body: str = ""

    def to_frontmatter(self) -> dict[str, Any]:
        meta: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "type": self.type,
            "created": self.created,
            "updated": self.updated,
        }
        if self.session_id:
            meta["session_id"] = self.session_id
        if self.worktree:
            meta["worktree"] = self.worktree
        if self.milestone:
            meta["milestone"] = self.milestone
        return meta


class SefirotState:
    """Manages the .sefirot/ directory state."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.sefirot_dir = root / ".sefirot"

    @property
    def tasks_dir(self) -> Path:
        return self.sefirot_dir / "tasks"

    @property
    def specs_dir(self) -> Path:
        return self.sefirot_dir / "specs"

    @property
    def config_dir(self) -> Path:
        return self.sefirot_dir / "config"

    @property
    def sessions_file(self) -> Path:
        return self.sefirot_dir / "sessions.json"

    def is_initialized(self) -> bool:
        return self.sefirot_dir.is_dir()

    # --- Tasks ---

    def next_task_id(self) -> str:
        existing = sorted(self.tasks_dir.glob("TASK-*.md"))
        if not existing:
            return "TASK-001"
        last = existing[-1].stem  # e.g. "TASK-003"
        num = int(last.split("-")[1]) + 1
        return f"TASK-{num:03d}"

    def create_task(
        self,
        title: str,
        task_type: str = "implement",
        milestone: str | None = None,
        body: str = "",
    ) -> Task:
        task_id = self.next_task_id()
        today = date.today().isoformat()
        task = Task(
            id=task_id,
            title=title,
            status="pending",
            type=task_type,
            milestone=milestone,
            created=today,
            updated=today,
            body=body,
        )
        self._write_task(task)
        return task

    def get_task(self, task_id: str) -> Task | None:
        path = self.tasks_dir / f"{task_id}.md"
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        return Task(
            id=meta.get("id", task_id),
            title=meta.get("title", ""),
            status=meta.get("status", "pending"),
            type=meta.get("type", "implement"),
            session_id=meta.get("session_id"),
            worktree=meta.get("worktree"),
            milestone=meta.get("milestone"),
            created=str(meta.get("created", "")),
            updated=str(meta.get("updated", "")),
            body=body,
        )

    def update_task(self, task_id: str, **kwargs: Any) -> Task | None:
        task = self.get_task(task_id)
        if task is None:
            return None
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated = date.today().isoformat()
        self._write_task(task)
        return task

    def list_tasks(self, status: str | None = None) -> list[Task]:
        tasks = []
        for path in sorted(self.tasks_dir.glob("TASK-*.md")):
            task = self.get_task(path.stem)
            if task and (status is None or task.status == status):
                tasks.append(task)
        return tasks

    def _write_task(self, task: Task) -> None:
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        path = self.tasks_dir / f"{task.id}.md"
        content = render_frontmatter(task.to_frontmatter(), task.body)
        path.write_text(content, encoding="utf-8")

    # --- Decisions ---

    def add_decision(self, decision: str, context: str = "") -> None:
        path = self.sefirot_dir / "decisions.md"
        today = date.today().isoformat()
        entry = f"\n### {today}\n\n{decision}\n"
        if context:
            entry += f"\n> {context}\n"
        if path.exists():
            current = path.read_text(encoding="utf-8")
            path.write_text(current + entry, encoding="utf-8")
        else:
            path.write_text(f"# Decisions\n{entry}", encoding="utf-8")

    # --- Milestones ---

    def add_milestone(self, milestone_id: str, title: str, description: str = "") -> None:
        path = self.sefirot_dir / "milestones.md"
        today = date.today().isoformat()
        entry = f"\n## {milestone_id}: {title}\n\n- Status: pending\n- Created: {today}\n"
        if description:
            entry += f"\n{description}\n"
        if path.exists():
            current = path.read_text(encoding="utf-8")
            path.write_text(current + entry, encoding="utf-8")
        else:
            path.write_text(f"# Milestones\n{entry}", encoding="utf-8")

    # --- Sessions ---

    def save_session(self, key: str, session_id: str) -> None:
        data = self._load_sessions()
        data[key] = session_id
        self.sessions_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def get_session(self, key: str) -> str | None:
        return self._load_sessions().get(key)

    def _load_sessions(self) -> dict[str, str]:
        if not self.sessions_file.exists():
            return {}
        return json.loads(self.sessions_file.read_text(encoding="utf-8"))

    # --- Config ---

    def get_agent_config(self, agent_type: str) -> str | None:
        path = self.config_dir / "agents" / f"{agent_type}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def get_main_agent_config(self) -> str | None:
        path = self.config_dir / "main-agent.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None
