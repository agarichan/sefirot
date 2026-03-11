import pytest
from toy.temperature import convert
from toy.types import ConversionResult


class TestTemperatureConvert:
    def test_celsius_to_fahrenheit_freezing(self):
        result = convert(0, "C", "F")
        assert result.value == pytest.approx(32.0)

    def test_celsius_to_fahrenheit_boiling(self):
        result = convert(100, "C", "F")
        assert result.value == pytest.approx(212.0)

    def test_celsius_to_kelvin(self):
        result = convert(0, "C", "K")
        assert result.value == pytest.approx(273.15)

    def test_fahrenheit_to_celsius(self):
        result = convert(32, "F", "C")
        assert result.value == pytest.approx(0.0)

    def test_fahrenheit_to_kelvin(self):
        result = convert(212, "F", "K")
        assert result.value == pytest.approx(373.15)

    def test_kelvin_to_celsius(self):
        result = convert(273.15, "K", "C")
        assert result.value == pytest.approx(0.0)

    def test_kelvin_to_fahrenheit(self):
        result = convert(273.15, "K", "F")
        assert result.value == pytest.approx(32.0)

    def test_same_unit(self):
        result = convert(100, "C", "C")
        assert result.value == pytest.approx(100.0)

    def test_return_type_and_fields(self):
        result = convert(0, "C", "F")
        assert isinstance(result, ConversionResult)
        assert result.from_unit == "C"
        assert result.to_unit == "F"
        assert result.original_value == 0

    def test_invalid_from_unit(self):
        with pytest.raises(ValueError):
            convert(0, "X", "C")

    def test_invalid_to_unit(self):
        with pytest.raises(ValueError):
            convert(0, "C", "X")
