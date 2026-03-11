from dataclasses import dataclass


@dataclass
class ConversionResult:
    """変換結果"""
    value: float           # 変換後の値
    from_unit: str         # 変換元の単位
    to_unit: str           # 変換先の単位
    original_value: float  # 変換前の値
