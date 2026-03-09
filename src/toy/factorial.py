def factorial(n: int) -> int:
    """n の階乗を返す。

    factorial(0) = 1, factorial(1) = 1, factorial(5) = 120

    Args:
        n: 0以上の整数

    Returns:
        n の階乗

    Raises:
        ValueError: n が負の数の場合
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
