def fibonacci(n: int) -> list[int]:
    """先頭 n 個のフィボナッチ数列を返す。

    数列: 0, 1, 1, 2, 3, 5, 8, 13, ...

    Args:
        n: 取得する個数（0以上の整数）

    Returns:
        長さ n のリスト
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-2] + result[-1])
    return result


def fib(n: int) -> int:
    """n 番目のフィボナッチ数を返す（0-indexed）。

    fib(0) = 0, fib(1) = 1, fib(2) = 1, fib(3) = 2, ...

    Args:
        n: 0以上の整数

    Returns:
        n 番目のフィボナッチ数
    """
    if n <= 0:
        return 0
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
