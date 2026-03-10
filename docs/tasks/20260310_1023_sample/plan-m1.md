# Milestone 1: 温度変換・長さ変換モジュールの実装とテスト

## 概要

`src/toy/` 配下に共通型定義・温度変換・長さ変換の3モジュールを作成し、`tests/toy/` にテストを用意して `pytest tests/toy/` が全件パスする状態にする。

## タスク一覧

| ステップ | タスクID | Wave | 概要 |
|----------|----------|------|------|
| A | define-shared-types | W1 | 共通型定義（ConversionResult） |
| B | impl-temperature | W2 | 温度変換モジュール＋テスト |
| C | impl-length | W2 | 長さ変換モジュール＋テスト |

## タスク詳細

### ステップ A: define-shared-types（Wave 1）

共通型と各モジュールの `__init__.py` を作成する。

#### 作成するファイル

- `src/toy/__init__.py`
- `src/toy/types.py`
- `tests/toy/__init__.py`

#### 型定義・インターフェース

```python
# src/toy/types.py
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """変換結果"""
    value: float          # 変換後の値
    from_unit: str        # 変換元の単位
    to_unit: str          # 変換先の単位
    original_value: float # 変換前の値
```

```python
# src/toy/__init__.py
（空ファイル）
```

```python
# tests/toy/__init__.py
（空ファイル）
```

#### import 先（既存コード）

なし（標準ライブラリの `dataclasses` のみ）

#### 実装パターン

シンプルな dataclass 定義。特別なパターンなし。

#### 注意事項

なし

---

### ステップ B: impl-temperature（Wave 2）

温度変換モジュールとそのテストを実装する。

#### 作成するファイル

- `src/toy/temperature.py`
- `tests/toy/test_temperature.py`

#### 型定義・インターフェース

```python
# src/toy/temperature.py

from src.toy.types import ConversionResult

SUPPORTED_UNITS = ("C", "F", "K")


def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """温度を変換する。

    Args:
        value: 変換前の値
        from_unit: 変換元の単位（"C", "F", "K"）
        to_unit: 変換先の単位（"C", "F", "K"）

    Returns:
        ConversionResult

    Raises:
        ValueError: 未対応の単位が指定された場合
    """
    ...
```

変換ロジック:
- C → F: `value * 9/5 + 32`
- F → C: `(value - 32) * 5/9`
- C → K: `value + 273.15`
- K → C: `value - 273.15`
- F → K: F→C→K の2段階変換
- K → F: K→C→F の2段階変換
- 同一単位（C→C 等）: そのまま返す

#### import 先（既存コード）

- `src/toy/types.py` → `ConversionResult`

#### テスト仕様

```python
# tests/toy/test_temperature.py

import pytest
from src.toy.temperature import convert


class TestTemperatureConvert:
    """正常系"""

    def test_c_to_f(self):
        result = convert(100, "C", "F")
        assert result.value == pytest.approx(212.0)
        assert result.from_unit == "C"
        assert result.to_unit == "F"
        assert result.original_value == 100

    def test_f_to_c(self):
        result = convert(32, "F", "C")
        assert result.value == pytest.approx(0.0)

    def test_c_to_k(self):
        result = convert(0, "C", "K")
        assert result.value == pytest.approx(273.15)

    def test_k_to_c(self):
        result = convert(273.15, "K", "C")
        assert result.value == pytest.approx(0.0)

    def test_f_to_k(self):
        result = convert(32, "F", "K")
        assert result.value == pytest.approx(273.15)

    def test_k_to_f(self):
        result = convert(273.15, "K", "F")
        assert result.value == pytest.approx(32.0)

    def test_same_unit(self):
        result = convert(42, "C", "C")
        assert result.value == pytest.approx(42.0)


class TestTemperatureBoundary:
    """境界値"""

    def test_absolute_zero_k_to_c(self):
        result = convert(0, "K", "C")
        assert result.value == pytest.approx(-273.15)

    def test_zero_c(self):
        result = convert(0, "C", "F")
        assert result.value == pytest.approx(32.0)

    def test_negative_value(self):
        result = convert(-40, "C", "F")
        assert result.value == pytest.approx(-40.0)


class TestTemperatureError:
    """異常系"""

    def test_invalid_from_unit(self):
        with pytest.raises(ValueError):
            convert(100, "X", "C")

    def test_invalid_to_unit(self):
        with pytest.raises(ValueError):
            convert(100, "C", "X")
```

#### 実装パターン

`from_unit` と `to_unit` を検証し、未対応なら `ValueError` を送出。一旦すべてを摂氏に変換してから目的の単位に変換する2段階方式が簡潔。

#### 注意事項

- 浮動小数点の比較はテストで `pytest.approx` を使う
- import パスは `from src.toy.types import ConversionResult` とする

---

### ステップ C: impl-length（Wave 2）

長さ変換モジュールとそのテストを実装する。

**注意**: 対応単位は `[要ユーザー確認]` のため、質問キューでユーザー回答を待つ。回答がない場合はメートル法のみ（mm, cm, m, km）で実装する。

#### 作成するファイル

- `src/toy/length.py`
- `tests/toy/test_length.py`

#### 型定義・インターフェース

```python
# src/toy/length.py

from src.toy.types import ConversionResult

# メートルを基準単位とした変換レートの辞書
# ユーザー確認の結果に応じてヤード・ポンド法も追加する可能性あり
UNITS_TO_METER: dict[str, float] = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
}


def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """長さを変換する。

    Args:
        value: 変換前の値
        from_unit: 変換元の単位
        to_unit: 変換先の単位

    Returns:
        ConversionResult

    Raises:
        ValueError: 未対応の単位が指定された場合
    """
    ...
```

変換ロジック:
- 基準単位（メートル）を経由する方式: `value * UNITS_TO_METER[from_unit] / UNITS_TO_METER[to_unit]`
- 同一単位の場合もそのまま計算で正しい結果になる

#### import 先（既存コード）

- `src/toy/types.py` → `ConversionResult`

#### テスト仕様

```python
# tests/toy/test_length.py

import pytest
from src.toy.length import convert


class TestLengthConvert:
    """正常系"""

    def test_m_to_km(self):
        result = convert(1500, "m", "km")
        assert result.value == pytest.approx(1.5)
        assert result.from_unit == "m"
        assert result.to_unit == "km"
        assert result.original_value == 1500

    def test_km_to_m(self):
        result = convert(2.5, "km", "m")
        assert result.value == pytest.approx(2500.0)

    def test_cm_to_mm(self):
        result = convert(10, "cm", "mm")
        assert result.value == pytest.approx(100.0)

    def test_mm_to_m(self):
        result = convert(5000, "mm", "m")
        assert result.value == pytest.approx(5.0)

    def test_same_unit(self):
        result = convert(42, "m", "m")
        assert result.value == pytest.approx(42.0)


class TestLengthBoundary:
    """境界値"""

    def test_zero_value(self):
        result = convert(0, "m", "km")
        assert result.value == pytest.approx(0.0)

    def test_very_small_value(self):
        result = convert(0.001, "mm", "m")
        assert result.value == pytest.approx(0.000001)


class TestLengthError:
    """異常系"""

    def test_invalid_from_unit(self):
        with pytest.raises(ValueError):
            convert(100, "lightyear", "m")

    def test_invalid_to_unit(self):
        with pytest.raises(ValueError):
            convert(100, "m", "lightyear")
```

#### 実装パターン

辞書ベースの変換レート方式。`from_unit` / `to_unit` が辞書にない場合は `ValueError` を送出。

#### 注意事項

- ユーザー確認結果によりヤード・ポンド法の単位（inch, feet, yard, mile）を `UNITS_TO_METER` 辞書に追加する可能性がある。追加する場合のレート: `inch: 0.0254`, `feet: 0.3048`, `yard: 0.9144`, `mile: 1609.344`。テストケースもそれに応じて追加する
- 浮動小数点の比較はテストで `pytest.approx` を使う
- import パスは `from src.toy.types import ConversionResult` とする
