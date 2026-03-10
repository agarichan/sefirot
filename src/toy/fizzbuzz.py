def fizzbuzz(n: int) -> list[str]:
    """1 から n までの FizzBuzz 結果をリストで返す。

    - 3 の倍数 → "Fizz"
    - 5 の倍数 → "Buzz"
    - 3 と 5 の両方の倍数 → "FizzBuzz"
    - それ以外 → 数字の文字列（例: "1", "2", "4"）

    Args:
        n: 正の整数

    Returns:
        長さ n のリスト
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    result: list[str] = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
