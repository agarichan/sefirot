from src.toy.palindrome import is_palindrome


class TestIsPalindrome:
    def test_racecar(self):
        assert is_palindrome("racecar") is True

    def test_hello(self):
        assert is_palindrome("hello") is False

    def test_ignore_spaces(self):
        assert is_palindrome("A man a plan a canal Panama") is True

    def test_ignore_case(self):
        assert is_palindrome("Was It A Rat I Saw") is True

    def test_empty_string(self):
        assert is_palindrome("") is True

    def test_single_char(self):
        assert is_palindrome("a") is True
