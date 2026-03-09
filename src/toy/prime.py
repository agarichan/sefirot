def is_prime(n: int) -> bool:
    """n が素数かどうかを返す。

    Args:
        n: 判定する整数

    Returns:
        素数なら True
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
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
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]
