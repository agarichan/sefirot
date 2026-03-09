# Milestone 1: 8つの独立した toy プログラムの実装

## 概要

`src/toy/` 配下に 8 つの独立した小規模プログラム（fizzbuzz, fibonacci, factorial, palindrome, caesar, prime, reverse, binary_search）を実装し、それぞれのテストを `tests/toy/` に作成する。全テストが `pytest tests/toy/` で pass することがゴール。

## タスク一覧

| ステップ | タスクID | Wave | 概要 |
|----------|----------|------|------|
| A | setup-toy-packages | W1 | src/toy/ と tests/toy/ のパッケージ初期化 |
| B | impl-fizzbuzz | W2 | fizzbuzz の実装とテスト |
| C | impl-fibonacci | W2 | fibonacci の実装とテスト |
| D | impl-factorial | W2 | factorial の実装とテスト |
| E | impl-palindrome | W2 | palindrome の実装とテスト |
| F | impl-caesar | W2 | caesar の実装とテスト |
| G | impl-prime | W2 | prime の実装とテスト |
| H | impl-reverse | W2 | reverse の実装とテスト |
| I | impl-binary-search | W2 | binary_search の実装とテスト |

## タスク詳細

### ステップ A: setup-toy-packages（Wave 1）

`src/toy/` と `tests/toy/` の `__init__.py` を作成し、パッケージとして認識されるようにする。

#### 作成するファイル
- `src/toy/__init__.py`
- `tests/toy/__init__.py`

#### 型定義・インターフェース

```python
# src/toy/__init__.py
# 空ファイル（パッケージマーカー）
```

```python
# tests/toy/__init__.py
# 空ファイル（パッケージマーカー）
```

#### import 先（既存コード）

なし

#### 実装パターン

既存の `tests/__init__.py` と同じパターン（空ファイル）。

#### 注意事項

- ディレクトリ `src/toy/` と `tests/toy/` が存在しない場合は作成すること

---

### ステップ B: impl-fizzbuzz（Wave 2）

FizzBuzz プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/fizzbuzz.py`
- `tests/toy/test_fizzbuzz.py`

#### 型定義・インターフェース

```python
# src/toy/fizzbuzz.py

def fizzbuzz(n: int) -> list[str]:
    """1 から n までの FizzBuzz 結果をリストで返す。

    - 3 の倍数 → "Fizz"
    - 5 の倍数 → "Buzz"
    - 3 と 5 の両方の倍数 → "FizzBuzz"
    - それ以外 → 数字の文字列（例: "1", "2"）

    Args:
        n: 正の整数

    Returns:
        FizzBuzz 結果の文字列リスト（長さ n）
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

単純なループ処理。外部依存なし。

#### テスト仕様

```python
# tests/toy/test_fizzbuzz.py

# 正常系
# - fizzbuzz(1) == ["1"]
# - fizzbuzz(3) == ["1", "2", "Fizz"]
# - fizzbuzz(5) で "Buzz" が含まれる
# - fizzbuzz(15) で "FizzBuzz" が含まれる
# - fizzbuzz(15) のリスト長が 15

# 境界値
# - fizzbuzz(0) == []

# 異常系（任意）
# - 負の数の扱い
```

---

### ステップ C: impl-fibonacci（Wave 2）

フィボナッチ数列プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/fibonacci.py`
- `tests/toy/test_fibonacci.py`

#### 型定義・インターフェース

```python
# src/toy/fibonacci.py

def fibonacci(n: int) -> list[int]:
    """先頭 n 個のフィボナッチ数列を返す。

    数列: 0, 1, 1, 2, 3, 5, 8, 13, ...

    Args:
        n: 取得する個数（0 以上の整数）

    Returns:
        フィボナッチ数列のリスト（長さ n）
    """

def fib(n: int) -> int:
    """n 番目のフィボナッチ数を返す（0-indexed）。

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, ...

    Args:
        n: インデックス（0 以上の整数）

    Returns:
        n 番目のフィボナッチ数
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

反復的な計算（再帰ではなくループ推奨）。

#### テスト仕様

```python
# tests/toy/test_fibonacci.py

# fibonacci 関数
# - fibonacci(0) == []
# - fibonacci(1) == [0]
# - fibonacci(2) == [0, 1]
# - fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]

# fib 関数
# - fib(0) == 0
# - fib(1) == 1
# - fib(10) == 55
```

---

### ステップ D: impl-factorial（Wave 2）

階乗プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/factorial.py`
- `tests/toy/test_factorial.py`

#### 型定義・インターフェース

```python
# src/toy/factorial.py

def factorial(n: int) -> int:
    """n の階乗を返す。

    Args:
        n: 0 以上の整数

    Returns:
        n!

    Raises:
        ValueError: n が負の数の場合
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

反復的な計算。負の数は `ValueError` を送出。

#### テスト仕様

```python
# tests/toy/test_factorial.py

# 正常系
# - factorial(0) == 1
# - factorial(1) == 1
# - factorial(5) == 120
# - factorial(10) == 3628800

# 異常系
# - factorial(-1) で ValueError が発生
```

---

### ステップ E: impl-palindrome（Wave 2）

回文判定プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/palindrome.py`
- `tests/toy/test_palindrome.py`

#### 型定義・インターフェース

```python
# src/toy/palindrome.py

def is_palindrome(s: str) -> bool:
    """文字列が回文かどうかを返す。

    大文字小文字を無視し、空白も無視して判定する。

    Args:
        s: 判定対象の文字列

    Returns:
        回文なら True、そうでなければ False
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

文字列を正規化（小文字化・空白除去）してから反転と比較。

#### テスト仕様

```python
# tests/toy/test_palindrome.py

# 正常系
# - is_palindrome("racecar") == True
# - is_palindrome("hello") == False
# - is_palindrome("A man a plan a canal Panama") == True（空白無視）
# - is_palindrome("Was It A Rat I Saw") == True（大文字小文字無視）

# 境界値
# - is_palindrome("") == True
# - is_palindrome("a") == True
```

---

### ステップ F: impl-caesar（Wave 2）

シーザー暗号プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/caesar.py`
- `tests/toy/test_caesar.py`

#### 型定義・インターフェース

```python
# src/toy/caesar.py

def encrypt(text: str, shift: int) -> str:
    """シーザー暗号で暗号化する。

    英字のみシフトし、他の文字（数字、記号、空白等）はそのまま残す。
    大文字・小文字は保持する。

    Args:
        text: 平文
        shift: シフト量（正の値で右シフト）

    Returns:
        暗号文
    """

def decrypt(text: str, shift: int) -> str:
    """シーザー暗号を復号する。

    encrypt の逆操作。decrypt(encrypt(text, n), n) == text が成立する。

    Args:
        text: 暗号文
        shift: シフト量

    Returns:
        平文
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

`ord()` / `chr()` を使ったアルファベットのシフト処理。`decrypt` は `encrypt(text, -shift)` で実装可能。

#### テスト仕様

```python
# tests/toy/test_caesar.py

# encrypt
# - encrypt("abc", 1) == "bcd"
# - encrypt("xyz", 3) == "abc"（ラップアラウンド）
# - encrypt("Hello, World!", 5) == "Mjqqt, Btwqi!"（大文字小文字保持、記号そのまま）

# decrypt
# - decrypt("bcd", 1) == "abc"
# - decrypt(encrypt("test", 13), 13) == "test"（ラウンドトリップ）

# 境界値
# - encrypt("", 5) == ""
# - encrypt("abc", 0) == "abc"
# - encrypt("abc", 26) == "abc"（26シフトで元に戻る）
```

---

### ステップ G: impl-prime（Wave 2）

素数判定・列挙プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/prime.py`
- `tests/toy/test_prime.py`

#### 型定義・インターフェース

```python
# src/toy/prime.py

def is_prime(n: int) -> bool:
    """素数判定。

    Args:
        n: 判定対象の整数

    Returns:
        素数なら True、そうでなければ False
    """

def primes_up_to(n: int) -> list[int]:
    """n 以下の素数一覧を返す（エラトステネスの篩）。

    Args:
        n: 上限値

    Returns:
        n 以下の素数のリスト（昇順）
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

- `is_prime`: 試し割り法（2 から √n まで）
- `primes_up_to`: エラトステネスの篩

#### テスト仕様

```python
# tests/toy/test_prime.py

# is_prime
# - is_prime(2) == True
# - is_prime(3) == True
# - is_prime(4) == False
# - is_prime(17) == True
# - is_prime(1) == False
# - is_prime(0) == False
# - is_prime(-5) == False

# primes_up_to
# - primes_up_to(10) == [2, 3, 5, 7]
# - primes_up_to(1) == []
# - primes_up_to(2) == [2]
# - primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

---

### ステップ H: impl-reverse（Wave 2）

文字列反転プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/reverse.py`
- `tests/toy/test_reverse.py`

#### 型定義・インターフェース

```python
# src/toy/reverse.py

def reverse_string(s: str) -> str:
    """文字列を反転する。

    Args:
        s: 対象の文字列

    Returns:
        反転した文字列
    """

def reverse_words(s: str) -> str:
    """単語の順序を反転する。

    "hello world" → "world hello"
    単語は空白で区切られたものとする。

    Args:
        s: 対象の文字列

    Returns:
        単語順が反転した文字列
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

- `reverse_string`: スライス `s[::-1]` で実装
- `reverse_words`: `split()` → `reverse` → `join` で実装

#### テスト仕様

```python
# tests/toy/test_reverse.py

# reverse_string
# - reverse_string("hello") == "olleh"
# - reverse_string("") == ""
# - reverse_string("a") == "a"
# - reverse_string("ab") == "ba"

# reverse_words
# - reverse_words("hello world") == "world hello"
# - reverse_words("one") == "one"
# - reverse_words("") == ""
# - reverse_words("a b c") == "c b a"
```

---

### ステップ I: impl-binary-search（Wave 2）

二分探索プログラムの実装とテスト。

#### 作成するファイル
- `src/toy/binary_search.py`
- `tests/toy/test_binary_search.py`

#### 型定義・インターフェース

```python
# src/toy/binary_search.py

def binary_search(arr: list[int], target: int) -> int:
    """ソート済みリストから target を二分探索する。

    Args:
        arr: 昇順にソートされた整数リスト
        target: 探索対象の値

    Returns:
        見つかった場合はそのインデックス、見つからない場合は -1
    """
```

#### import 先（既存コード）

なし（標準ライブラリのみ）

#### 実装パターン

標準的な二分探索アルゴリズム（while ループで low/high を狭めていく）。

#### テスト仕様

```python
# tests/toy/test_binary_search.py

# 正常系
# - binary_search([1, 2, 3, 4, 5], 3) == 2
# - binary_search([1, 2, 3, 4, 5], 1) == 0（先頭）
# - binary_search([1, 2, 3, 4, 5], 5) == 4（末尾）

# 見つからない場合
# - binary_search([1, 2, 3, 4, 5], 6) == -1
# - binary_search([1, 2, 3, 4, 5], 0) == -1

# 境界値
# - binary_search([], 1) == -1（空リスト）
# - binary_search([1], 1) == 0（要素1つ）
# - binary_search([1], 2) == -1
```

#### 注意事項

- `sample_task.md` の仕様セクション（### 8）は「????.py」だが、ディレクトリ構成では `binary_search.py` が明記されているため、binary_search を採用する
