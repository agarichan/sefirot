"""Project installer - handles `sefirot init`."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def _templates_dir() -> Path:
    """Get the path to bundled templates."""
    return Path(__file__).parent / "templates"


def init_project(root: Path) -> list[str]:
    """Initialize sefirot in a project directory.

    Returns a list of actions taken.
    """
    actions: list[str] = []
    templates = _templates_dir()

    # 1. Create .sefirot/ structure
    sefirot_dir = root / ".sefirot"
    for subdir in ["config/agents", "tasks", "specs"]:
        (sefirot_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Copy default config files
    _copy_template(templates / "config" / "main-agent.md", sefirot_dir / "config" / "main-agent.md")
    actions.append("Created .sefirot/config/main-agent.md")

    for agent in ["implement", "test", "review", "spec"]:
        src = templates / "config" / "agents" / f"{agent}.md"
        dst = sefirot_dir / "config" / "agents" / f"{agent}.md"
        _copy_template(src, dst)
    actions.append("Created .sefirot/config/agents/ (implement, test, review, spec)")

    # Copy project/milestone templates
    _copy_template(templates / "project.md", sefirot_dir / "project.md")
    _copy_template(templates / "milestone.md", sefirot_dir / "milestones.md")
    actions.append("Created .sefirot/project.md and milestones.md")

    # Create decisions.md
    decisions = sefirot_dir / "decisions.md"
    if not decisions.exists():
        decisions.write_text("# Decisions\n", encoding="utf-8")
    actions.append("Created .sefirot/decisions.md")

    # Create sessions.json
    sessions = sefirot_dir / "sessions.json"
    if not sessions.exists():
        sessions.write_text("{}", encoding="utf-8")

    # 2. Create .claude/skills/sefirot/SKILL.md
    skill_dir = root / ".claude" / "skills" / "sefirot"
    skill_dir.mkdir(parents=True, exist_ok=True)
    _copy_template(templates / "skill.md", skill_dir / "SKILL.md")
    actions.append("Created .claude/skills/sefirot/SKILL.md")

    # 3. Update .mcp.json
    _update_mcp_json(root)
    actions.append("Updated .mcp.json (registered sefirot MCP server)")

    # 4. Update .claude/settings.json (hooks)
    _update_claude_settings(root)
    actions.append("Updated .claude/settings.json (added hooks)")

    return actions


def _copy_template(src: Path, dst: Path) -> None:
    """Copy template file if destination doesn't exist."""
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _update_mcp_json(root: Path) -> None:
    """Add sefirot to .mcp.json without clobbering existing entries."""
    mcp_path = root / ".mcp.json"
    data: dict = {}
    if mcp_path.exists():
        data = json.loads(mcp_path.read_text(encoding="utf-8"))

    servers = data.setdefault("mcpServers", {})
    if "sefirot" not in servers:
        servers["sefirot"] = {
            "command": "sefirot",
            "args": ["serve"],
        }
    mcp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _update_claude_settings(root: Path) -> None:
    """Add sefirot hooks to .claude/settings.json without clobbering."""
    settings_path = root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    data: dict = {}
    if settings_path.exists():
        data = json.loads(settings_path.read_text(encoding="utf-8"))

    hooks = data.setdefault("hooks", {})

    # PreCompact hook
    if "PreCompact" not in hooks:
        hooks["PreCompact"] = [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "sefirot hook pre-compact",
                    }
                ]
            }
        ]

    # Stop hook
    if "Stop" not in hooks:
        hooks["Stop"] = [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "sefirot hook stop",
                    }
                ]
            }
        ]

    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
