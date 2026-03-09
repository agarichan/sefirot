import pytest
from src.toy.caesar import encrypt, decrypt


class TestEncrypt:
    def test_simple_shift(self):
        assert encrypt("abc", 3) == "def"

    def test_wrap_around(self):
        assert encrypt("xyz", 3) == "abc"

    def test_mixed_case_and_punctuation(self):
        assert encrypt("Hello, World!", 5) == "Mjqqt, Btwqi!"

    def test_empty_string(self):
        assert encrypt("", 5) == ""

    def test_zero_shift(self):
        assert encrypt("abc", 0) == "abc"

    def test_full_rotation(self):
        assert encrypt("abc", 26) == "abc"

    def test_negative_shift(self):
        assert encrypt("abc", -1) == "zab"


class TestDecrypt:
    def test_simple_decrypt(self):
        assert decrypt("def", 3) == "abc"

    def test_round_trip(self):
        assert decrypt(encrypt("test", 13), 13) == "test"

    def test_round_trip_negative(self):
        assert decrypt(encrypt("Hello!", -7), -7) == "Hello!"

    def test_large_shift_round_trip(self):
        assert decrypt(encrypt("XYZ", 52), 52) == "XYZ"
