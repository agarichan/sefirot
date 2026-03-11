# CLAUDE.md

## プロジェクト概要

sefirot は Claude Code 上のマルチエージェントオーケストレーションフレームワーク。
Planner / Builder / Verifier の3エージェントが Milestone 単位で設計→実装→検証のループを自動で回す。

## Lint

```bash
ty check src/ tests/
```

- コード変更後は `ty check` を実行して型エラーがないことを確認する

## 検証コマンド

```bash
pytest tests/
```

## ファイル構成と同期ルール

プロンプトテンプレートとスキル定義は以下の3箇所に存在する:

| 場所 | 役割 | git 追跡 |
|------|------|----------|
| `skills/` | **本体（Source of Truth）** | o |
| `src/sefirot/templates/prompts/` | パッケージ同梱テンプレート | o |
| `.claude/skills/` | ローカルインストール先 | x（.gitignore） |

### 同期ルール

- **編集は `skills/` と `src/sefirot/templates/prompts/` の両方に行う**
- `.claude/skills/` は `skills/` からインストールされるため、直接編集しない
- プロンプトテンプレート（planner.md, builder.md, verifier.md）は `skills/sefirot-loop/prompts/` と `src/sefirot/templates/prompts/` で同一内容を維持すること
- SKILL.md は `skills/{スキル名}/SKILL.md` が本体
