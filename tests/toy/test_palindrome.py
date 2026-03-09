import pytest
from src.toy.palindrome import is_palindrome


# 正常系
def test_racecar():
    assert is_palindrome("racecar") is True


def test_hello():
    assert is_palindrome("hello") is False


def test_sentence_with_spaces():
    assert is_palindrome("A man a plan a canal Panama") is True


def test_sentence_was_it_a_car():
    assert is_palindrome("Was it a car or a cat I saw") is True


# 境界値
def test_empty_string():
    assert is_palindrome("") is True


def test_single_char():
    assert is_palindrome("a") is True


def test_case_insensitive():
    assert is_palindrome("Race Car") is True
