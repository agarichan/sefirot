import pytest
from src.toy.prime import is_prime, primes_up_to


class TestIsPrime:
    def test_prime_2(self):
        assert is_prime(2) is True

    def test_prime_3(self):
        assert is_prime(3) is True

    def test_prime_17(self):
        assert is_prime(17) is True

    def test_not_prime_4(self):
        assert is_prime(4) is False

    def test_not_prime_15(self):
        assert is_prime(15) is False

    def test_zero_not_prime(self):
        assert is_prime(0) is False

    def test_one_not_prime(self):
        assert is_prime(1) is False

    def test_negative_not_prime(self):
        assert is_prime(-5) is False


class TestPrimesUpTo:
    def test_primes_up_to_20(self):
        assert primes_up_to(20) == [2, 3, 5, 7, 11, 13, 17, 19]

    def test_primes_up_to_2(self):
        assert primes_up_to(2) == [2]

    def test_primes_up_to_1(self):
        assert primes_up_to(1) == []

    def test_primes_up_to_0(self):
        assert primes_up_to(0) == []
