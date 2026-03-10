# Toy プログラム作成

## 目的

sefirot 開発者が、Planner → Builder → Verifier ループ（特に並列実行）が正しく動作することを、簡単なプログラムで検証するため。

## 概要

`src/toy/` 配下に、独立した小規模プログラムを 8 個作成する。各プログラムは 1 ファイル + 1 テストファイルの構成とし、プログラム間に依存関係を持たせない。これにより、sefirot の Wave 並列実行（最大 8 並列）を検証できる。

## ディレクトリ構成

```
src/toy/
├── __init__.py
├── fizzbuzz.py
├── fibonacci.py
├── factorial.py
├── palindrome.py
├── caesar.py
├── prime.py
├── reverse.py
└── binary_search.py

tests/toy/
├── __init__.py
├── test_fizzbuzz.py
├── test_fibonacci.py
├── test_factorial.py
├── test_palindrome.py
├── test_caesar.py
├── test_prime.py
├── test_reverse.py
└── test_binary_search.py
```

## 各プログラムの仕様

### 1. fizzbuzz.py

- `fizzbuzz(n: int) -> list[str]`: 1 から n までの FizzBuzz 結果をリストで返す
  - 3 の倍数 → "Fizz"、5 の倍数 → "Buzz"、両方 → "FizzBuzz"、それ以外 → 数字の文字列

### 2. fibonacci.py

- `fibonacci(n: int) -> list[int]`: 先頭 n 個のフィボナッチ数列を返す（0, 1, 1, 2, 3, 5, ...）
- `fib(n: int) -> int`: n 番目のフィボナッチ数を返す（0-indexed）

### 3. factorial.py

- `factorial(n: int) -> int`: n の階乗を返す。負の数は ValueError。

### 4. palindrome.py

- `is_palindrome(s: str) -> bool`: 文字列が回文かどうかを返す（大文字小文字無視、空白無視）

### 5. caesar.py

- `encrypt(text: str, shift: int) -> str`: シーザー暗号で暗号化。英字のみ対象、他の文字はそのまま。
- `decrypt(text: str, shift: int) -> str`: 復号。

### 6. prime.py

- `is_prime(n: int) -> bool`: 素数判定
- `primes_up_to(n: int) -> list[int]`: n 以下の素数一覧（エラトステネスの篩）

### 7. reverse.py

- `reverse_string(s: str) -> str`: 文字列を反転
- `reverse_words(s: str) -> str`: 単語の順序を反転（"hello world" → "world hello"）

### 8. ????.py

- 実装時に考えるので他のプログラムを実装する前に質問してほしい。

## テスト方針

- 各テストファイルで正常系・境界値・異常系をカバーする
- 実行コマンド: `pytest tests/toy/`

## 備考

- このコードは sefirot の動作テスト用であり、テスト完了後に削除する前提
- プログラム間に依存関係はない（全て独立して並列実装可能）
