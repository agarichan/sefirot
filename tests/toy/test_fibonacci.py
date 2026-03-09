import pytest
from src.toy.fibonacci import fibonacci, fib


class TestFibonacci:
    def test_fibonacci_7(self):
        assert fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]

    def test_fibonacci_0(self):
        assert fibonacci(0) == []

    def test_fibonacci_1(self):
        assert fibonacci(1) == [0]

    def test_fibonacci_2(self):
        assert fibonacci(2) == [0, 1]

    def test_fibonacci_negative(self):
        with pytest.raises(ValueError):
            fibonacci(-1)


class TestFib:
    def test_fib_0(self):
        assert fib(0) == 0

    def test_fib_1(self):
        assert fib(1) == 1

    def test_fib_10(self):
        assert fib(10) == 55

    def test_fib_negative(self):
        with pytest.raises(ValueError):
            fib(-1)
