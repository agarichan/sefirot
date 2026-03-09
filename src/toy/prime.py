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


def prime_factorization(n: int) -> list[int]:
    """n を素因数分解し、素因数を昇順のリストで返す。

    重複する素因数はその回数分含める。
    例: prime_factorization(12) → [2, 2, 3]
        prime_factorization(7) → [7]
        prime_factorization(1) → []

    Args:
        n: 1以上の整数

    Returns:
        素因数のリスト（昇順、重複あり）

    Raises:
        ValueError: n が 1 未満の場合
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    factors: list[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors
