import pytest
from src.toy.reverse import reverse_string, reverse_words


class TestReverseString:
    def test_normal_string(self):
        assert reverse_string("hello") == "olleh"

    def test_abcde(self):
        assert reverse_string("abcde") == "edcba"

    def test_empty_string(self):
        assert reverse_string("") == ""

    def test_single_char(self):
        assert reverse_string("a") == "a"


class TestReverseWords:
    def test_two_words(self):
        assert reverse_words("hello world") == "world hello"

    def test_multiple_words(self):
        assert reverse_words("the quick brown fox") == "fox brown quick the"

    def test_empty_string(self):
        assert reverse_words("") == ""

    def test_single_word(self):
        assert reverse_words("hello") == "hello"

    def test_extra_whitespace(self):
        assert reverse_words("  hello  world  ") == "world hello"
