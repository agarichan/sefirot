import pytest
from src.toy.fizzbuzz import fizzbuzz


class TestFizzbuzzNormal:
    def test_fizzbuzz_15(self):
        result = fizzbuzz(15)
        assert result == [
            "1", "2", "Fizz", "4", "Buzz",
            "Fizz", "7", "8", "Fizz", "Buzz",
            "11", "Fizz", "13", "14", "FizzBuzz",
        ]

    def test_fizzbuzz_1(self):
        assert fizzbuzz(1) == ["1"]

    def test_fizzbuzz_3(self):
        assert fizzbuzz(3) == ["1", "2", "Fizz"]

    def test_fizzbuzz_5_fifth_element(self):
        result = fizzbuzz(5)
        assert result[4] == "Buzz"


class TestFizzbuzzBoundary:
    def test_fizzbuzz_0(self):
        assert fizzbuzz(0) == []


class TestFizzbuzzError:
    def test_fizzbuzz_negative(self):
        with pytest.raises(ValueError):
            fizzbuzz(-1)
