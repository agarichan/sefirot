import pytest
from src.toy.factorial import factorial


class TestFactorialNormal:
    def test_factorial_0(self):
        assert factorial(0) == 1

    def test_factorial_1(self):
        assert factorial(1) == 1

    def test_factorial_5(self):
        assert factorial(5) == 120

    def test_factorial_10(self):
        assert factorial(10) == 3628800


class TestFactorialBoundary:
    def test_factorial_0_is_1(self):
        assert factorial(0) == 1


class TestFactorialError:
    def test_negative_1(self):
        with pytest.raises(ValueError):
            factorial(-1)

    def test_negative_100(self):
        with pytest.raises(ValueError):
            factorial(-100)
