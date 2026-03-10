import math


def is_prime(n: int) -> bool:
    """素数判定。

    Args:
        n: 判定する整数

    Returns:
        n が素数なら True
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def primes_up_to(n: int) -> list[int]:
    """n 以下の素数一覧をエラトステネスの篩で求める。

    Args:
        n: 上限値

    Returns:
        n 以下の素数のリスト（昇順）
    """
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = False
    sieve[1] = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]
