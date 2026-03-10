# Milestone 1: FizzBuzz 実装とディレクトリ構成の作成

## 概要

`src/toy/` と `tests/toy/` のパッケージ構成を作成し、fizzbuzz.py を実装してテストが通る状態にする。

## タスク一覧

| ステップ | タスク ID | Wave | 概要 |
|---|---|---|---|
| A | setup-and-impl-fizzbuzz | 1 | ディレクトリ構成の作成と FizzBuzz の実装・テスト |

## タスク詳細

### ステップ A: setup-and-impl-fizzbuzz（Wave 1）

#### 作成するファイル

- `src/toy/__init__.py`
- `src/toy/fizzbuzz.py`
- `tests/toy/__init__.py`
- `tests/toy/test_fizzbuzz.py`

#### 型定義・インターフェース

```python
# src/toy/fizzbuzz.py

def fizzbuzz(n: int) -> list[str]:
    """1 から n までの FizzBuzz 結果をリストで返す。

    - 3 の倍数 → "Fizz"
    - 5 の倍数 → "Buzz"
    - 3 と 5 の両方の倍数 → "FizzBuzz"
    - それ以外 → 数字の文字列（例: "1", "2", "4"）

    Args:
        n: 正の整数

    Returns:
        長さ n のリスト
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `src/toy/__init__.py` と `tests/toy/__init__.py` は空ファイル（パッケージ初期化のみ）
- `fizzbuzz` 関数は純粋関数として実装する。ループで 1 から n まで回し、条件分岐で文字列を決定してリストに追加するシンプルな実装でよい

#### テスト仕様

`tests/toy/test_fizzbuzz.py` で以下をカバーする:

```python
import pytest
from toy.fizzbuzz import fizzbuzz
```

- **正常系**: `fizzbuzz(15)` の結果が正しいこと（"1", "2", "Fizz", "4", "Buzz", ..., "14", "FizzBuzz"）
- **境界値**: `fizzbuzz(1)` → `["1"]`
- **Fizz のみ**: 3 番目の要素が `"Fizz"` であること
- **Buzz のみ**: 5 番目の要素が `"Buzz"` であること
- **FizzBuzz**: 15 番目の要素が `"FizzBuzz"` であること

#### 注意事項

- `pytest tests/toy/` で実行するため、`src/toy/` が Python パスに含まれている必要がある。`pyproject.toml` の `[tool.hatch.build.targets.wheel]` には `src/sefirot` のみ指定されているが、`pytest` は `src/` をルートとして認識するため、`from toy.fizzbuzz import fizzbuzz` で import できる。もし import エラーが発生する場合は `pyproject.toml` の `testpaths` 設定や `pythonpath` 設定を確認すること
