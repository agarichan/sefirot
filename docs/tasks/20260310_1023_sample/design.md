# Toy プログラム作成

## 目的

sefirot 開発者が、Planner → Builder → Verifier ループ（特に並列実行とHILを挟むフロー）が正しく動作することを、簡単なプログラムで検証するため。

## 概要

`src/toy/` 配下に、独立した小規模プログラムを 2 個作成する。各プログラムは 1 ファイル + 1 テストファイルの構成とし、プログラム間に依存関係を持たせない。これにより、sefirot の Wave 並列実行を検証できる。

## ディレクトリ構成

```
src/toy/
├── __init__.py
├── fizzbuzz.py
└── ???.py  # 後で決まる

tests/toy/
├── __init__.py
├── test_fizzbuzz.py
└── test_???.py  # 後で決まる
```

## 各プログラムの仕様

### 1. fizzbuzz.py

- `fizzbuzz(n: int) -> list[str]`: 1 から n までの FizzBuzz 結果をリストで返す
  - 3 の倍数 → "Fizz"、5 の倍数 → "Buzz"、両方 → "FizzBuzz"、それ以外 → 数字の文字列

### 2. ????.py

- 実装時に考えるので他のプログラムを実装する前に質問してほしい。

#### 追加指示（ユーザー回答）
- Q: Milestone 1 で実装する2つ目の toy プログラムの種類を決めてください。設計ドキュメントでは未定（????.py）となっています。例: fibonacci, palindrome, factorial, caesar, prime, reverse, binary_search など。どのプログラムを実装しますか？
- A: fibonacci

## テスト方針

- 各テストファイルで正常系・境界値・異常系をカバーする
- 実行コマンド: `pytest tests/toy/`

## 備考

- このコードは sefirot の動作テスト用であり、テスト完了後に削除する前提
- プログラム間に依存関係はない（全て独立して並列実装可能）
