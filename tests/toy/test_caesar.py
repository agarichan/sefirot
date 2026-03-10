import pytest
from toy.caesar import encrypt, decrypt


def test_encrypt_basic():
    assert encrypt("abc", 3) == "def"


def test_encrypt_wrap_around():
    assert encrypt("xyz", 3) == "abc"


def test_encrypt_uppercase():
    assert encrypt("ABC", 3) == "DEF"


def test_encrypt_non_alpha_preserved():
    result = encrypt("Hello, World!", 5)
    assert result == "Mjqqt, Btwqi!"


def test_decrypt_roundtrip():
    assert decrypt(encrypt("Hello", 7), 7) == "Hello"


def test_encrypt_shift_zero():
    assert encrypt("abc", 0) == "abc"
