# Milestone 1: 共通型定義・温度変換・長さ変換の実装

## 概要

`src/toy/` 配下に単位変換ライブラリを作成する。共通の型定義（`ConversionResult`）を定義し、それを参照する温度変換モジュールと長さ変換モジュールを並列に実装する。`pytest tests/toy/` で全テストが通ることがゴール。

## タスク一覧

| ステップ | タスク ID | Wave | 概要 |
|----------|-----------|------|------|
| A | common-types | 1 | 共通型定義（ConversionResult）とパッケージ初期化 |
| B | temperature-conversion | 2 | 温度変換モジュールとテスト |
| C | length-conversion | 2 | 長さ変換モジュールとテスト |

## タスク詳細

### ステップ A: common-types（Wave 1）

#### 作成するファイル

- `src/toy/__init__.py`
- `src/toy/types.py`
- `tests/toy/__init__.py`

#### 型定義・インターフェース

**`src/toy/types.py`**:

```python
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """変換結果"""
    value: float           # 変換後の値
    from_unit: str         # 変換元の単位
    to_unit: str           # 変換先の単位
    original_value: float  # 変換前の値
```

**`src/toy/__init__.py`**:

```python
from toy.types import ConversionResult

__all__ = ["ConversionResult"]
```

**`tests/toy/__init__.py`**: 空ファイル

#### import 先（既存コード）

なし（標準ライブラリの `dataclasses` のみ使用）

#### 実装パターン

標準的な dataclass 定義。特殊なパターンなし。

#### 注意事項

- `src/toy/` と `tests/toy/` の両方のディレクトリを作成すること
- `pyproject.toml` の `pythonpath = ["src"]` により、`import toy.types` でアクセス可能（`pyproject.toml` の変更は不要）

---

### ステップ B: temperature-conversion（Wave 2）

#### 作成するファイル

- `src/toy/temperature.py`
- `tests/toy/test_temperature.py`

#### 型定義・インターフェース

**`src/toy/temperature.py`**:

```python
from toy.types import ConversionResult


def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """温度を変換する。

    Args:
        value: 変換元の値
        from_unit: 変換元の単位（"C", "F", "K"）
        to_unit: 変換先の単位（"C", "F", "K"）

    Returns:
        ConversionResult

    Raises:
        ValueError: 未対応の単位が指定された場合
    """
    ...
```

#### import 先（既存コード）

- `src/toy/types.py` -> `ConversionResult`

#### 実装パターン

変換ロジック:

- **C → F**: `value * 9/5 + 32`
- **F → C**: `(value - 32) * 5/9`
- **C → K**: `value + 273.15`
- **K → C**: `value - 273.15`
- **F → K**: F → C → K の2段階変換
- **K → F**: K → C → F の2段階変換
- **同一単位**: そのまま返す（`from_unit == to_unit` の場合）

未対応の単位には `ValueError` を送出する。対応単位は `"C"`, `"F"`, `"K"` の3つ。

**`tests/toy/test_temperature.py`** のテストケース:

```python
import pytest
from toy.temperature import convert
from toy.types import ConversionResult
```

正常系:
- `convert(0, "C", "F")` → `value == 32.0`
- `convert(100, "C", "F")` → `value == 212.0`
- `convert(32, "F", "C")` → `value == 0.0`
- `convert(0, "C", "K")` → `value == 273.15`
- `convert(273.15, "K", "C")` → `value == 0.0`
- `convert(32, "F", "K")` → `value == 273.15`
- `convert(273.15, "K", "F")` → `value == 32.0`
- 同一単位: `convert(100, "C", "C")` → `value == 100.0`
- 戻り値が `ConversionResult` 型であること
- `from_unit`, `to_unit`, `original_value` が正しくセットされていること

異常系:
- `convert(0, "X", "C")` → `ValueError`
- `convert(0, "C", "X")` → `ValueError`

#### 注意事項

- 浮動小数点の比較は `pytest.approx()` を使用すること

---

### ステップ C: length-conversion（Wave 2）

#### 作成するファイル

- `src/toy/length.py`
- `tests/toy/test_length.py`

#### 型定義・インターフェース

**`src/toy/length.py`**:

```python
from toy.types import ConversionResult


def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """長さを変換する。

    Args:
        value: 変換元の値
        from_unit: 変換元の単位（"mm", "cm", "m", "km"）
        to_unit: 変換先の単位（"mm", "cm", "m", "km"）

    Returns:
        ConversionResult

    Raises:
        ValueError: 未対応の単位が指定された場合
    """
    ...
```

> **注意**: 対応単位はユーザー確認待ち。現時点ではメートル法（mm, cm, m, km）のみで設計。ユーザーがヤード・ポンド法も含める場合は inch, feet, yard, mile を追加する。

#### import 先（既存コード）

- `src/toy/types.py` -> `ConversionResult`

#### 実装パターン

メートル（m）を基準単位として、各単位からメートルへの換算係数を辞書で持つ:

```python
# メートルへの換算係数
_TO_METER = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
}
```

変換ロジック: `from_unit → m → to_unit`（基準単位経由の2段階変換）

```
result = value * _TO_METER[from_unit] / _TO_METER[to_unit]
```

未対応の単位には `ValueError` を送出する。同一単位はそのまま返す。

**`tests/toy/test_length.py`** のテストケース:

```python
import pytest
from toy.length import convert
from toy.types import ConversionResult
```

正常系:
- `convert(1, "m", "cm")` → `value == 100.0`
- `convert(1, "km", "m")` → `value == 1000.0`
- `convert(1000, "mm", "m")` → `value == 1.0`
- `convert(1, "cm", "mm")` → `value == 10.0`
- `convert(1, "km", "cm")` → `value == 100000.0`
- 同一単位: `convert(5, "m", "m")` → `value == 5.0`
- 戻り値が `ConversionResult` 型であること
- `from_unit`, `to_unit`, `original_value` が正しくセットされていること

異常系:
- `convert(1, "x", "m")` → `ValueError`
- `convert(1, "m", "x")` → `ValueError`

#### 注意事項

- 浮動小数点の比較は `pytest.approx()` を使用すること
- ユーザー確認で対応単位が変更された場合、`_TO_METER` 辞書にエントリを追加するだけで対応可能な設計にしている
