# Milestone 2: fizzbuzz の異常系・境界値テスト追加とエラーハンドリング実装

## 概要

既存の `src/toy/fizzbuzz.py` に異常入力のエラーハンドリングを追加し、`tests/toy/test_fizzbuzz.py` に正常系・境界値・異常系を網羅するテストを追加する。

## タスク一覧

| ステップ | タスクID | Wave | 概要 |
|----------|----------|------|------|
| A | enhance-fizzbuzz-tests | W1 | fizzbuzz のエラーハンドリング追加とテスト拡充 |

## タスク詳細

### ステップ A: enhance-fizzbuzz-tests（Wave 1）

#### 編集するファイル
- `src/toy/fizzbuzz.py`（既存ファイルを編集）
- `tests/toy/test_fizzbuzz.py`（既存ファイルを編集）

#### 型定義・インターフェース

関数シグネチャは変更なし:

```python
# src/toy/fizzbuzz.py
def fizzbuzz(n: int) -> list[str]:
    """1 から n までの FizzBuzz 結果をリストで返す。"""
    ...
```

#### エラーハンドリング仕様

`fizzbuzz` 関数の先頭に以下のバリデーションを追加する:

```python
def fizzbuzz(n: int) -> list[str]:
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    # n == 0 の場合は空リスト [] を返す（既存ロジックで対応済み）
    ...
```

- `n` が整数でない場合 → `TypeError("n must be an integer")`
- `n` が負の場合 → `ValueError("n must be non-negative")`
- `n == 0` の場合 → 空リスト `[]` を返す（既存の `range(1, n + 1)` で自然に空リストになる）
- `bool` は `int` のサブクラスのため、`isinstance(n, bool)` で明示的に除外する

#### import 先（既存コード）

なし。外部ライブラリや既存コードへの依存はない。

#### テスト仕様

```python
# tests/toy/test_fizzbuzz.py
import pytest
from toy.fizzbuzz import fizzbuzz
```

以下のテストケースを実装する（既存の 5 テストは維持）:

**正常系（既存テスト — 変更不要）:**

| テスト関数名 | 入力 | 期待値 | 備考 |
|-------------|------|--------|------|
| `test_fizzbuzz_15` | `fizzbuzz(15)` | 15要素のリスト | 既存 |
| `test_fizz` | `fizzbuzz(3)` | `result[2] == "Fizz"` | 既存 |
| `test_buzz` | `fizzbuzz(5)` | `result[4] == "Buzz"` | 既存 |
| `test_fizzbuzz_element` | `fizzbuzz(15)` | `result[14] == "FizzBuzz"` | 既存 |

**境界値（既存 1 + 新規 2）:**

| テスト関数名 | 入力 | 期待値 | 備考 |
|-------------|------|--------|------|
| `test_fizzbuzz_boundary` | `fizzbuzz(1)` | `["1"]` | 既存 |
| `test_fizzbuzz_zero` | `fizzbuzz(0)` | `[]` | **新規** |
| `test_fizzbuzz_large` | `fizzbuzz(30)` | 長さ30, `result[29] == "FizzBuzz"` | **新規** — 30は15の倍数 |

**異常系（全て新規）:**

| テスト関数名 | 入力 | 期待例外 | 備考 |
|-------------|------|----------|------|
| `test_fizzbuzz_negative` | `fizzbuzz(-1)` | `ValueError` | **新規** |
| `test_fizzbuzz_float` | `fizzbuzz(3.5)` | `TypeError` | **新規** |
| `test_fizzbuzz_string` | `fizzbuzz("abc")` | `TypeError` | **新規** |
| `test_fizzbuzz_none` | `fizzbuzz(None)` | `TypeError` | **新規** |
| `test_fizzbuzz_bool` | `fizzbuzz(True)` | `TypeError` | **新規** |

異常系テストは `pytest.raises` を使用する:

```python
def test_fizzbuzz_negative():
    with pytest.raises(ValueError):
        fizzbuzz(-1)

def test_fizzbuzz_float():
    with pytest.raises(TypeError):
        fizzbuzz(3.5)

def test_fizzbuzz_string():
    with pytest.raises(TypeError):
        fizzbuzz("abc")

def test_fizzbuzz_none():
    with pytest.raises(TypeError):
        fizzbuzz(None)

def test_fizzbuzz_bool():
    with pytest.raises(TypeError):
        fizzbuzz(True)
```

#### 実装パターン

- エラーハンドリング: Milestone 1 の `fibonacci.py` を参考にする（同プロジェクトの `src/toy/fibonacci.py` に同様のバリデーションパターンがあれば踏襲）
- テスト: 既存の `test_fizzbuzz.py` のスタイルを踏襲し、末尾にテストを追加する

#### 注意事項

- `pyproject.toml` の `pythonpath = ["src"]` により、import は `from toy.fizzbuzz import fizzbuzz` で行う
- `pyproject.toml` は変更不要
- 既存テスト 5 件は変更せず維持すること
- `pytest` は既存の import 文で取り込み済み
