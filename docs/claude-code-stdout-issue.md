# Claude Code バックグラウンドタスクの stdout 消失問題

## 現象

Claude Code の Bash ツールで `run_in_background: true` を使ってコマンドを実行すると、出力が `/private/tmp/claude-{uid}/.../tasks/{task_id}.output` にキャプチャされる。

しかし、そのコマンド内で `claude -p`（子プロセス）を起動すると、**この出力ファイルが削除される**。結果、バックグラウンドタスクの完了通知を受け取っても出力が空（ファイル不在）になる。

## 原因

子 `claude` プロセスが起動時に親プロセスの stdout キャプチャファイルを削除する。これは Claude Code の内部挙動であり、`CLAUDECODE` 環境変数の有無に関わらず発生する。

関連 Issue:
- [#17011: run_in_background=true Task agents silently lose all output](https://github.com/anthropics/claude-code/issues/17011)（closed as "not planned"）
- [#22711: Background task's output file not accessible](https://github.com/anthropics/claude-code/issues/22711)（open）

## CLAUDECODE 環境変数のジレンマ

Claude Code 内で子 `claude` プロセスを起動する際、`CLAUDECODE=1` が親から継承される。

- **`CLAUDECODE=1` を残す**: 子 `claude` が「ネストされたセッション」として起動を拒否する
  ```
  Error: Claude Code cannot be launched inside another Claude Code session.
  ```
- **`CLAUDECODE` を除外する**: 子 `claude` は起動するが、自分がトップレベルだと認識して stdout を乗っ取る

→ **解決策**: `env -u CLAUDECODE` で除外しつつ、子プロセスの stdout/stderr はログファイルにリダイレクト（`> logfile 2>&1`）する。

## ワークアラウンド: stdout キャプチャファイルの再作成

sefirot では以下のワークアラウンドで対処している:

### 1. 起動時に stdout キャプチャファイルのパスを特定

```python
import subprocess, os

result = subprocess.run(
    ["lsof", "-p", str(os.getpid()), "-a", "-d", "1", "-Fn"],
    capture_output=True, text=True, timeout=5,
)
stdout_capture = None
for line in result.stdout.splitlines():
    if line.startswith("n/"):
        stdout_capture = line[1:]
        break
```

`lsof` で自プロセスの fd 1（stdout）が指すファイルパスを取得する。macOS では `readlink /dev/fd/1` が使えないため `lsof` を使用。

### 2. 進捗ログを専用ファイルに書く

子 `claude` が stdout を破壊するため、進捗は専用ファイル（`loop-output.log`）に書く:

```python
self._output_log = sessions_dir / "loop-output.log"
self._output_fh = open(self._output_log, "w", encoding="utf-8")
```

### 3. 書き込みのたびにキャプチャファイルを再作成

```python
import shutil

def _sync_stdout_capture(self):
    if self._stdout_capture and self._output_log.exists():
        shutil.copy2(self._output_log, self._stdout_capture)
```

子 `claude` がキャプチャファイルを削除しても、`_emit()` のたびに進捗ログの内容でファイルを再作成する。これにより Claude Code のバックグラウンドタスク UI にログが表示される。

### シェルスクリプトでの実装例

```bash
# stdout キャプチャファイルのパスを特定
OUTPUT_FILE=$(lsof -p $$ -a -d 1 -Fn 2>/dev/null | grep '^n' | head -1 | cut -c2-)

# 進捗は別ファイルに書く
PROGRESS_LOG="/tmp/my-progress.log"
log() { echo "[$(date '+%H:%M:%S')] $*" >> "$PROGRESS_LOG"; }

# claude を起動（stdout はログファイルにリダイレクト）
env -u CLAUDECODE claude -p "prompt" < /dev/null > /tmp/claude.log 2>&1 &
PID=$!

# 出力ファイルが消されたら再作成
while kill -0 $PID 2>/dev/null; do
    if [ -n "$OUTPUT_FILE" ] && [ ! -e "$OUTPUT_FILE" ]; then
        cp "$PROGRESS_LOG" "$OUTPUT_FILE"
    fi
    sleep 1
done
wait $PID

# 最終結果を書き込む
cp "$PROGRESS_LOG" "$OUTPUT_FILE"
```

### 子プロセスの環境変数設定

```bash
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT \
    CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 \
    claude -p --model opus --verbose \
    --output-format stream-json \
    --dangerously-skip-permissions \
    "$prompt" < /dev/null > "$logfile" 2>&1
```

- `-u CLAUDECODE`: ネストセッションガードを回避
- `-u CLAUDE_CODE_ENTRYPOINT`: 追加の初期化ロジックを回避（[#26190](https://github.com/anthropics/claude-code/issues/26190)）
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`: チーム機能を有効化
- `< /dev/null`: stdin を切断して親の I/O を保護
- `> "$logfile" 2>&1`: 子の出力を専用ログに隔離
