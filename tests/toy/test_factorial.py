import pytest

from toy.factorial import factorial


class TestFactorial:
    def test_zero(self):
        assert factorial(0) == 1

    def test_one(self):
        assert factorial(1) == 1

    def test_five(self):
        assert factorial(5) == 120

    def test_ten(self):
        assert factorial(10) == 3628800

    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            factorial(-1)
