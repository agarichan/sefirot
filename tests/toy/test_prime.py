from src.toy.prime import is_prime, primes_up_to


class TestIsPrime:
    def test_two_is_prime(self):
        assert is_prime(2) is True

    def test_three_is_prime(self):
        assert is_prime(3) is True

    def test_four_is_not_prime(self):
        assert is_prime(4) is False

    def test_seventeen_is_prime(self):
        assert is_prime(17) is True

    def test_one_is_not_prime(self):
        assert is_prime(1) is False

    def test_zero_is_not_prime(self):
        assert is_prime(0) is False

    def test_negative_is_not_prime(self):
        assert is_prime(-5) is False


class TestPrimesUpTo:
    def test_primes_up_to_10(self):
        assert primes_up_to(10) == [2, 3, 5, 7]

    def test_primes_up_to_1(self):
        assert primes_up_to(1) == []

    def test_primes_up_to_2(self):
        assert primes_up_to(2) == [2]

    def test_primes_up_to_30(self):
        assert primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
