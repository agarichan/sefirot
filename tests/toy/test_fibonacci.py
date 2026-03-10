import pytest
from toy.fibonacci import fibonacci, fib


def test_fibonacci_7():
    assert fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]


def test_fibonacci_0():
    assert fibonacci(0) == []


def test_fibonacci_1():
    assert fibonacci(1) == [0]


def test_fibonacci_2():
    assert fibonacci(2) == [0, 1]


def test_fib_0():
    assert fib(0) == 0


def test_fib_1():
    assert fib(1) == 1


def test_fib_5():
    assert fib(5) == 5


def test_fib_10():
    assert fib(10) == 55
