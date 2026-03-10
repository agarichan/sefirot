import pytest
from toy.reverse import reverse_string, reverse_words


def test_reverse_string_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_string_empty():
    assert reverse_string("") == ""


def test_reverse_string_single():
    assert reverse_string("a") == "a"


def test_reverse_string_palindrome():
    assert reverse_string("racecar") == "racecar"


def test_reverse_words_normal():
    assert reverse_words("hello world") == "world hello"


def test_reverse_words_single():
    assert reverse_words("hello") == "hello"


def test_reverse_words_empty():
    assert reverse_words("") == ""
