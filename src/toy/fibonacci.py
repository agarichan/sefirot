def fibonacci(n: int) -> list[int]:
    """先頭 n 個のフィボナッチ数列を返す。

    0-indexed: [0, 1, 1, 2, 3, 5, 8, ...]

    Args:
        n: 取得する個数（0以上の整数）

    Returns:
        フィボナッチ数列のリスト
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return []
    if n == 1:
        return [0]
    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-1] + result[-2])
    return result


def fib(n: int) -> int:
    """n 番目のフィボナッチ数を返す（0-indexed）。

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, ...

    Args:
        n: 0以上の整数

    Returns:
        n 番目のフィボナッチ数
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
