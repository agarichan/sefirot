def factorial(n: int) -> int:
    """n の階乗を返す。

    Args:
        n: 0 以上の整数

    Returns:
        n!

    Raises:
        ValueError: n が負の数の場合
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
