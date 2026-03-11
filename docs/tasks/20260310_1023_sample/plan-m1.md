# Milestone 1: 単位変換ライブラリの実装

## 概要

`src/toy/` 配下に共通型定義（`ConversionResult`）、温度変換モジュール（C/F/K 全方向）、長さ変換モジュール（mm/cm/m/km）を実装し、`pytest tests/toy/` で全テストを通す。

## タスク一覧

| ステップ | タスクID | Wave | 概要 |
|---------|---------|------|------|
| A | common-types | 1 | 共通型定義（ConversionResult）とパッケージ初期化 |
| B | temperature-converter | 2 | 温度変換モジュールとテスト |
| C | length-converter | 2 | 長さ変換モジュールとテスト |

## タスク詳細

### ステップ A: common-types（Wave 1）

W2 の全タスクが参照する共通型と、パッケージの `__init__.py` を作成する。

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
from .types import ConversionResult

__all__ = ["ConversionResult"]
```

**`tests/toy/__init__.py`**: 空ファイル

#### import 先（既存コード）

なし（新規パッケージ）

#### 実装パターン

標準的な Python dataclass パターン。特別な実装パターンの参照は不要。

#### 注意事項

- `src/toy/` と `tests/toy/` の両ディレクトリを新規作成する必要がある

---

### ステップ B: temperature-converter（Wave 2）

温度変換モジュール（C/F/K 全方向）と対応するテストを実装する。

#### 作成するファイル

- `src/toy/temperature.py`
- `tests/toy/test_temperature.py`

#### 型定義・インターフェース

**`src/toy/temperature.py`**:

```python
from .types import ConversionResult


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

#### 変換ロジック

対応単位: `"C"`（摂氏）、`"F"`（華氏）、`"K"`（ケルビン）

変換式:
- C → F: `value * 9/5 + 32`
- C → K: `value + 273.15`
- F → C: `(value - 32) * 5/9`
- F → K: `(value - 32) * 5/9 + 273.15`
- K → C: `value - 273.15`
- K → F: `(value - 273.15) * 9/5 + 32`
- 同一単位: そのまま返す

未対応の単位（`from_unit` または `to_unit` が `"C"`, `"F"`, `"K"` のいずれでもない）が指定された場合は `ValueError` を送出する。

#### import 先（既存コード）

- `src/toy/types.py` → `ConversionResult`（ステップ A で作成済み）

#### テスト仕様

**`tests/toy/test_temperature.py`**:

```python
import pytest
from toy.temperature import convert
from toy.types import ConversionResult
```

テストケース:
1. **正常系**: C→F, C→K, F→C, F→K, K→C, K→F の各方向変換
   - `convert(0, "C", "F")` → `value == 32.0`
   - `convert(100, "C", "F")` → `value == 212.0`
   - `convert(0, "C", "K")` → `value == 273.15`
   - `convert(32, "F", "C")` → `value == 0.0`
   - `convert(212, "F", "K")` → `value == 373.15`
   - `convert(273.15, "K", "C")` → `value == 0.0`
   - `convert(273.15, "K", "F")` → `value == 32.0`
2. **同一単位**: `convert(100, "C", "C")` → `value == 100.0`
3. **戻り値の型**: `ConversionResult` であること、各フィールドが正しいこと
4. **異常系**: `convert(0, "X", "C")` → `ValueError`、`convert(0, "C", "X")` → `ValueError`

浮動小数点の比較は `pytest.approx()` を使用する。

#### 実装パターン

一般的な温度変換の実装。中間変換方式（一旦 C に変換してから目標単位へ）でも、直接変換テーブル方式でもよい。

#### 注意事項

- 浮動小数点の精度に注意。テストでは `pytest.approx()` を使う

---

### ステップ C: length-converter（Wave 2）

長さ変換モジュール（mm/cm/m/km メートル法のみ）と対応するテストを実装する。

#### 作成するファイル

- `src/toy/length.py`
- `tests/toy/test_length.py`

#### 型定義・インターフェース

**`src/toy/length.py`**:

```python
from .types import ConversionResult


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

#### 変換ロジック

対応単位: `"mm"`, `"cm"`, `"m"`, `"km"`（メートル法のみ）

変換方式: 基準単位（m）への変換係数テーブルを使用する。

```python
# 各単位から m への変換係数
_TO_METERS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
}
```

変換手順:
1. `from_unit` の値を m に変換: `value_in_meters = value * _TO_METERS[from_unit]`
2. m から `to_unit` に変換: `result = value_in_meters / _TO_METERS[to_unit]`

未対応の単位（`from_unit` または `to_unit` が `"mm"`, `"cm"`, `"m"`, `"km"` のいずれでもない）が指定された場合は `ValueError` を送出する。

#### import 先（既存コード）

- `src/toy/types.py` → `ConversionResult`（ステップ A で作成済み）

#### テスト仕様

**`tests/toy/test_length.py`**:

```python
import pytest
from toy.length import convert
from toy.types import ConversionResult
```

テストケース:
1. **正常系**: 各方向の変換
   - `convert(1, "m", "cm")` → `value == 100.0`
   - `convert(1, "km", "m")` → `value == 1000.0`
   - `convert(1000, "mm", "m")` → `value == 1.0`
   - `convert(1, "m", "mm")` → `value == 1000.0`
   - `convert(100, "cm", "m")` → `value == 1.0`
   - `convert(1, "km", "mm")` → `value == 1000000.0`
2. **同一単位**: `convert(500, "m", "m")` → `value == 500.0`
3. **戻り値の型**: `ConversionResult` であること、各フィールドが正しいこと
4. **異常系**: `convert(1, "inch", "m")` → `ValueError`、`convert(1, "m", "mile")` → `ValueError`

浮動小数点の比較は `pytest.approx()` を使用する。

#### 実装パターン

基準単位への変換係数テーブルパターン。温度変換と異なり、線形変換なのでシンプルに実装できる。

#### 注意事項

- 特になし
