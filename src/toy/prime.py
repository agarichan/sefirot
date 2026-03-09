import math


def is_prime(n: int) -> bool:
    """素数判定。

    Args:
        n: 判定対象の整数

    Returns:
        素数なら True、そうでなければ False
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def primes_up_to(n: int) -> list[int]:
    """n 以下の素数一覧を返す（エラトステネスの篩）。

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
    return [i for i, is_p in enumerate(sieve) if is_p]
