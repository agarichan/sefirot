from .types import ConversionResult

_VALID_UNITS = {"C", "F", "K"}


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
    if from_unit not in _VALID_UNITS:
        raise ValueError(f"未対応の単位: {from_unit}")
    if to_unit not in _VALID_UNITS:
        raise ValueError(f"未対応の単位: {to_unit}")

    if from_unit == to_unit:
        result = value
    elif from_unit == "C" and to_unit == "F":
        result = value * 9 / 5 + 32
    elif from_unit == "C" and to_unit == "K":
        result = value + 273.15
    elif from_unit == "F" and to_unit == "C":
        result = (value - 32) * 5 / 9
    elif from_unit == "F" and to_unit == "K":
        result = (value - 32) * 5 / 9 + 273.15
    elif from_unit == "K" and to_unit == "C":
        result = value - 273.15
    elif from_unit == "K" and to_unit == "F":
        result = (value - 273.15) * 9 / 5 + 32

    return ConversionResult(
        value=result,
        from_unit=from_unit,
        to_unit=to_unit,
        original_value=value,
    )
