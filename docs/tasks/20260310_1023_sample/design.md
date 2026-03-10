# 単位変換ライブラリ

## 目的

sefirot の主要機能（Wave 依存管理、並列実行、HIL 質問フロー）を検証するためのサンプルタスク。

## 概要

`src/toy/` 配下に単位変換ライブラリを作成する。共通の型定義を先に作り、それを参照する2つの独立した変換モジュールを並列に実装する。

検証したい sefirot の機能:
- **Wave 依存**: W1（共通型） → W2（実装）の順序制御
- **並列実行**: W2 で2つの Builder が同時に動く
- **HIL**: 長さ変換の対応単位をユーザーに確認する

## ディレクトリ構成

```
src/toy/
├── __init__.py
├── types.py           # 共通型定義
├── temperature.py     # 温度変換
└── length.py          # 長さ変換

tests/toy/
├── __init__.py
├── test_temperature.py
└── test_length.py
```

## モジュール仕様

### 1. types.py（共通型定義）

```python
from dataclasses import dataclass

@dataclass
class ConversionResult:
    """変換結果"""
    value: float        # 変換後の値
    from_unit: str      # 変換元の単位
    to_unit: str        # 変換先の単位
    original_value: float  # 変換前の値
```

### 2. temperature.py（温度変換）

- `convert(value: float, from_unit: str, to_unit: str) -> ConversionResult`
- 対応単位: `"C"`（摂氏）、`"F"`（華氏）、`"K"`（ケルビン）
- 全方向の変換に対応する（C↔F、C↔K、F↔K）
- 未対応の単位が指定された場合は `ValueError` を送出する

### 3. length.py（長さ変換）

- `convert(value: float, from_unit: str, to_unit: str) -> ConversionResult`
- 対応単位: メートル法のみ（mm, cm, m, km）

#### 追加指示（ユーザー回答）
- Q: 長さ変換の対応単位について: メートル法のみ（mm, cm, m, km）にしますか？それともヤード・ポンド法（inch, feet, yard, mile）も含めますか？
- A: メートル法のみ
- 未対応の単位が指定された場合は `ValueError` を送出する

## テスト方針

- 各テストファイルで正常系・境界値・異常系をカバーする
- 実行コマンド: `pytest tests/toy/`

## 備考

- このコードは sefirot の動作テスト用であり、テスト完了後に削除する前提
