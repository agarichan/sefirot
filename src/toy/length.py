from .types import ConversionResult

# 各単位から m への変換係数
_TO_METERS = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
}


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
    if from_unit not in _TO_METERS:
        raise ValueError(f"未対応の単位: {from_unit}")
    if to_unit not in _TO_METERS:
        raise ValueError(f"未対応の単位: {to_unit}")

    value_in_meters = value * _TO_METERS[from_unit]
    result = value_in_meters / _TO_METERS[to_unit]

    return ConversionResult(
        value=result,
        from_unit=from_unit,
        to_unit=to_unit,
        original_value=value,
    )
