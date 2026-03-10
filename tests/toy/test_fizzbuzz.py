import pytest
from toy.fizzbuzz import fizzbuzz


def test_fizzbuzz_15():
    result = fizzbuzz(15)
    expected = [
        "1", "2", "Fizz", "4", "Buzz",
        "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]
    assert result == expected


def test_fizzbuzz_boundary():
    assert fizzbuzz(1) == ["1"]


def test_fizz():
    result = fizzbuzz(3)
    assert result[2] == "Fizz"


def test_buzz():
    result = fizzbuzz(5)
    assert result[4] == "Buzz"


def test_fizzbuzz_element():
    result = fizzbuzz(15)
    assert result[14] == "FizzBuzz"
