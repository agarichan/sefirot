"""Git worktree management."""

from __future__ import annotations

import subprocess
from pathlib import Path


class WorktreeManager:
    """Manages git worktrees for sub-agent task isolation."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.worktrees_dir = root / ".sefirot" / "worktrees"

    def create(self, task_id: str, base_branch: str = "HEAD") -> Path:
        """Create a new worktree for a task. Returns the worktree path."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"sefirot/{task_id}"

        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        return worktree_path

    def remove(self, task_id: str) -> None:
        """Remove a worktree and its branch for a task."""
        worktree_path = self.worktrees_dir / task_id
        branch_name = f"sefirot/{task_id}"
        if worktree_path.exists():
            subprocess.run(
                ["git", "worktree", "remove", str(worktree_path), "--force"],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
        # Delete the branch after removing the worktree
        subprocess.run(
            ["git", "branch", "-D", branch_name],
            cwd=self.root,
            capture_output=True,
            text=True,
        )

    def merge(self, task_id: str, target_branch: str = "main") -> str:
        """Merge a task's worktree branch into target. Returns merge output."""
        branch_name = f"sefirot/{task_id}"
        result = subprocess.run(
            ["git", "merge", branch_name, "--no-ff", "-m", f"Merge {task_id}"],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Merge failed: {result.stderr}")
        return result.stdout

    def list_worktrees(self) -> list[dict[str, str]]:
        """List all sefirot worktrees."""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        worktrees = []
        current: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
        if current:
            worktrees.append(current)

        # Filter to sefirot worktrees only
        return [
            w for w in worktrees
            if w.get("branch", "").startswith("refs/heads/sefirot/")
        ]

    def get_path(self, task_id: str) -> Path | None:
        """Get the worktree path for a task, if it exists."""
        path = self.worktrees_dir / task_id
        return path if path.exists() else None
