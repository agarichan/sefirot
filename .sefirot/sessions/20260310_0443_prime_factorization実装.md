# add-prime-factorization: prime_factorization 関数の実装

## タスク ID
`add-prime-factorization` — Milestone 1 ステップ A

## 変更ファイル
- `src/toy/prime.py` — `prime_factorization()` 関数を追加
- `tests/toy/test_prime.py` — `TestPrimeFactorization` クラスを追加（9テスト）

## 設計判断
- 試し割り法で実装。2 から順に割り切れる限り割り、商が 1 になるまで繰り返す
- 既存の `is_prime` / `primes_up_to` は使わず独立実装（設計ドキュメントの指示通り）
- エラーメッセージ形式は既存コードに合わせた（f-string で具体的な値を表示）

## 次のタスクへの申し送り
- 特になし。既存テストも全て pass 確認済み（21 tests passed）
