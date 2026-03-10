import pytest
from toy.factorial import factorial


def test_factorial_5():
    assert factorial(5) == 120


def test_factorial_10():
    assert factorial(10) == 3628800


def test_factorial_0():
    assert factorial(0) == 1


def test_factorial_1():
    assert factorial(1) == 1


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-1)
