# Milestone 3: 全8プログラムの並列実装

## 概要

fizzbuzz 以外の残り7プログラム（fibonacci, factorial, palindrome, caesar, prime, reverse, binary_search）を全て並列実装し、`pytest tests/toy/` で全8プログラムのテストが通る状態にする。

## タスク一覧

| ステップ | タスク ID | Wave | 概要 |
|---|---|---|---|
| A | impl-fibonacci | 1 | フィボナッチ数列の実装とテスト |
| B | impl-factorial | 1 | 階乗関数の実装とテスト |
| C | impl-palindrome | 1 | 回文判定の実装とテスト |
| D | impl-caesar | 1 | シーザー暗号の実装とテスト |
| E | impl-prime | 1 | 素数判定・列挙の実装とテスト |
| F | impl-reverse | 1 | 文字列反転の実装とテスト |
| G | impl-binary-search | 1 | 二分探索の実装とテスト |

## タスク詳細

### ステップ A: impl-fibonacci（Wave 1）

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
        n: 取得する個数（0以上の整数）

    Returns:
        長さ n のリスト
    """

def fib(n: int) -> int:
    """n 番目のフィボナッチ数を返す（0-indexed）。

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, ...

    Args:
        n: 0以上の整数

    Returns:
        n 番目のフィボナッチ数
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- `fibonacci` はループで先頭 n 個を生成してリストに追加する
- `fib` は `fibonacci(n + 1)` の最後の要素を返す、またはループで直接計算する
- テストの import は `from toy.fibonacci import fibonacci, fib`

#### テスト仕様

```python
import pytest
from toy.fibonacci import fibonacci, fib
```

- **正常系**: `fibonacci(7)` → `[0, 1, 1, 2, 3, 5, 8]`
- **境界値**: `fibonacci(0)` → `[]`、`fibonacci(1)` → `[0]`、`fibonacci(2)` → `[0, 1]`
- **fib 関数**: `fib(0)` → `0`、`fib(1)` → `1`、`fib(5)` → `5`、`fib(10)` → `55`

#### 注意事項

なし。

---

### ステップ B: impl-factorial（Wave 1）

#### 作成するファイル
- `src/toy/factorial.py`
- `tests/toy/test_factorial.py`

#### 型定義・インターフェース

```python
# src/toy/factorial.py

def factorial(n: int) -> int:
    """n の階乗を返す。

    Args:
        n: 0以上の整数

    Returns:
        n!

    Raises:
        ValueError: n が負の数の場合
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- ループまたは再帰で実装する（ループ推奨）
- 負の数の場合は `ValueError` を送出する
- テストの import は `from toy.factorial import factorial`

#### テスト仕様

```python
import pytest
from toy.factorial import factorial
```

- **正常系**: `factorial(5)` → `120`、`factorial(10)` → `3628800`
- **境界値**: `factorial(0)` → `1`、`factorial(1)` → `1`
- **異常系**: `factorial(-1)` で `pytest.raises(ValueError)`

#### 注意事項

なし。

---

### ステップ C: impl-palindrome（Wave 1）

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
        s: 判定する文字列

    Returns:
        回文なら True
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- 文字列を小文字に変換し、空白を除去してから、反転したものと比較する
- テストの import は `from toy.palindrome import is_palindrome`

#### テスト仕様

```python
import pytest
from toy.palindrome import is_palindrome
```

- **正常系（回文）**: `is_palindrome("racecar")` → `True`
- **正常系（非回文）**: `is_palindrome("hello")` → `False`
- **大文字小文字混在**: `is_palindrome("RaceCar")` → `True`
- **空白含む**: `is_palindrome("A man a plan a canal Panama")` → `True`
- **境界値**: `is_palindrome("")` → `True`、`is_palindrome("a")` → `True`

#### 注意事項

なし。

---

### ステップ D: impl-caesar（Wave 1）

#### 作成するファイル
- `src/toy/caesar.py`
- `tests/toy/test_caesar.py`

#### 型定義・インターフェース

```python
# src/toy/caesar.py

def encrypt(text: str, shift: int) -> str:
    """シーザー暗号で暗号化する。

    英字のみシフトし、他の文字（数字、記号、空白等）はそのまま保持する。
    大文字は大文字のまま、小文字は小文字のままシフトする。

    Args:
        text: 平文
        shift: シフト量（正の値で右シフト）

    Returns:
        暗号文
    """

def decrypt(text: str, shift: int) -> str:
    """シーザー暗号を復号する。

    encrypt の逆操作。encrypt(text, shift) を decrypt(result, shift) で元に戻せる。

    Args:
        text: 暗号文
        shift: 暗号化時に使ったシフト量

    Returns:
        平文
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- `encrypt`: 各文字について `ord()` と `chr()` を使い、`a-z` / `A-Z` の範囲内でシフトする。`shift % 26` で正規化する
- `decrypt`: `encrypt(text, -shift)` で実装できる
- テストの import は `from toy.caesar import encrypt, decrypt`

#### テスト仕様

```python
import pytest
from toy.caesar import encrypt, decrypt
```

- **正常系**: `encrypt("abc", 3)` → `"def"`
- **折り返し**: `encrypt("xyz", 3)` → `"abc"`
- **大文字保持**: `encrypt("ABC", 3)` → `"DEF"`
- **非英字保持**: `encrypt("Hello, World!", 5)` → 英字のみシフト、カンマ・空白・感嘆符はそのまま
- **復号**: `decrypt(encrypt("Hello", 7), 7)` → `"Hello"`
- **シフト0**: `encrypt("abc", 0)` → `"abc"`

#### 注意事項

なし。

---

### ステップ E: impl-prime（Wave 1）

#### 作成するファイル
- `src/toy/prime.py`
- `tests/toy/test_prime.py`

#### 型定義・インターフェース

```python
# src/toy/prime.py

def is_prime(n: int) -> bool:
    """素数判定。

    Args:
        n: 判定する整数

    Returns:
        n が素数なら True
    """

def primes_up_to(n: int) -> list[int]:
    """n 以下の素数一覧をエラトステネスの篩で求める。

    Args:
        n: 上限値

    Returns:
        n 以下の素数のリスト（昇順）
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- `is_prime`: 2 未満は False、2 は True、偶数は False、`3` から `√n` まで奇数で割り切れるか判定する
- `primes_up_to`: エラトステネスの篩。長さ `n+1` のブール配列を作り、2 から順に倍数を除外する
- テストの import は `from toy.prime import is_prime, primes_up_to`

#### テスト仕様

```python
import pytest
from toy.prime import is_prime, primes_up_to
```

- **is_prime 正常系**: `is_prime(2)` → `True`、`is_prime(17)` → `True`、`is_prime(4)` → `False`、`is_prime(15)` → `False`
- **is_prime 境界値**: `is_prime(0)` → `False`、`is_prime(1)` → `False`、`is_prime(-5)` → `False`
- **primes_up_to 正常系**: `primes_up_to(20)` → `[2, 3, 5, 7, 11, 13, 17, 19]`
- **primes_up_to 境界値**: `primes_up_to(1)` → `[]`、`primes_up_to(2)` → `[2]`

#### 注意事項

なし。

---

### ステップ F: impl-reverse（Wave 1）

#### 作成するファイル
- `src/toy/reverse.py`
- `tests/toy/test_reverse.py`

#### 型定義・インターフェース

```python
# src/toy/reverse.py

def reverse_string(s: str) -> str:
    """文字列を反転する。

    Args:
        s: 入力文字列

    Returns:
        反転した文字列
    """

def reverse_words(s: str) -> str:
    """単語の順序を反転する。

    単語は空白で区切られる。"hello world" → "world hello"

    Args:
        s: 入力文字列

    Returns:
        単語順を反転した文字列
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- `reverse_string`: スライス `s[::-1]` で実装
- `reverse_words`: `s.split()` で分割し、`reversed` または `[::-1]` で逆順にして `" ".join()` で結合
- テストの import は `from toy.reverse import reverse_string, reverse_words`

#### テスト仕様

```python
import pytest
from toy.reverse import reverse_string, reverse_words
```

- **reverse_string 正常系**: `reverse_string("hello")` → `"olleh"`
- **reverse_string 境界値**: `reverse_string("")` → `""`、`reverse_string("a")` → `"a"`
- **reverse_string 回文**: `reverse_string("racecar")` → `"racecar"`
- **reverse_words 正常系**: `reverse_words("hello world")` → `"world hello"`
- **reverse_words 単一語**: `reverse_words("hello")` → `"hello"`
- **reverse_words 境界値**: `reverse_words("")` → `""`

#### 注意事項

なし。

---

### ステップ G: impl-binary-search（Wave 1）

#### 作成するファイル
- `src/toy/binary_search.py`
- `tests/toy/test_binary_search.py`

#### 型定義・インターフェース

```python
# src/toy/binary_search.py

def binary_search(arr: list[int], target: int) -> int:
    """ソート済みリストから target のインデックスを二分探索で返す。

    Args:
        arr: 昇順にソートされた整数リスト
        target: 検索する値

    Returns:
        target のインデックス。見つからない場合は -1。
    """
```

#### import 先（既存コード）

なし。外部ライブラリ・プロジェクト内の既存コードへの依存はない。

#### 実装パターン

- `fizzbuzz.py` と同じパターンで、純粋関数として実装する
- `left`, `right` の2ポインタで範囲を狭めていく標準的な二分探索を実装する
- `while left <= right` でループし、`mid = (left + right) // 2` で中間点を計算する
- テストの import は `from toy.binary_search import binary_search`

#### テスト仕様

```python
import pytest
from toy.binary_search import binary_search
```

- **正常系（先頭）**: `binary_search([1, 3, 5, 7, 9], 1)` → `0`
- **正常系（中間）**: `binary_search([1, 3, 5, 7, 9], 5)` → `2`
- **正常系（末尾）**: `binary_search([1, 3, 5, 7, 9], 9)` → `4`
- **見つからない**: `binary_search([1, 3, 5, 7, 9], 4)` → `-1`
- **空リスト**: `binary_search([], 1)` → `-1`
- **要素1つ（見つかる）**: `binary_search([5], 5)` → `0`
- **要素1つ（見つからない）**: `binary_search([5], 3)` → `-1`

#### 注意事項

なし。
