# Sefirot

Claude Code を使ったマルチエージェント自律開発フレームワーク。

Planner / Builder / Verifier の3エージェントが、設計 → 実装 → 検証のループを自動で回す。
人間は設計の承認と、エージェントからの質問への回答だけを行う。

## アーキテクチャ

```
/sefirot-plan          設計ドキュメント作成（人間と対話）
     ↓
/sefirot-milestone     Milestone分割（milestones.json生成）
     ↓
/sefirot-loop          自律ループ開始
  ├─ Planner   タスク分割 + 詳細設計書作成
  ├─ Builder × N  worktree並列実装（最大8並列）
  ├─ Verifier  マージ + 品質検証 + fix task生成
  └─ (質問があればユーザーに確認して再開)
```

### Wave システム（依存制御）

Builder は Wave 単位で並列実行される。

- **W1**: 型定義・インターフェース（契約）
- **W2-W4**: 並列実装（同一ファイル編集は別Wave）
- **W5**: テスト・統合

## インストール

### スキル（`/sefirot-plan`, `/sefirot-milestone`, `/sefirot-loop`）

```bash
npx skills add agarichan/sefirot
```

### CLI（`sefirot loop` コマンド）

```bash
uv tool install git+https://github.com/agarichan/sefirot.git
```

## 使い方

### 1. 設計ドキュメントを作成する

Claude Code 内で:

```
/plan ユーザー認証機能を追加する
```

対話形式で要件を詰め、`docs/tasks/YYYYMMDD_HHMM_作業名/design.md` に設計ドキュメントが作成される。

### 2. Milestone を生成する

```
/milestone docs/tasks/20260310_1430_ユーザー認証設計/design.md
```

`docs/tasks/20260310_1430_ユーザー認証設計/milestones.json` が生成される:

```json
{
  "source": "design.md",
  "milestones": [
    {
      "milestone": 1,
      "goal": "メールアドレスでサインアップ・ログインができ、セッションが維持される",
      "verification": "pytest",
      "done": false,
      "tasks": []
    }
  ]
}
```

### 3. ループを実行する

#### Claude Code 内から（推奨）

```
/sefirot-loop
```

質問が発生すると自動的にユーザーに確認し、回答を設計書に反映して再開する。

#### CLI から直接

```bash
# 全 Milestone を実行
sefirot loop

# 特定の Milestone のみ
sefirot loop -m 1

# 実行計画の確認（実際には実行しない）
sefirot loop --dry-run

# Claude Code Skill から呼ぶ場合（質問キュー有効）
sefirot loop --from-skill
```

### 4. 状態を確認する

```bash
sefirot status
```

```
[    ] Milestone 1: メールアドレスでサインアップ・ログインができる  (3/5 tasks)
  [x] W1 define-auth-types: 認証関連の型定義
  [x] W2 impl-auth-service: 認証サービス実装
  [x] W2 impl-auth-api: 認証APIエンドポイント実装
  [ ] W3 impl-auth-ui: ログイン/サインアップUI
  [ ] W4 integration-test: 統合テスト
```

## 質問キュー（`--from-skill` モード）

`/sefirot-loop` 経由で実行すると、Planner/Builder/Verifier が判断に迷った場合に `milestones.json` の `questions` 配列に質問を書き込む。

```json
{
  "questions": [
    {
      "agent": "builder",
      "task_id": "impl-auth-service",
      "question": "パスワードのハッシュ化に bcrypt と argon2 のどちらを使うべきですか？",
      "timestamp": "2026-03-10T14:30:00"
    }
  ]
}
```

ループはプロセスを停止し（exit code 10）、呼び出し元のスキルがユーザーに質問を提示する。回答は設計ドキュメントに反映され、ループが再開される。

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `sefirot loop` | Planner → Builder → Verifier ループを実行 |
| `sefirot status` | milestones.json の状態を表示 |
| `sefirot questions` | 保留中の質問を表示・クリア |

### `sefirot loop` オプション

| オプション | デフォルト | 説明 |
|---|---|---|
| `--from-skill` | false | Skill から呼ばれた場合に有効。質問キューで停止する |
| `-m`, `--milestone` | 全て | 特定の Milestone のみ実行 |
| `--dry-run` | false | 実行計画を表示するのみ |
| `--max-parallel` | 8 | Builder の最大並列数 |
| `--model` | opus | 使用する Claude モデル |
| `--task-dir` | 自動探索 | タスクディレクトリの指定（`docs/tasks/` 配下から自動探索） |

## プロンプトのカスタマイズ

`.sefirot/prompts/` にプロンプトファイルを配置するとカスタマイズできる。
パッケージのデフォルトよりローカルコピーが優先される。

- `planner.md` - 設計・タスク分割の方針
- `builder.md` - 実装の進め方・コミット規約
- `verifier.md` - マージ・検証・修正の判断基準

## 前提条件

- Python 3.11+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) がインストール済み
- Git リポジトリ内で実行すること

## 参考

- [claude-looper](https://github.com/jujunjun110/claude-looper) - worktree を使った並列ビルドの着想元
