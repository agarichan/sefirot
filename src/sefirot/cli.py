"""CLI entry point for sefirot."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from sefirot.state import SefirotState


def _find_root() -> Path:
    """Find project root (directory containing .sefirot/ or .git/)."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".sefirot").is_dir() or (parent / ".git").is_dir():
            return parent
    return cwd


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """Sefirot - Claude Codeマルチエージェント開発オーケストレーションフレームワーク。

    人間が判断し、AIが実装する半自動ワークフローを提供します。
    """
    pass


@main.command()
def init() -> None:
    """現在のプロジェクトにsefirotを初期化する。"""
    from sefirot.installer import init_project

    root = Path.cwd()
    actions = init_project(root)
    click.echo("Sefirot initialized:")
    for action in actions:
        click.echo(f"  - {action}")
    click.echo()
    click.echo("Next: run `claude` and use `/sefirot` to activate PM mode.")


@main.command()
def deinit() -> None:
    """現在のプロジェクトからsefirotを削除する。"""
    from sefirot.installer import deinit_project

    root = _find_root()
    if not (root / ".sefirot").is_dir():
        click.echo("Not a sefirot project.", err=True)
        sys.exit(1)

    click.confirm("Remove sefirot from this project?", abort=True)

    actions = deinit_project(root)
    if actions:
        click.echo("Sefirot removed:")
        for action in actions:
            click.echo(f"  - {action}")
    else:
        click.echo("Nothing to remove.")


@main.command()
@click.option("--format", "fmt", type=click.Choice(["table", "markdown"]), default="table")
@click.option("--filter", "status_filter", default=None, help="Filter by status")
def status(fmt: str, status_filter: str | None) -> None:
    """タスクの状態を表示する。"""
    root = _find_root()
    state = SefirotState(root)

    if not state.is_initialized():
        click.echo("Not a sefirot project. Run `sefirot init` first.", err=True)
        sys.exit(1)

    tasks = state.list_tasks(status=status_filter)

    if not tasks:
        if fmt == "markdown":
            click.echo("No active tasks yet.")
        else:
            click.echo("No tasks found.")
        return

    if fmt == "markdown":
        click.echo("| ID | Title | Status | Type | Milestone |")
        click.echo("|---|---|---|---|---|")
        for t in tasks:
            click.echo(f"| {t.id} | {t.title} | {t.status} | {t.type} | {t.milestone or '-'} |")
    else:
        # Table format
        click.echo(f"{'ID':<10} {'Title':<40} {'Status':<12} {'Type':<10} {'Milestone':<10}")
        click.echo("-" * 82)
        for t in tasks:
            click.echo(
                f"{t.id:<10} {t.title[:40]:<40} {t.status:<12} {t.type:<10} {(t.milestone or '-'):<10}"
            )


@main.command()
@click.argument("task_id")
def resume(task_id: str) -> None:
    """タスクのサブエージェントセッションを再開する。"""
    root = _find_root()
    state = SefirotState(root)

    if not state.is_initialized():
        click.echo("Not a sefirot project. Run `sefirot init` first.", err=True)
        sys.exit(1)

    task = state.get_task(task_id.upper())
    if task is None:
        click.echo(f"Task {task_id} not found.", err=True)
        sys.exit(1)

    if not task.session_id:
        click.echo(f"Task {task.id} has no session ID.", err=True)
        sys.exit(1)

    # Change to worktree directory if available (sessions are saved per-cwd)
    if task.worktree and Path(task.worktree).is_dir():
        os.chdir(task.worktree)
        click.echo(f"Resuming session for {task.id} in {task.worktree}")
    else:
        click.echo(f"Resuming session for {task.id}: {task.title}")

    os.execvp("claude", ["claude", "--resume", task.session_id])


@main.command()
def serve() -> None:
    """MCPサーバーを起動する（.mcp.json経由でClaude Codeから呼び出される）。"""
    from sefirot.server import run_server

    run_server()


@main.group(name="mcp")
def mcp_group() -> None:
    """MCPサーバー管理コマンド。"""
    pass


def _find_mcp_pids() -> list[int]:
    """Find PIDs of running sefirot serve processes."""
    import subprocess as sp

    result = sp.run(["pgrep", "-f", "sefirot serve"], capture_output=True, text=True)
    return [
        int(p) for p in result.stdout.strip().split("\n")
        if p.strip() and int(p) != os.getpid()
    ]


def _kill_mcp(pids: list[int]) -> int:
    """Kill the given PIDs. Returns number killed."""
    import signal

    killed = 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            click.echo(f"Killed sefirot serve (PID {pid})")
            killed += 1
        except ProcessLookupError:
            pass
    return killed


@mcp_group.command()
def stop() -> None:
    """MCPサーバーを停止する。"""
    pids = _find_mcp_pids()
    if not pids:
        click.echo("No running sefirot MCP server found.")
        return
    _kill_mcp(pids)


@mcp_group.command()
def restart() -> None:
    """MCPサーバーを再起動する（停止後、Claude Codeで /mcp reconnect）。"""
    pids = _find_mcp_pids()
    if pids:
        _kill_mcp(pids)
    else:
        click.echo("No running sefirot MCP server found.")
    click.echo("Use `/mcp` in Claude Code to reconnect.")


@main.group()
def hook() -> None:
    """フックハンドラー（Claude Codeフックから呼び出される）。"""
    pass


@hook.command("pre-compact")
def hook_pre_compact() -> None:
    """PreCompactフック処理 - コンテキスト圧迫を通知する。"""
    root = _find_root()
    queue_file = root / ".sefirot" / "queue.json"
    import json
    from datetime import datetime

    data: list = []
    if queue_file.exists():
        data = json.loads(queue_file.read_text(encoding="utf-8"))

    data.append({
        "type": "context_pressure",
        "message": "Context is getting large. Consider checkpointing and starting a fresh session.",
        "timestamp": datetime.now().isoformat(),
    })
    queue_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@hook.command("stop")
def hook_stop() -> None:
    """Stopフック処理 - エージェント応答完了。"""
    # Currently a no-op, reserved for future use (e.g., auto-queue check)
    pass


if __name__ == "__main__":
    main()
