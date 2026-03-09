# Sefirot 使い方ガイド

## クイックスタート

### 1. インストール

スキル（`/plan`, `/milestone`, `/loop`）:

```bash
npx skills add agarichan/sefirot
```

CLI（`sefirot loop` コマンド）:

```bash
uv tool install git+https://github.com/agarichan/sefirot.git
```

### 2. 作業開始

```bash
claude
```

## ワークフロー

### Step 1: 設計ドキュメント作成

Claude Code 内で `/plan` を実行:

```
/plan ユーザーモジュールにOAuth2認証を追加したい
```

対話形式で要件を詰め、`docs/tasks/YYYYMMDD_HHMM_作業名/design.md` に設計ドキュメントが作成される。

### Step 2: Milestone 生成

```
/milestone docs/tasks/20260310_1430_OAuth2認証設計/design.md
```

設計ドキュメントから `.sefirot/milestones.json` が生成される。各 Milestone は検証可能な単位に分割され、tasks は空の状態で作成される（Planner が後で埋める）。

### Step 3: ループ実行

#### Claude Code 内から（推奨）

```
/loop
```

質問が発生すると自動的にユーザーに確認し、回答を設計書に反映して再開する。

#### CLI から直接

```bash
sefirot loop              # 全 Milestone を実行
sefirot loop -m 1         # 特定の Milestone のみ
sefirot loop --dry-run    # 実行計画の確認のみ
```

### Step 4: 状態確認

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

## ループの流れ

```
/loop
 ├─ Milestone ごとに:
 │   ├─ Planner: タスク分割 + 詳細設計書作成
 │   ├─ Wave ごとに:
 │   │   ├─ Builder × N: worktree 並列実装（最大8並列）
 │   │   ├─ Verifier: マージ + 品質検証
 │   │   └─ (失敗時は fix task を追加して再ループ)
 │   └─ Milestone 完了
 └─ 全 Milestone 完了
```

### 質問が発生した場合

Planner/Builder/Verifier が判断に迷うと `.sefirot/milestones.json` に質問を書き込み、ループが停止する（exit code 10）。

`/loop` 経由の場合、スキルがユーザーに質問を提示し、回答を設計ドキュメントに反映してループを再開する:

```
[質問 1/1] from builder (task: impl-auth-service)
パスワードのハッシュ化に bcrypt と argon2 のどちらを使うべきですか？
```

回答は設計ドキュメントの該当タスクセクションに「追加指示」として永続化される。

## ファイル構成

```
docs/tasks/
  20260310_1430_OAuth2認証設計/
    design.md              ← /plan で生成（git 管理）
    milestone-1.md         ← Planner が生成（git 管理）
    milestone-2.md

.sefirot/
  milestones.json          ← ランタイム状態（git 管理外）
  sessions/
    20260310_1430_OAuth2認証設計/  ← ライフサイクルごと
      planner-m1.log
      builder-{task_id}.log
      ...
```

## カスタマイズ

### プロンプト

`.sefirot/prompts/` にプロンプトファイルを配置するとカスタマイズできる。パッケージデフォルトよりローカルコピーが優先される。

- `planner.md` - 設計・タスク分割の方針
- `builder.md` - 実装の進め方・コミット規約
- `verifier.md` - マージ・検証・修正の判断基準

プロンプトの探索順:

1. `.sefirot/prompts/` （プロジェクトローカル）
2. `.claude/skills/sefirot-loop/prompts/` （skills でインストールされたもの）
3. パッケージ内蔵テンプレート（フォールバック）

## 前提条件

- Python 3.11+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) がインストール済み
- Git リポジトリ内で実行すること
