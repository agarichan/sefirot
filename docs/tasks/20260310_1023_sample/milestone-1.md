# Milestone 1: fibonacci プログラムの実装

## 概要

`src/toy/` 配下に fibonacci（フィボナッチ数列）プログラムを実装し、対応するテストを作成する。ディレクトリ構成（`__init__.py`）も含めてセットアップする。

## タスク一覧

| ステップ | タスクID | Wave | 概要 |
|----------|----------|------|------|
| A | setup-and-impl-fibonacci | W1 | ディレクトリ構成作成と fibonacci 実装・テスト |

## タスク詳細

### ステップ A: setup-and-impl-fibonacci（Wave 1）

#### 作成するファイル

- `src/toy/__init__.py`
- `src/toy/fibonacci.py`
- `tests/toy/__init__.py`
- `tests/toy/test_fibonacci.py`

#### 型定義・インターフェース

```python
# src/toy/fibonacci.py

def fibonacci(n: int) -> list[int]:
    """先頭 n 個のフィボナッチ数列を返す。

    数列: 0, 1, 1, 2, 3, 5, 8, 13, ...

    Args:
        n: 取得する個数（0以上の整数）

    Returns:
        長さ n のリスト
    """
    ...

def fib(n: int) -> int:
    """n 番目のフィボナッチ数を返す（0-indexed）。

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, ...

    Args:
        n: 0以上の整数

    Returns:
        n 番目のフィボナッチ数
    """
    ...
```

#### `__init__.py` について

- `src/toy/__init__.py` — 空ファイル（パッケージ認識用）
- `tests/toy/__init__.py` — 空ファイル（パッケージ認識用）

#### import 先（既存コード）

なし。外部ライブラリや既存コードへの依存はない。

#### 実装パターン

- `fibonacci(n)`: n <= 0 で空リスト、n == 1 で `[0]`、それ以上はループで `result[-2] + result[-1]` を追加
- `fib(n)`: n <= 0 で 0 を返す。2 変数（a, b）のイテレーションで n 番目を計算

#### テスト仕様

```python
# tests/toy/test_fibonacci.py
import pytest
from toy.fibonacci import fibonacci, fib
```

以下のテストケースを実装する:

**`fibonacci` 関数:**

| テスト関数名 | 入力 | 期待値 | 分類 |
|-------------|------|--------|------|
| `test_fibonacci_7` | `fibonacci(7)` | `[0, 1, 1, 2, 3, 5, 8]` | 正常系 |
| `test_fibonacci_0` | `fibonacci(0)` | `[]` | 境界値 |
| `test_fibonacci_1` | `fibonacci(1)` | `[0]` | 境界値 |
| `test_fibonacci_2` | `fibonacci(2)` | `[0, 1]` | 境界値 |

**`fib` 関数:**

| テスト関数名 | 入力 | 期待値 | 分類 |
|-------------|------|--------|------|
| `test_fib_0` | `fib(0)` | `0` | 境界値 |
| `test_fib_1` | `fib(1)` | `1` | 境界値 |
| `test_fib_5` | `fib(5)` | `5` | 正常系 |
| `test_fib_10` | `fib(10)` | `55` | 正常系 |

#### 注意事項

- `pyproject.toml` の `pythonpath = ["src"]` により、import は `from toy.fibonacci import ...` で行う
- `pyproject.toml` は変更不要（既に設定済み）
