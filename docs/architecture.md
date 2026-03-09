# Sefirot アーキテクチャ

## 概要

SefirotはClaude Codeの上に構築された薄いオーケストレーションレイヤーで、マルチエージェント開発ワークフローを半自動化します。基本哲学は**人間が判断し、AIが実装する**こと。完全な自律ではなく、人間を意思決定者として維持しつつ、エージェントの起動・コンテキストの受け渡し・タスク状態の追跡にかかる手間を削減します。

Sefirotは汎用フレームワーク（プロジェクト固有ではない）で、CLI・MCPサーバー・バックグラウンドデーモンの3つで構成されます。すべての状態は`.sefirot/`配下のMarkdownファイルに保存されるため、確認・バージョン管理・セッション間の復旧が可能です。

## アーキテクチャ図

```
┌──────────────────────────────────────────────────────┐
│            Claude Code（メインエージェント）            │
│                                                      │
│  /sefirot スキルでPMロールを読み込み                     │
│  - マイルストーンとタスクを計画                          │
│  - sefirot MCPツールでサブエージェントを起動              │
│  - ユーザーと対話（Claude Code標準のUX）                 │
│  - スラッシュコマンド、画像、フックにフルアクセス           │
└──────────┬──────────────────────────┬────────────────┘
           │ MCPツール呼び出し         │ フック（HTTP）
           ▼                          ▼
┌──────────────────────────────────────────────────────┐
│         sefirot（MCPサーバー + デーモン）               │
│                                                      │
│  MCPツール:                                          │
│    sefirot_spawn    - worktree作成＋サブエージェント開始 │
│    sefirot_status   - 全タスク状態の一覧                │
│    sefirot_queue    - 通知キューの取得                  │
│    sefirot_checkpoint - マイルストーンの記録             │
│    sefirot_decide   - 意思決定の記録                    │
│    sefirot_merge    - worktreeのマージ                 │
│                                                      │
│  デーモン:                                            │
│    - .sefirot/tasks/ のファイル変更を監視               │
│    - ブロック状態のサブエージェントを検出→通知をキューに追加│
│    - PreCompactフックを受信→リセット推奨フラグを設定     │
└──────────┬───────────────────────────────────────────┘
           │ claude -p（非対話モード）
           ▼
┌──────────────────────────────────────────────────────┐
│        サブエージェント（Claude Codeセッション）         │
│  - 各エージェントは独自のgit worktreeで作業              │
│  - .sefirot/tasks/TASK-xxx.md にステータスを書き込み     │
│  - ブロック時は質問を記録して停止                        │
│  - ユーザーが直接再開可能: claude --resume <id>          │
└──────────────────────────────────────────────────────┘
```

## コンポーネント

### CLI (`cli.py`)

pyproject.tomlで`sefirot`として登録されたエントリーポイント。

| コマンド              | 目的                                              |
|----------------------|--------------------------------------------------|
| `sefirot init`       | プロジェクトにsefirotを導入（後述）                   |
| `sefirot status`     | 全タスクの状態を表示（ファイル読み取りのみ、AI不要）     |
| `sefirot resume <id>`| session_idを検索して`claude --resume`を実行          |
| `sefirot serve`      | MCPサーバーを起動（Claude Codeから呼び出される）       |

`sefirot init`が生成・変更するもの:
- `.sefirot/` デフォルト設定付きのディレクトリ構造
- `.mcp.json` -- sefirot MCPサーバーの登録
- `.claude/settings.json` -- PreCompactとStopフックの追加
- `.claude/skills/sefirot/SKILL.md` -- `/sefirot`スキルファイル
- `CLAUDE.md`は**変更しない**

### MCPサーバー (`server.py`)

stdio transportを使用するPython MCP SDKサーバー。メインエージェントがClaude Code内から呼び出す6つのツールを提供。また、Claude Codeからのフックイベント（PreCompact、Stop）を受信するHTTPエンドポイントも公開。

### デーモン (`daemon.py`)

watchdogを使って`.sefirot/tasks/`のファイル変更を監視。サブエージェントがタスクファイルに`status: blocked`を書き込むと、デーモンが通知キューにエントリを追加。メインエージェントは`sefirot_queue()`で取得。

### 状態管理 (`state.py`)

すべての状態は`.sefirot/`配下にYAMLフロントマター付きMarkdownとして保存:

```
.sefirot/
├── config/
│   ├── main-agent.md          # PMロール定義（カスタマイズ可能）
│   └── agents/
│       ├── implement.md       # 実装サブエージェント用プロンプト
│       ├── test.md            # テストサブエージェント用プロンプト
│       ├── review.md          # レビューサブエージェント用プロンプト
│       └── spec.md            # 仕様サブエージェント用プロンプト
├── project.md                 # プロジェクト概要
├── milestones.md              # マイルストーン一覧
├── decisions.md               # 意思決定ログ
├── tasks/                     # タスクごとに1ファイル（TASK-xxx.md）
├── specs/                     # 仕様書
└── sessions.json              # セッションIDマッピング
```

タスクファイルのフロントマタースキーマ:

```yaml
id: TASK-001
status: pending | in_progress | blocked | completed | failed
type: implement | spec | test | review
session_id: <claude-session-id>
worktree: .sefirot/worktrees/TASK-001
milestone: M-001
```

サブエージェントがブロックされると、質問セクションを追記。ユーザーがセッションを再開して直接回答するか、メインエージェントが判断を中継する。

## 通信フロー

エージェント同士が直接通信することはない。すべての通信は`.sefirot/`ファイルを介して行われる:

1. **メインエージェント → サブエージェント**: `sefirot_spawn()`がタスクファイルを作成し、`.sefirot/config/agents/*.md`を参照する指示で`claude -p`を起動。
2. **サブエージェント → メインエージェント**: サブエージェントがタスクファイルにステータス更新を書き込む。デーモンが変更を検知し、通知キューに追加。
3. **メインエージェントのポーリング**: メインエージェントが`sefirot_queue()`を呼び出し、ブロックされたタスク・完了した作業・コンテキストリセットの提案を確認。
4. **ユーザーの介入**: ユーザーが別のターミナルで`claude --resume <session-id>`を実行し、ブロックされたサブエージェントと直接対話可能。

## スキルベースの起動

Sefirotは`CLAUDE.md`を変更しない。代わりに`.claude/skills/sefirot/SKILL.md`にスキルファイルをインストール:

```markdown
---
name: sefirot
description: Activate sefirot orchestration system.
---

!`cat .sefirot/config/main-agent.md`

## Current Project State
!`sefirot status --format=markdown 2>/dev/null || echo "No active tasks yet."`
```

ユーザーが`/sefirot`と入力すると、Claude Codeがこのスキルを読み込み:
- `.sefirot/config/main-agent.md`からPMロールを動的に読み取り
- `sefirot status`で現在のタスク状態を注入
- プロジェクトごとに`config/main-agent.md`を独自にカスタマイズ可能

## コンテキスト管理

長いセッションではコンテキストが蓄積される。SefirotはPreCompactフックでこれに対応:

1. コンテキスト圧迫が高まるとClaude Codeが`PreCompact`を発火。
2. フックがsefirotのHTTPエンドポイントにアクセスし、リセット推奨フラグを設定。
3. 次の`sefirot_queue()`呼び出し時にメインエージェントがフラグを受信。
4. メインエージェントが現在の状態を`.sefirot/`に保存し、新しいセッションの開始を提案。
5. 新セッションが`.sefirot/`ファイルと`sefirot_status()`から状態を復元。

`Stop`フックはセッション終了イベントをキャプチャし、sefirotが`sessions.json`のセッション追跡を更新できるようにする。

## Git Worktree戦略

各サブエージェントは競合を避けるため、独立したgit worktreeで作業:

1. `sefirot_spawn()`が`git worktree add`を呼び出し、タスク用のworktreeを作成（`worktree.py`が管理）。
2. サブエージェント（`claude -p`）がそのworktree内で実行。
3. タスク完了時、`sefirot_merge()`がworktreeブランチをメインブランチにマージ。
4. マージ後にworktreeをクリーンアップ。

これにより、複数のサブエージェントが異なるタスクを並列で作業しても、互いの変更を上書きしない。

## 実装

- **言語**: Python
- **依存関係**: `mcp`（MCP SDK）、`watchdog`（ファイル監視）、`pyyaml`（フロントマター解析）、`click`（CLI）
- **パッケージエントリ**: `[project.scripts] sefirot = "sefirot.cli:main"`
- **ソースレイアウト**: `src/sefirot/` 配下にcli、server、daemon、state、worktree、spawner、installer、templatesの各モジュール
