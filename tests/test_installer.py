"""Tests for the installer."""

import json
from pathlib import Path

import pytest

from sefirot.installer import init_project


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a temp directory simulating a project root."""
    return tmp_path


class TestInitProject:
    def test_creates_sefirot_structure(self, project_dir: Path):
        init_project(project_dir)
        assert (project_dir / ".sefirot").is_dir()
        assert (project_dir / ".sefirot" / "config").is_dir()
        assert (project_dir / ".sefirot" / "config" / "agents").is_dir()
        assert (project_dir / ".sefirot" / "tasks").is_dir()
        assert (project_dir / ".sefirot" / "specs").is_dir()

    def test_creates_default_config(self, project_dir: Path):
        init_project(project_dir)
        assert (project_dir / ".sefirot" / "config" / "main-agent.md").exists()
        assert (project_dir / ".sefirot" / "config" / "agents" / "implement.md").exists()
        assert (project_dir / ".sefirot" / "config" / "agents" / "test.md").exists()
        assert (project_dir / ".sefirot" / "config" / "agents" / "review.md").exists()
        assert (project_dir / ".sefirot" / "config" / "agents" / "spec.md").exists()

    def test_creates_skill(self, project_dir: Path):
        init_project(project_dir)
        skill = project_dir / ".claude" / "skills" / "sefirot" / "SKILL.md"
        assert skill.exists()
        content = skill.read_text()
        assert "sefirot" in content

    def test_creates_mcp_json(self, project_dir: Path):
        init_project(project_dir)
        mcp_json = project_dir / ".mcp.json"
        assert mcp_json.exists()
        data = json.loads(mcp_json.read_text())
        assert "sefirot" in data["mcpServers"]
        assert data["mcpServers"]["sefirot"]["command"] == "sefirot"

    def test_preserves_existing_mcp_json(self, project_dir: Path):
        mcp_json = project_dir / ".mcp.json"
        mcp_json.write_text(json.dumps({
            "mcpServers": {"other-tool": {"command": "other"}}
        }))
        init_project(project_dir)
        data = json.loads(mcp_json.read_text())
        assert "other-tool" in data["mcpServers"]
        assert "sefirot" in data["mcpServers"]

    def test_creates_claude_settings(self, project_dir: Path):
        init_project(project_dir)
        settings = project_dir / ".claude" / "settings.json"
        assert settings.exists()
        data = json.loads(settings.read_text())
        assert "PreCompact" in data["hooks"]
        assert "Stop" in data["hooks"]

    def test_preserves_existing_hooks(self, project_dir: Path):
        settings_path = project_dir / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text(json.dumps({
            "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}
        }))
        init_project(project_dir)
        data = json.loads(settings_path.read_text())
        assert "UserPromptSubmit" in data["hooks"]
        assert "PreCompact" in data["hooks"]

    def test_does_not_modify_claude_md(self, project_dir: Path):
        claude_md = project_dir / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting content.\n")
        init_project(project_dir)
        assert claude_md.read_text() == "# My Project\n\nExisting content.\n"

    def test_idempotent(self, project_dir: Path):
        init_project(project_dir)
        first_mcp = (project_dir / ".mcp.json").read_text()
        init_project(project_dir)
        second_mcp = (project_dir / ".mcp.json").read_text()
        assert first_mcp == second_mcp

    def test_returns_actions(self, project_dir: Path):
        actions = init_project(project_dir)
        assert len(actions) > 0
        assert any("config" in a.lower() or "sefirot" in a.lower() for a in actions)
