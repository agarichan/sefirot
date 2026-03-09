"""Tests for state management."""

from pathlib import Path

import pytest

from sefirot.state import SefirotState, parse_frontmatter, render_frontmatter


@pytest.fixture
def state(tmp_path: Path) -> SefirotState:
    """Create a SefirotState in a temp directory."""
    s = SefirotState(tmp_path)
    (tmp_path / ".sefirot" / "tasks").mkdir(parents=True)
    (tmp_path / ".sefirot" / "config" / "agents").mkdir(parents=True)
    return s


class TestFrontmatter:
    def test_parse_basic(self):
        text = "---\ntitle: Hello\nstatus: pending\n---\nBody text"
        meta, body = parse_frontmatter(text)
        assert meta["title"] == "Hello"
        assert meta["status"] == "pending"
        assert body == "Body text"

    def test_parse_no_frontmatter(self):
        text = "Just body text"
        meta, body = parse_frontmatter(text)
        assert meta == {}
        assert body == "Just body text"

    def test_roundtrip(self):
        meta = {"id": "TASK-001", "title": "Test", "status": "pending"}
        body = "\n## Overview\n\nSome content\n"
        rendered = render_frontmatter(meta, body)
        parsed_meta, parsed_body = parse_frontmatter(rendered)
        assert parsed_meta == meta
        assert parsed_body == body


class TestTaskCRUD:
    def test_create_task(self, state: SefirotState):
        task = state.create_task("Test task", task_type="implement")
        assert task.id == "TASK-001"
        assert task.title == "Test task"
        assert task.status == "pending"
        assert task.type == "implement"

    def test_create_multiple_tasks(self, state: SefirotState):
        t1 = state.create_task("First")
        t2 = state.create_task("Second")
        t3 = state.create_task("Third")
        assert t1.id == "TASK-001"
        assert t2.id == "TASK-002"
        assert t3.id == "TASK-003"

    def test_get_task(self, state: SefirotState):
        state.create_task("Test task")
        task = state.get_task("TASK-001")
        assert task is not None
        assert task.title == "Test task"

    def test_get_nonexistent_task(self, state: SefirotState):
        assert state.get_task("TASK-999") is None

    def test_update_task(self, state: SefirotState):
        state.create_task("Test task")
        updated = state.update_task("TASK-001", status="in_progress", session_id="abc123")
        assert updated is not None
        assert updated.status == "in_progress"
        assert updated.session_id == "abc123"

        # Verify persistence
        reloaded = state.get_task("TASK-001")
        assert reloaded is not None
        assert reloaded.status == "in_progress"
        assert reloaded.session_id == "abc123"

    def test_list_tasks(self, state: SefirotState):
        state.create_task("First", task_type="implement")
        state.create_task("Second", task_type="test")
        state.update_task("TASK-001", status="in_progress")

        all_tasks = state.list_tasks()
        assert len(all_tasks) == 2

        in_progress = state.list_tasks(status="in_progress")
        assert len(in_progress) == 1
        assert in_progress[0].id == "TASK-001"


class TestDecisions:
    def test_add_decision(self, state: SefirotState):
        decisions_path = state.sefirot_dir / "decisions.md"
        state.add_decision("Use PostgreSQL", context="Better JSON support")
        content = decisions_path.read_text()
        assert "Use PostgreSQL" in content
        assert "Better JSON support" in content

    def test_append_decision(self, state: SefirotState):
        state.add_decision("First decision")
        state.add_decision("Second decision")
        content = (state.sefirot_dir / "decisions.md").read_text()
        assert "First decision" in content
        assert "Second decision" in content


class TestSessions:
    def test_save_and_get_session(self, state: SefirotState):
        state.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        state.save_session("main", "sess-123")
        assert state.get_session("main") == "sess-123"

    def test_get_nonexistent_session(self, state: SefirotState):
        assert state.get_session("nonexistent") is None


class TestConfig:
    def test_get_agent_config(self, state: SefirotState):
        config_path = state.config_dir / "agents" / "implement.md"
        config_path.write_text("# Implement Agent\n", encoding="utf-8")
        assert state.get_agent_config("implement") == "# Implement Agent\n"

    def test_get_nonexistent_agent_config(self, state: SefirotState):
        assert state.get_agent_config("nonexistent") is None
