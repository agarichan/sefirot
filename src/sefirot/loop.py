"""Core loop engine - orchestrates Planner/Builder/Verifier agents.

Inspired by claude-looper's run.sh, reimplemented in Python with
question queue support for skill integration.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Exit code when questions are pending (signals skill to ask user)
EXIT_QUESTIONS_PENDING = 10

# Defaults
DEFAULT_MAX_PARALLEL = 8
DEFAULT_MAX_ROUNDS = 50
DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes
DEFAULT_MODEL = "opus"


class LoopEngine:
    """Orchestrates the Planner → Builder → Verifier loop."""

    def __init__(
        self,
        root: Path,
        *,
        task_dir: Path | str | None = None,
        from_skill: bool = False,
        milestone: int | None = None,
        dry_run: bool = False,
        max_parallel: int = DEFAULT_MAX_PARALLEL,
        max_rounds: int = DEFAULT_MAX_ROUNDS,
        session_timeout: int = DEFAULT_SESSION_TIMEOUT,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.root = root
        self.from_skill = from_skill
        self.target_milestone = milestone
        self.dry_run = dry_run
        self.max_parallel = max_parallel
        self.max_rounds = max_rounds
        self.session_timeout = session_timeout
        self.model = model

        # Resolve task directory (where milestones.json lives)
        if task_dir is not None:
            self.task_dir = Path(task_dir)
        else:
            self.task_dir = self._discover_task_dir()
        self.milestones_file = root / self.task_dir / "milestones.json"
        self.prompts_dir = self._find_prompts_dir()
        # sessions_dir is set per-lifecycle in run()
        self.sessions_dir = root / ".sefirot" / "sessions"

        # Pre-load CLAUDE.md content (if exists) to inject into prompts
        self._claude_md_content = self._load_claude_md()

        # Lock for milestones.json writes (prevents parallel builder race conditions)
        self._milestones_lock = asyncio.Lock()

    def _discover_task_dir(self) -> Path:
        """Auto-discover task directory containing milestones.json."""
        tasks_root = self.root / "docs" / "tasks"
        if not tasks_root.is_dir():
            logger.error("docs/tasks/ directory not found. Specify --task-dir.")
            self._print_action("ERROR", "docs/tasks/ directory not found. Specify --task-dir.")
            sys.exit(1)
        candidates = sorted(tasks_root.glob("*/milestones.json"))
        if not candidates:
            logger.error("No milestones.json found in docs/tasks/*/. Specify --task-dir.")
            self._print_action("ERROR", "No milestones.json found in docs/tasks/*/. Specify --task-dir.")
            sys.exit(1)
        if len(candidates) == 1:
            return candidates[0].parent.relative_to(self.root)
        # Multiple found - prefer one with undone milestones
        active = []
        for c in candidates:
            try:
                data = json.loads(c.read_text(encoding="utf-8"))
                if any(not m.get("done") for m in data.get("milestones", [])):
                    active.append(c)
            except (json.JSONDecodeError, OSError):
                continue
        if len(active) == 1:
            return active[0].parent.relative_to(self.root)
        if len(active) == 0:
            # All done, use the last one
            return candidates[-1].parent.relative_to(self.root)
        # Multiple active - ambiguous
        dirs = ", ".join(str(c.parent.relative_to(self.root)) for c in active)
        msg = f"Multiple active milestones.json found: {dirs}. Specify --task-dir."
        logger.error(msg)
        self._print_action("ERROR", msg)
        sys.exit(1)

    def _load_claude_md(self) -> str:
        """Load CLAUDE.md content if it exists, otherwise return notice."""
        for candidate in [
            self.root / "CLAUDE.md",
            self.root / ".claude" / "CLAUDE.md",
        ]:
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8")
                return (
                    f"## CLAUDE.md（プロジェクトルール）\n\n"
                    f"以下は `{candidate.relative_to(self.root)}` の内容です:\n\n"
                    f"{content}\n"
                )
        return (
            "## CLAUDE.md（プロジェクトルール）\n\n"
            "このプロジェクトには CLAUDE.md がありません。"
            "プロジェクト固有のルールは設計ドキュメントを参照してください。\n"
        )

    def _find_prompts_dir(self) -> Path:
        """Find prompts directory - check project-local first, then package."""
        local = self.root / ".sefirot" / "prompts"
        if local.is_dir():
            return local
        # npx skills add でインストールされた場合
        skills = self.root / ".claude" / "skills" / "sefirot-loop" / "prompts"
        if skills.is_dir():
            return skills
        # Fall back to package templates
        return Path(__file__).parent / "templates" / "prompts"

    # --- Milestones JSON ---

    def load_milestones(self) -> dict:
        """Load milestones.json."""
        if not self.milestones_file.exists():
            msg = f"milestones.json not found at {self.milestones_file}"
            logger.error(msg)
            self._print_action("ERROR", msg)
            sys.exit(1)
        return json.loads(self.milestones_file.read_text(encoding="utf-8"))

    def save_milestones(self, data: dict) -> None:
        """Save milestones.json."""
        self.milestones_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    async def _save_milestones_locked(self, task_id: str) -> None:
        """Reload, mark task done, and save milestones.json with lock.

        Prevents race conditions when parallel builders complete simultaneously.
        """
        async with self._milestones_lock:
            data = self.load_milestones()
            for ms in data.get("milestones", []):
                for t in ms.get("tasks", []):
                    if t.get("id") == task_id:
                        t["done"] = True
                        break
            self.save_milestones(data)

    # --- Question Queue ---

    def has_pending_questions(self, data: dict) -> bool:
        """Check if there are pending questions in the queue."""
        return bool(data.get("questions"))

    def add_question(self, data: dict, agent: str, task_id: str, question: str) -> None:
        """Add a question to the queue."""
        if "questions" not in data:
            data["questions"] = []
        data["questions"].append({
            "agent": agent,
            "task_id": task_id,
            "question": question,
            "timestamp": datetime.now().isoformat(),
        })

    def clear_questions(self, data: dict) -> list[dict]:
        """Clear and return pending questions."""
        questions = data.get("questions", [])
        data["questions"] = []
        return questions

    # --- Action Output ---

    def _init_output(self) -> None:
        """Initialize output log file for progress reporting.

        When running inside Claude Code (CLAUDECODE=1), child claude processes
        can hijack the parent's stdout. We write to a dedicated log file instead
        and print its path so the caller can tail it.
        """
        self._output_log = self.sessions_dir / "loop-output.log"
        self._output_fh = open(self._output_log, "w", encoding="utf-8")
        # Print the log path to stdout before claude can hijack it
        print(f"[SEFIROT:OUTPUT_LOG] {self._output_log}", flush=True)

    def _emit(self, line: str) -> None:
        """Write a line to the output log and flush."""
        self._output_fh.write(line + "\n")
        self._output_fh.flush()

    def _print_action(self, action: str, message: str) -> None:
        """Print action directive for the caller (skill) to follow."""
        self._emit(f"\n[SEFIROT:ACTION] {action}")
        self._emit(f"[SEFIROT:MESSAGE] {message}")

    def _progress(self, msg: str) -> None:
        """Print a highly visible progress line (flushed immediately)."""
        self._emit(f"[SEFIROT] {msg}")

    @staticmethod
    def _build_shell_command(cmd: list[str], logfile: Path) -> str:
        """Build a shell command string that redirects stdout/stderr to logfile."""
        import shlex
        escaped_cmd = " ".join(shlex.quote(str(c)) for c in cmd)
        escaped_log = shlex.quote(str(logfile))
        return f"{escaped_cmd} < /dev/null > {escaped_log} 2>&1"

    # --- Main Loop ---

    def _lifecycle_name(self) -> str:
        """Extract lifecycle directory name from task_dir."""
        return self.task_dir.name or "default"

    def _source_dir(self) -> str:
        """Get task directory path (relative to root)."""
        return str(self.task_dir)

    def run(self) -> int:
        """Run the main loop. Returns exit code."""
        self._init_output()
        self._progress(f"ループ開始: {self.task_dir}")
        data = self.load_milestones()

        # Set lifecycle-specific sessions directory
        self.sessions_dir = (
            self.root / ".sefirot" / "sessions" / self._lifecycle_name()
        )
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        milestones = data.get("milestones", [])

        if not milestones:
            logger.error("No milestones found in milestones.json")
            self._print_action("ERROR", "No milestones found in milestones.json")
            return 1

        # Filter to target milestone if specified
        if self.target_milestone is not None:
            milestones = [
                m for m in milestones
                if m.get("milestone") == self.target_milestone
            ]
            if not milestones:
                logger.error("Milestone %d not found", self.target_milestone)
                self._print_action("ERROR", f"Milestone {self.target_milestone} not found")
                return 1

        round_count = 0
        for ms in milestones:
            if ms.get("done"):
                logger.info(
                    "Milestone %d already done, skipping", ms["milestone"]
                )
                continue

            rc = self._run_milestone(data, ms)
            if rc == EXIT_QUESTIONS_PENDING:
                self._print_action("QUESTIONS_PENDING", "質問が保留中です。milestones.json の questions 配列を確認し、ユーザーに質問してください。回答を設計ドキュメントに反映した後、再度 sefirot loop を実行してください。")
                return rc
            if rc != 0:
                self._print_action("ERROR", f"Milestone {ms['milestone']} failed with exit code {rc}")
                return rc

            round_count += 1
            if round_count >= self.max_rounds:
                logger.warning("Max rounds (%d) reached", self.max_rounds)
                break

        self._progress("全マイルストーン完了")
        logger.info("All milestones completed")
        self._print_action("COMPLETE", "全てのマイルストーンが完了しました。milestones.json を読み、完了したマイルストーンとタスクの一覧をユーザーに報告してください。")
        return 0

    def _reload_milestone(self, data: dict, ms_num: int) -> tuple[dict, dict]:
        """Reload milestones.json and return (data, milestone) with fresh references."""
        data_reloaded = self.load_milestones()
        for m in data_reloaded.get("milestones", []):
            if m.get("milestone") == ms_num:
                return data_reloaded, m
        return data_reloaded, {}

    def _run_milestone(self, data: dict, ms: dict) -> int:
        """Run a single milestone through Planner → Wave(Builder → Verifier)."""
        ms_num = ms["milestone"]
        self._progress(f"=== Milestone {ms_num}: {ms.get('goal', '')} ===")
        logger.info("=== Milestone %d: %s ===", ms_num, ms.get("goal", ""))

        # Phase A: Planning (if no tasks yet)
        if not ms.get("tasks"):
            if self.dry_run:
                logger.info("[DRY RUN] Would run Planner for milestone %d", ms_num)
                return 0

            rc = self._run_planner(data, ms)
            if rc != 0:
                return rc

            # Reload - planner wrote tasks to milestones.json
            data, ms = self._reload_milestone(data, ms_num)

            # Check questions after planner
            if self.from_skill and self.has_pending_questions(data):
                return EXIT_QUESTIONS_PENDING

        # Phase B: Wave loop (while-loop to handle fix tasks and retries)
        round_count = 0
        while round_count < self.max_rounds:
            # Always reload to pick up verifier's fix tasks / done updates
            data, ms = self._reload_milestone(data, ms_num)
            tasks = ms.get("tasks", [])

            if not tasks:
                logger.error(
                    "Milestone %d has no tasks after planning. "
                    "Planner may have failed to generate tasks or ask questions.",
                    ms_num,
                )
                return 1

            undone = [t for t in tasks if not t.get("done")]
            if not undone:
                break  # All tasks done

            # Find the lowest wave with undone tasks
            current_wave = min(t.get("wave", 1) for t in undone)
            wave_tasks = [t for t in undone if t.get("wave") == current_wave]

            self._progress(f"--- Wave {current_wave} ({len(wave_tasks)} tasks) ---")
            logger.info("--- Wave %d (%d tasks) ---", current_wave, len(wave_tasks))

            if self.dry_run:
                for t in wave_tasks:
                    logger.info(
                        "  [DRY RUN] Would build: %s - %s",
                        t["id"], t.get("description", ""),
                    )
                # In dry-run, advance by marking as if done to avoid infinite loop
                break

            # Run Builders in parallel
            rc = asyncio.run(self._run_builders(data, ms, wave_tasks))
            if rc != 0:
                return rc

            # Reload and check questions after builders
            data, ms = self._reload_milestone(data, ms_num)
            if self.from_skill and self.has_pending_questions(data):
                return EXIT_QUESTIONS_PENDING

            # Determine if milestone will be complete after this wave
            tasks_after = ms.get("tasks", [])
            undone_after_build = [
                t for t in tasks_after
                if not t.get("done") and t.get("wave") != current_wave
            ]
            is_milestone_complete = len(undone_after_build) == 0

            # Run Verifier
            rc = self._run_verifier(
                data, ms, wave_tasks, current_wave, is_milestone_complete
            )
            if rc != 0:
                return rc

            # Reload and check questions after verifier
            data, ms = self._reload_milestone(data, ms_num)
            if self.from_skill and self.has_pending_questions(data):
                return EXIT_QUESTIONS_PENDING

            round_count += 1

        # Final reload to check completion
        data, ms = self._reload_milestone(data, ms_num)
        undone = [t for t in ms.get("tasks", []) if not t.get("done")]
        if not undone:
            ms["done"] = True
            self.save_milestones(data)
            self._progress(f"=== Milestone {ms_num} 完了 ===")
            logger.info("=== Milestone %d completed ===", ms_num)
        else:
            logger.warning(
                "Milestone %d has %d undone tasks after %d rounds",
                ms_num, len(undone), round_count,
            )
        return 0

    # --- Agent Runners ---

    @staticmethod
    def _fmt_elapsed(seconds: float) -> str:
        """Format elapsed seconds as human-readable string."""
        m, s = divmod(int(seconds), 60)
        if m > 0:
            return f"{m}m{s:02d}s"
        return f"{s}s"

    def _run_planner(self, data: dict, ms: dict) -> int:
        """Run the Planner agent for a milestone."""
        self._progress(f"Planner 開始 (Milestone {ms['milestone']})")
        logger.info("Running Planner for milestone %d...", ms["milestone"])

        prompt = self._build_planner_prompt(data, ms)
        t0 = time.monotonic()
        rc, _ = self._invoke_claude(
            prompt,
            session_name=f"planner-m{ms['milestone']}",
            cwd=self.root,
        )
        elapsed = self._fmt_elapsed(time.monotonic() - t0)
        if rc == 0:
            self._progress(f"Planner 完了 ({elapsed})")
            logger.info("Planner completed (%s)", elapsed)
        else:
            self._progress(f"Planner 失敗 ({elapsed})")
            logger.error("Planner failed (%s)", elapsed)
        return rc

    async def _run_builders(
        self, data: dict, ms: dict, wave_tasks: list[dict]
    ) -> int:
        """Run Builder agents in parallel using worktrees."""
        sem = asyncio.Semaphore(self.max_parallel)
        total = len(wave_tasks)
        completed = 0
        t0 = time.monotonic()

        async def run_one(task: dict) -> int:
            nonlocal completed
            async with sem:
                rc = await self._run_single_builder(data, ms, task)
                completed += 1
                elapsed = self._fmt_elapsed(time.monotonic() - t0)
                status = "ok" if rc == 0 else f"FAILED(rc={rc})"
                self._progress(
                    f"Builder [{completed}/{total}] {task['id']}: {status} ({elapsed})"
                )
                logger.info(
                    "Builder [%d/%d] %s: %s (%s)",
                    completed, total, task["id"], status, elapsed,
                )
                return rc

        coros = [run_one(t) for t in wave_tasks]
        results = await asyncio.gather(*coros)

        elapsed = self._fmt_elapsed(time.monotonic() - t0)
        # Check for failures
        failures = [
            (t, rc)
            for t, rc in zip(wave_tasks, results)
            if rc != 0
        ]
        if failures:
            self._progress(f"Builders: {len(failures)}/{total} 失敗 ({elapsed})")
            logger.error(
                "Builders finished with %d/%d failures (%s)",
                len(failures), total, elapsed,
            )
        else:
            self._progress(f"Builders: 全 {total} 件完了 ({elapsed})")
            logger.info("All %d builders completed (%s)", total, elapsed)
        return 0

    async def _run_single_builder(
        self, data: dict, ms: dict, task: dict
    ) -> int:
        """Run a single Builder agent in a worktree."""
        task_id = task["id"]

        # Skip guard: re-check if task is already done (e.g. from a previous run)
        if task.get("done"):
            logger.info("Builder %s already done, skipping", task_id)
            return 0

        prompt = self._build_builder_prompt(data, ms, task)
        worktree_name = f"sefirot-{task_id}"

        cmd = [
            "claude", "-p",
            "-w", worktree_name,
            "--output-format", "stream-json",
            "--model", self.model,
            "--dangerously-skip-permissions",
            "--verbose",
            "--team-name", f"sefirot-{task_id}",
            prompt,
        ]

        logfile = self.sessions_dir / f"builder-{task_id}.log"

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        try:
            shell_cmd = self._build_shell_command(cmd, logfile)
            proc = await asyncio.create_subprocess_shell(
                shell_cmd,
                cwd=str(self.root),
                env=env,
            )

            # Wait for completion with periodic heartbeat
            t0 = time.monotonic()
            while proc.returncode is None:
                try:
                    await asyncio.wait_for(proc.wait(), timeout=30)
                except asyncio.TimeoutError:
                    elapsed_s = time.monotonic() - t0
                    if elapsed_s >= self.session_timeout:
                        proc.kill()
                        await proc.wait()
                        logger.error("Builder %s timed out after %ds", task_id, self.session_timeout)
                        return 1
                    elapsed = self._fmt_elapsed(elapsed_s)
                    self._progress(f"  builder-{task_id} 実行中... ({elapsed})")

            if proc.returncode != 0:
                stderr_tail = logfile.read_text(encoding="utf-8", errors="replace")[-500:] if logfile.exists() else ""
                logger.error(
                    "Builder %s failed (rc=%d): %s",
                    task_id, proc.returncode, stderr_tail,
                )
            else:
                # Mark task done with lock (reload-modify-save to prevent race)
                await self._save_milestones_locked(task_id)

            return proc.returncode or 0

        except Exception:
            logger.exception("Builder %s unexpected error", task_id)
            return 1

    def _run_verifier(
        self,
        data: dict,
        ms: dict,
        wave_tasks: list[dict],
        current_wave: int,
        is_milestone_complete: bool,
    ) -> int:
        """Run the Verifier agent."""
        done_tasks = [t for t in wave_tasks if t.get("done")]
        if not done_tasks:
            logger.warning("No completed tasks for Verifier to process")
            return 0

        self._progress(f"Verifier 開始 ({len(done_tasks)} tasks)")
        logger.info("Running Verifier for %d tasks...", len(done_tasks))

        prompt = self._build_verifier_prompt(
            data, ms, done_tasks, is_milestone_complete
        )

        t0 = time.monotonic()
        rc, _ = self._invoke_claude(
            prompt,
            session_name=f"verifier-m{ms['milestone']}-w{current_wave}",
            cwd=self.root,
        )
        elapsed = self._fmt_elapsed(time.monotonic() - t0)
        if rc == 0:
            self._progress(f"Verifier 完了 ({elapsed})")
            logger.info("Verifier completed (%s)", elapsed)
        else:
            self._progress(f"Verifier 失敗 ({elapsed})")
            logger.error("Verifier failed (%s)", elapsed)
        return rc

    # --- Claude Invocation ---

    def _invoke_claude(
        self,
        prompt: str,
        *,
        session_name: str,
        cwd: Path,
    ) -> tuple[int, str]:
        """Invoke Claude Code in pipe mode. Returns (returncode, stdout).

        Runs the subprocess asynchronously so we can emit periodic heartbeat
        logs while waiting, making progress visible in background execution.
        """
        cmd = [
            "claude", "-p",
            "--output-format", "stream-json",
            "--model", self.model,
            "--dangerously-skip-permissions",
            "--verbose",
            "--team-name", f"sefirot-{session_name}",
            prompt,
        ]

        logfile = self.sessions_dir / f"{session_name}.log"

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        async def _run() -> tuple[int, str]:
            shell_cmd = self._build_shell_command(cmd, logfile)
            proc = await asyncio.create_subprocess_shell(
                shell_cmd,
                cwd=str(cwd),
                env=env,
            )
            t0 = time.monotonic()

            while proc.returncode is None:
                try:
                    await asyncio.wait_for(proc.wait(), timeout=30)
                except asyncio.TimeoutError:
                    elapsed = self._fmt_elapsed(time.monotonic() - t0)
                    self._progress(f"  {session_name} 実行中... ({elapsed})")

            if proc.returncode != 0:
                stderr_tail = logfile.read_text(encoding="utf-8", errors="replace")[-500:] if logfile.exists() else ""
                logger.error(
                    "%s failed (rc=%d): %s",
                    session_name, proc.returncode, stderr_tail,
                )

            stdout_data = logfile.read_text(encoding="utf-8", errors="replace") if logfile.exists() else ""
            return proc.returncode or 0, stdout_data

        return asyncio.run(_run())

    # --- Prompt Building ---

    def _load_prompt_template(self, name: str) -> str:
        """Load a prompt template file."""
        path = self.prompts_dir / f"{name}.md"
        if not path.exists():
            logger.error("Prompt template not found: %s", path)
            sys.exit(1)
        return path.read_text(encoding="utf-8")

    def _question_queue_section(self, agent: str) -> str:
        """Generate question queue instructions. Empty when not --from-skill."""
        if not self.from_skill:
            return ""

        if agent == "planner":
            examples = (
                "- 設計ドキュメントに未決事項（どの機能を追加するか、どの方式を採用するか等）が明記されている\n"
                "- 要件が曖昧で、解釈次第で設計が大きく異なる\n"
                "- 技術選定やアーキテクチャ方針について設計者の判断が必要"
            )
        elif agent == "builder":
            examples = (
                "- Ambiguous requirements where both interpretations lead to significantly different implementations\n"
                "- Missing information that cannot be inferred from the design doc or existing code\n"
                "- Contradictions between the design doc and existing code that require human judgment"
            )
        else:
            examples = (
                "- Merge conflicts where both sides have valid but incompatible changes\n"
                "- Test failures that suggest a design-level problem requiring human decision\n"
                "- Ambiguities in how to resolve integration issues between multiple builders' work"
            )

        ms_path = str(self.milestones_file)

        # Builder runs in a worktree, so it must use the absolute path
        # to write to the main repo's milestones.json (not the worktree copy).
        if agent == "builder":
            path_note = (
                "作業をブロックする重大な疑問がある場合、**メインリポジトリの** "
                f"`{ms_path}` の `questions` 配列に質問を追加してください。\n\n"
                "**重要**: worktree 内の milestones.json ではなく、上記の絶対パスのファイルに書き込むこと。\n\n"
            )
        else:
            path_note = (
                "作業をブロックする重大な疑問がある場合、"
                f"`{ms_path}` の `questions` 配列に質問を追加してください。\n\n"
            )

        return (
            "## 質問キュー\n\n"
            "このセッションはユーザーとの対話チャネルが有効です。\n"
            f"{path_note}"
            '```json\n'
            f'{{"agent": "{agent}", "task_id": "<your-task-id>", '
            '"question": "質問内容", "timestamp": "<ISO datetime>"}\n'
            '```\n\n'
            "質問すべきケース:\n"
            f"{examples}\n\n"
            "**自分で合理的に判断できることで質問してはならない。**\n"
        )

    def _build_planner_prompt(self, data: dict, ms: dict) -> str:
        """Build prompt for the Planner agent."""
        template = self._load_prompt_template("planner")
        source_doc = data.get("source", "")

        # Read source design doc if it exists
        source_content = ""
        if source_doc:
            # source can be absolute or relative to task_dir
            source_path = self.root / self.task_dir / source_doc
            if not source_path.exists():
                # Try as absolute path from root (legacy format)
                source_path = self.root / source_doc
            if source_path.exists():
                source_content = source_path.read_text(encoding="utf-8")

        source_dir = self._source_dir()

        replacements = {
            "__MILESTONE_NUMBER__": str(ms["milestone"]),
            "__MILESTONE_GOAL__": ms.get("goal", ""),
            "__MILESTONE_VERIFICATION__": ms.get("verification", ""),
            "__SOURCE_DOC__": source_doc,
            "__SOURCE_CONTENT__": source_content,
            "__SOURCE_DIR__": source_dir,
            "__MILESTONES_JSON_PATH__": str(self.milestones_file),
            "__CLAUDE_MD_SECTION__": self._claude_md_content,
            "__QUESTION_QUEUE_SECTION__": self._question_queue_section("planner"),
        }

        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        return prompt

    def _build_builder_prompt(self, data: dict, ms: dict, task: dict) -> str:
        """Build prompt for a Builder agent."""
        template = self._load_prompt_template("builder")

        # Read plan doc if it exists
        plan_content = ""
        plan_doc = ms.get("plan_doc", "")
        if plan_doc:
            plan_path = self.root / plan_doc
            if plan_path.exists():
                plan_content = plan_path.read_text(encoding="utf-8")

        replacements = {
            "__MILESTONE_NUMBER__": str(ms["milestone"]),
            "__MILESTONE_GOAL__": ms.get("goal", ""),
            "__TASK_ID__": task["id"],
            "__TASK_DESCRIPTION__": task.get("description", ""),
            "__PLAN_DOC__": plan_doc,
            "__PLAN_CONTENT__": plan_content,
            "__SESSIONS_DIR__": str(self.sessions_dir),
            "__MILESTONES_JSON_PATH__": str(self.milestones_file),
            "__CLAUDE_MD_SECTION__": self._claude_md_content,
            "__QUESTION_QUEUE_SECTION__": self._question_queue_section("builder"),
        }

        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        return prompt

    def _build_verifier_prompt(
        self,
        data: dict,
        ms: dict,
        done_tasks: list[dict],
        is_milestone_complete: bool,
    ) -> str:
        """Build prompt for the Verifier agent."""
        template = self._load_prompt_template("verifier")

        # Provide task IDs - verifier discovers actual branch names via git
        task_ids = [t["id"] for t in done_tasks]

        # Collect handoff notes from builder logs
        handoff_notes = self._collect_handoff_notes(done_tasks)

        replacements = {
            "__MILESTONE_NUMBER__": str(ms["milestone"]),
            "__MILESTONE_GOAL__": ms.get("goal", ""),
            "__MILESTONE_VERIFICATION__": ms.get("verification", ""),
            "__BRANCHES__": "\n".join(f"- sefirot-{tid}" for tid in task_ids),
            "__TASK_SUMMARY__": "\n".join(
                f"- {t['id']}: {t.get('description', '')}" for t in done_tasks
            ),
            "__HANDOFF_NOTES__": handoff_notes,
            "__IS_MILESTONE_COMPLETE__": "true" if is_milestone_complete else "false",
            "__MILESTONES_JSON_PATH__": str(self.milestones_file),
            "__CLAUDE_MD_SECTION__": self._claude_md_content,
            "__QUESTION_QUEUE_SECTION__": self._question_queue_section("verifier"),
        }

        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        return prompt

    def _collect_handoff_notes(self, tasks: list[dict]) -> str:
        """Collect handoff notes from builder session logs."""
        notes = []
        for task in tasks:
            logfile = self.sessions_dir / f"builder-{task['id']}.log"
            if not logfile.exists():
                continue
            # Try to extract last result message from stream-json
            try:
                for line in logfile.read_text(encoding="utf-8").splitlines():
                    try:
                        event = json.loads(line)
                        if event.get("type") == "result":
                            result_text = event.get("result", "")
                            if result_text:
                                notes.append(f"### {task['id']}\n{result_text}")
                    except json.JSONDecodeError:
                        continue
            except Exception:
                continue
        return "\n\n".join(notes) if notes else "(No handoff notes available)"

