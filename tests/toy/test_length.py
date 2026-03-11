import pytest
from toy.length import convert
from toy.types import ConversionResult


class TestLengthConvert:
    """長さ変換の正常系テスト"""

    def test_m_to_cm(self):
        result = convert(1, "m", "cm")
        assert result.value == pytest.approx(100.0)

    def test_km_to_m(self):
        result = convert(1, "km", "m")
        assert result.value == pytest.approx(1000.0)

    def test_mm_to_m(self):
        result = convert(1000, "mm", "m")
        assert result.value == pytest.approx(1.0)

    def test_m_to_mm(self):
        result = convert(1, "m", "mm")
        assert result.value == pytest.approx(1000.0)

    def test_cm_to_m(self):
        result = convert(100, "cm", "m")
        assert result.value == pytest.approx(1.0)

    def test_km_to_mm(self):
        result = convert(1, "km", "mm")
        assert result.value == pytest.approx(1000000.0)


class TestLengthConvertSameUnit:
    """同一単位の変換テスト"""

    def test_same_unit(self):
        result = convert(500, "m", "m")
        assert result.value == pytest.approx(500.0)


class TestLengthConvertResultType:
    """戻り値の型テスト"""

    def test_returns_conversion_result(self):
        result = convert(1, "m", "cm")
        assert isinstance(result, ConversionResult)
        assert result.from_unit == "m"
        assert result.to_unit == "cm"
        assert result.original_value == 1
        assert result.value == pytest.approx(100.0)


class TestLengthConvertErrors:
    """異常系テスト"""

    def test_invalid_from_unit(self):
        with pytest.raises(ValueError):
            convert(1, "inch", "m")

    def test_invalid_to_unit(self):
        with pytest.raises(ValueError):
            convert(1, "m", "mile")
