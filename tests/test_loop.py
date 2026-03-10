"""Tests for the loop engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sefirot.loop import EXIT_QUESTIONS_PENDING, LoopEngine


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory."""
    sefirot_dir = tmp_path / ".sefirot"
    sefirot_dir.mkdir()
    (sefirot_dir / "sessions").mkdir()
    (sefirot_dir / "prompts").mkdir()

    # Create minimal prompt templates
    for name in ("planner", "builder", "verifier"):
        (sefirot_dir / "prompts" / f"{name}.md").write_text(
            f"You are the {name}. Milestone __MILESTONE_NUMBER__: __MILESTONE_GOAL__"
        )

    # Init git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], cwd=tmp_path, capture_output=True)

    return tmp_path


def make_milestones(project_dir: Path, milestones: list[dict], **extra) -> Path:
    """Write .sefirot/milestones.json and return its path."""
    data = {"source": "", "questions": [], "milestones": milestones, **extra}
    ms_file = project_dir / ".sefirot" / "milestones.json"
    ms_file.parent.mkdir(parents=True, exist_ok=True)
    ms_file.write_text(json.dumps(data, indent=2) + "\n")
    return ms_file


class TestLoopEngine:
    def test_load_milestones(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {"milestone": 1, "goal": "Setup", "done": False, "tasks": []},
        ])
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()
        assert len(data["milestones"]) == 1
        assert data["milestones"][0]["goal"] == "Setup"

    def test_load_milestones_missing(self, project_dir: Path) -> None:
        engine = LoopEngine(project_dir)
        with pytest.raises(SystemExit):
            engine.load_milestones()

    def test_milestones_file_path(self, project_dir: Path) -> None:
        """milestones.json は .sefirot/ 配下に配置される。"""
        engine = LoopEngine(project_dir)
        assert engine.milestones_file == project_dir / ".sefirot" / "milestones.json"

    def test_question_queue(self, project_dir: Path) -> None:
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()

        assert not engine.has_pending_questions(data)

        engine.add_question(data, "builder", "task-1", "How should I handle auth?")
        assert engine.has_pending_questions(data)
        assert len(data["questions"]) == 1
        assert data["questions"][0]["agent"] == "builder"

        questions = engine.clear_questions(data)
        assert len(questions) == 1
        assert not engine.has_pending_questions(data)

    def test_save_milestones(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {"milestone": 1, "goal": "Setup", "done": False, "tasks": []},
        ])
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()
        data["milestones"][0]["done"] = True
        engine.save_milestones(data)

        reloaded = engine.load_milestones()
        assert reloaded["milestones"][0]["done"] is True

    def test_dry_run_skips_execution(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {
                "milestone": 1,
                "goal": "Setup",
                "done": False,
                "tasks": [
                    {"id": "setup-types", "description": "Create types", "wave": 1, "done": False},
                ],
            },
        ])
        engine = LoopEngine(project_dir, dry_run=True)
        rc = engine.run()
        assert rc == 0

    def test_skip_done_milestones(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {"milestone": 1, "goal": "Done", "done": True, "tasks": []},
        ])
        engine = LoopEngine(project_dir)
        rc = engine.run()
        assert rc == 0

    def test_filter_target_milestone(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {"milestone": 1, "goal": "First", "done": True, "tasks": []},
            {
                "milestone": 2,
                "goal": "Second",
                "done": False,
                "tasks": [
                    {"id": "t1", "description": "task", "wave": 1, "done": False},
                ],
            },
        ])
        engine = LoopEngine(project_dir, milestone=2, dry_run=True)
        rc = engine.run()
        assert rc == 0

    def test_target_milestone_not_found(self, project_dir: Path) -> None:
        make_milestones(project_dir, [
            {"milestone": 1, "goal": "First", "done": False, "tasks": []},
        ])
        engine = LoopEngine(project_dir, milestone=99)
        rc = engine.run()
        assert rc == 1

    def test_prompts_dir_local_override(self, project_dir: Path) -> None:
        """Local .sefirot/prompts/ should take priority over package templates."""
        engine = LoopEngine(project_dir)
        assert engine.prompts_dir == project_dir / ".sefirot" / "prompts"

    def test_lifecycle_sessions_dir(self, project_dir: Path) -> None:
        """sessions_dir はライフサイクルごとのサブディレクトリになる。"""
        make_milestones(
            project_dir, [],
            source="docs/tasks/20260310_0437_toy新機能追加/design.md",
        )
        engine = LoopEngine(project_dir, dry_run=True)
        # run() がライフサイクル別 sessions_dir を設定する
        data = engine.load_milestones()
        lifecycle = engine._lifecycle_name(data)
        assert lifecycle == "20260310_0437_toy新機能追加"
        assert engine._source_dir(data) == "docs/tasks/20260310_0437_toy新機能追加"

    def test_collect_handoff_notes_empty(self, project_dir: Path) -> None:
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir)
        notes = engine._collect_handoff_notes([{"id": "nonexistent"}])
        assert "No handoff notes" in notes

    def test_collect_handoff_notes_from_log(self, project_dir: Path) -> None:
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir)

        # Create a fake builder log with stream-json
        engine.sessions_dir.mkdir(parents=True, exist_ok=True)
        logfile = engine.sessions_dir / "builder-task-1.log"
        events = [
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "working"}]}}),
            json.dumps({"type": "result", "result": "Implemented auth module. All tests pass."}),
        ]
        logfile.write_text("\n".join(events))

        notes = engine._collect_handoff_notes([{"id": "task-1"}])
        assert "task-1" in notes
        assert "auth module" in notes

    def test_question_queue_section_from_skill(self, project_dir: Path) -> None:
        """--from-skill のとき質問キューセクションが注入される。"""
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir, from_skill=True)
        section = engine._question_queue_section("builder")
        assert "質問キュー" in section
        assert '"agent": "builder"' in section

    def test_question_queue_section_planner(self, project_dir: Path) -> None:
        """--from-skill のとき planner にも質問キューセクションが注入される。"""
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir, from_skill=True)
        section = engine._question_queue_section("planner")
        assert "質問キュー" in section
        assert '"agent": "planner"' in section
        assert "未決事項" in section
        # planner は worktree で動かないので worktree の注意書きがないこと
        assert "worktree" not in section

    def test_lifecycle_name_root_source_falls_back_to_default(self, project_dir: Path) -> None:
        """source がルート直下のファイルの場合、lifecycle name は 'default' になる。"""
        make_milestones(project_dir, [], source="sample_task.md")
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()
        assert engine._lifecycle_name(data) == "default"

    def test_source_dir_root_source_falls_back_to_docs_tasks(self, project_dir: Path) -> None:
        """source がルート直下のファイルの場合、source_dir は 'docs/tasks' になる。"""
        make_milestones(project_dir, [], source="sample_task.md")
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()
        assert engine._source_dir(data) == "docs/tasks"

    def test_lifecycle_name_empty_source_falls_back_to_default(self, project_dir: Path) -> None:
        """source が空の場合、lifecycle name は 'default' になる。"""
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir)
        data = engine.load_milestones()
        assert engine._lifecycle_name(data) == "default"

    def test_question_queue_section_not_from_skill(self, project_dir: Path) -> None:
        """--from-skill なしのとき質問キューセクションは空。"""
        make_milestones(project_dir, [])
        engine = LoopEngine(project_dir, from_skill=False)
        section = engine._question_queue_section("builder")
        assert section == ""
