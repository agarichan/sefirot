# Sefirot アーキテクチャ

## 概要

Sefirot は Claude Code の上に構築されたマルチエージェントオーケストレーションフレームワーク。Planner / Builder / Verifier の3エージェントが Milestone 単位で設計→実装→検証のループを自動で回す。人間は設計の承認とエージェントからの質問への回答だけを行う。

構成要素は CLI（Python）と Claude Code スキルの2つ。外部サーバーやデーモンは不要。すべての状態は `milestones.json`（タスクディレクトリ内、git 管理）と設計ドキュメント（Markdown、git 管理）で管理される。

## アーキテクチャ図

```
┌────────────────────────────────────────────────────┐
│          Claude Code（ユーザーセッション）             │
│                                                    │
│  /plan      設計ドキュメント作成（対話形式）           │
│  /milestone  milestones.json 生成                   │
│  /loop      sefirot loop --from-skill を実行         │
│             質問があればユーザーに確認して再開          │
└──────────────────────┬─────────────────────────────┘
                       │ subprocess
                       ▼
┌────────────────────────────────────────────────────┐
│          sefirot loop（LoopEngine）                  │
│                                                    │
│  ┌─ Planner ──────────────────────────────┐        │
│  │  claude -p で起動（main repo）           │        │
│  │  → 設計ドキュメント + tasks 生成          │        │
│  └────────────────────────────────────────┘        │
│           ↓                                        │
│  ┌─ Builder × N ─────────────────────────┐        │
│  │  claude -p -w sefirot-{task_id} で起動  │        │
│  │  → 各 worktree で並列実装（最大8）       │        │
│  │  → タスクごとにコミット                   │        │
│  └────────────────────────────────────────┘        │
│           ↓                                        │
│  ┌─ Verifier ────────────────────────────┐        │
│  │  claude -p で起動（main repo）           │        │
│  │  → ブランチを順次マージ                   │        │
│  │  → テスト・リント・型チェック             │        │
│  │  → 失敗時は fix task 生成               │        │
│  │  → worktree/ブランチのクリーンアップ      │        │
│  └────────────────────────────────────────┘        │
└────────────────────────────────────────────────────┘
```

## コンポーネント

### CLI (`cli.py`)

`pyproject.toml` で `sefirot` として登録されたエントリーポイント。

| コマンド | 目的 |
|---|---|
| `sefirot loop` | Planner → Builder → Verifier ループを実行 |
| `sefirot status` | milestones.json の状態を表示 |
| `sefirot questions` | 保留中の質問を表示・クリア |

### LoopEngine (`loop.py`)

オーケストレーションのコア。Milestone ごとに以下を実行する:

1. **Planner フェーズ** — タスクが未生成なら Planner を起動。設計ドキュメント（タスクディレクトリ内）とタスク一覧を生成し、`milestones.json` に書き込む。
2. **Wave ループ** — 未完了タスクを Wave 番号順に処理:
   - **Builder フェーズ**: 同一 Wave のタスクを asyncio で並列実行。各 Builder は `claude -p -w sefirot-{task_id}` で worktree 内で動作する。
   - **Verifier フェーズ**: Builder 完了後、Verifier がブランチをマージし検証する。失敗時は fix task を追加。
3. **完了判定** — 全タスク完了で Milestone を done にマーク。

### スキル

`npx skills add agarichan/sefirot` でインストールされる3つのスキル:

| スキル | 説明 |
|---|---|
| `/plan` | 対話形式で設計ドキュメントを作成 → `docs/tasks/{name}/design.md` に出力 |
| `/milestone` | 設計ドキュメントから `milestones.json` を生成（同ディレクトリに配置） |
| `/loop` | `sefirot loop --from-skill` を実行し、質問があればユーザーに確認 |

### プロンプトテンプレート

3つのエージェント用テンプレート。変数置換（`__TASK_ID__` 等）でプロンプトを組み立てる。

| テンプレート | エージェント | 主な内容 |
|---|---|---|
| `planner.md` | Planner | 設計ドキュメント作成、タスク分割 |
| `builder.md` | Builder | 1タスクの実装、セルフチェック、コミット |
| `verifier.md` | Verifier | マージ、検証、fix task 生成 |

探索順: `.sefirot/prompts/` → `.claude/skills/sefirot-loop/prompts/` → パッケージ内蔵

## Wave システム

Builder は Wave 単位で並列実行される。同一 Wave 内のタスクはファイル競合しない前提。

- **W1**: 型定義・インターフェース（契約のみ）
- **W2-W4**: 並列実装（同一ファイル編集は別 Wave）
- **W5**: テスト・統合

Verifier は Wave 完了後に検証レベルを調整する:
- W1 のみ: 検証スキップ（契約のみ）
- 中間 Wave: 基本チェック（lint、型、ユニットテスト）
- Milestone 最終 Wave: フルチェック（E2E 含む）

## 通信フロー

エージェント同士が直接通信することはない。すべての通信は `milestones.json` と設計ドキュメントを介して行われる:

1. **LoopEngine → エージェント**: プロンプトを stdin で送信。設計ドキュメントのパスや milestones.json の絶対パスを含む。
2. **Builder → Verifier**: コミットメッセージの「申し送り」セクションとセッションログ（stream-json）の result イベントで情報を受け渡す。
3. **エージェント → ユーザー**: `milestones.json` の `questions` 配列に質問を書き込む。LoopEngine が検知して exit code 10 で停止し、スキルがユーザーに質問を提示する。

## 質問キュー

`--from-skill` モードで有効。Planner/Builder/Verifier が判断に迷った場合の流れ:

1. エージェントが `milestones.json` の `questions` 配列に質問を追加
2. LoopEngine が検知し exit code 10 で停止
3. `/loop` スキルが質問をユーザーに提示
4. 回答を設計ドキュメントの該当タスクセクションに「追加指示」として追記
5. `questions` をクリアしてコミット
6. ループ再開

## Git Worktree 戦略

各 Builder は競合を避けるため、独立した worktree で作業する:

1. `claude -p -w sefirot-{task_id}` が worktree を自動作成
2. Builder が worktree 内で実装・コミット
3. Verifier が `main` にマージし、worktree とブランチを削除

## ディレクトリ構造

```
project/
├── docs/tasks/
│   └── 20260310_1430_OAuth2認証設計/           # タスクディレクトリ
│       ├── design.md                           # 設計ドキュメント（/plan で生成）
│       ├── milestones.json                     # Milestone 状態（/milestone で生成）
│       ├── plan-m1.md                          # Planner が生成
│       └── plan-m2.md
├── .sefirot/
│   ├── sessions/
│   │   └── 20260310_1430_OAuth2認証設計/       # タスクごと
│   │       ├── planner-m1.log                  # stream-json 形式
│   │       ├── builder-{task_id}.log
│   │       ├── verifier-m1-w1.log
│   │       └── {YYYYMMDD_HHMM}_{作業内容}.md   # Builder の作業記録
│   └── prompts/                                # カスタムプロンプト（任意）
├── .claude/skills/
│   ├── sefirot-plan/SKILL.md
│   ├── sefirot-milestone/SKILL.md
│   └── sefirot-loop/
│       ├── SKILL.md
│       └── prompts/                            # スキル同梱プロンプト
└── src/sefirot/                                # パッケージソース
    ├── cli.py                                  # CLI エントリーポイント
    ├── loop.py                                 # LoopEngine
    └── templates/prompts/                      # デフォルトプロンプト
```

## 実装

- **言語**: Python 3.11+
- **依存関係**: `click`（CLI のみ）
- **パッケージエントリ**: `[project.scripts] sefirot = "sefirot.cli:main"`
- **ソースレイアウト**: `src/sefirot/` 配下に `cli.py`、`loop.py`、`templates/`
- **外部依存**: Claude Code CLI（`claude` コマンド）

## 定数

| 定数 | 値 | 説明 |
|---|---|---|
| `EXIT_QUESTIONS_PENDING` | 10 | 質問保留時の終了コード |
| `DEFAULT_MAX_PARALLEL` | 8 | Builder の最大並列数 |
| `DEFAULT_MAX_ROUNDS` | 50 | 1回の実行あたりの最大ラウンド数 |
| `DEFAULT_SESSION_TIMEOUT` | 1800 | エージェントセッションのタイムアウト（秒） |
| `DEFAULT_MODEL` | opus | 使用する Claude モデル |
