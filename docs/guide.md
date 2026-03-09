# Sefirot 使い方ガイド

## クイックスタート

### 1. インストール

```bash
uv tool install sefirot
```

### 2. プロジェクトで初期化

```bash
cd your-project
sefirot init
```

これにより以下が作成される:
- `.sefirot/` - デフォルト設定付きの状態ディレクトリ
- `.claude/skills/sefirot/SKILL.md` - Claude Codeスキル
- `.mcp.json` - MCPサーバー登録
- `.claude/settings.json` - コンテキスト監視用フック

### 3. 作業開始

```bash
claude
```

Claude Code内で`/sefirot`と入力してPMモードを起動。

## ワークフロー例

### 計画

```
あなた: /sefirot
あなた: ユーザーモジュールにOAuth2認証を追加したい。

PMエージェント: マイルストーンとタスクに分解します...
  M-001: OAuth2認証
    TASK-001: 認証フローの設計（spec）
    TASK-002: OAuth2プロバイダーの実装（implement）
    TASK-003: 認証テストの作成（test）
    TASK-004: セキュリティレビュー（review）
```

### 実行

PMエージェントが`sefirot_spawn`でサブエージェントを起動:
- 各サブエージェントは独自のgit worktreeを取得
- それぞれバックグラウンドで独立して作業

### ブロックされたタスクの処理

サブエージェントが質問を持つ場合:
1. タスクファイルに質問を書き込み、ステータスを`blocked`に設定
2. sefirotデーモンがこれを検知し、通知をキューに追加
3. PMエージェントが`sefirot_queue()`で通知を取得
4. PMがあなたに伝える: 「TASK-002がブロックされています。再開: `sefirot resume TASK-002`」
5. 別のターミナルで: `sefirot resume TASK-002`
6. 質問に直接回答すると、サブエージェントが作業を継続

### 状態の確認

シェルから（AI不要）:

```bash
sefirot status
```

またはClaude Code内でPMエージェントが`sefirot_status()`を呼び出す。

### 完了した作業のマージ

タスクが完了すると、PMエージェントが`sefirot_merge(task_id)`を呼び出し、worktreeブランチをmainにマージ。

## カスタマイズ

### PMロール

`.sefirot/config/main-agent.md`を編集して、PMエージェントの振る舞いをカスタマイズ。

### サブエージェントプロンプト

`.sefirot/config/agents/`内のファイルを編集:
- `implement.md` - 実装エージェント
- `test.md` - テストエージェント
- `review.md` - レビューエージェント
- `spec.md` - 仕様エージェント

### コンテキスト管理

セッションが大きくなると、sefirotがPreCompactフックでコンテキスト圧迫を検知し、新しいセッションの開始を提案する。状態は`.sefirot/`ファイルに保存されているため、新しいセッションで`/sefirot`を呼び出せばそこから再開できる。
