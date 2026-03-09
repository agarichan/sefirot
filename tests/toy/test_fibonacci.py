from src.toy.fibonacci import fib, fibonacci


class TestFibonacci:
    def test_zero(self):
        assert fibonacci(0) == []

    def test_one(self):
        assert fibonacci(1) == [0]

    def test_two(self):
        assert fibonacci(2) == [0, 1]

    def test_seven(self):
        assert fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]


class TestFib:
    def test_fib_zero(self):
        assert fib(0) == 0

    def test_fib_one(self):
        assert fib(1) == 1

    def test_fib_ten(self):
        assert fib(10) == 55
