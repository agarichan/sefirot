from src.toy.caesar import decrypt, encrypt


class TestEncrypt:
    def test_simple_shift(self) -> None:
        assert encrypt("abc", 1) == "bcd"

    def test_wrap_around(self) -> None:
        assert encrypt("xyz", 3) == "abc"

    def test_preserves_case_and_symbols(self) -> None:
        assert encrypt("Hello, World!", 5) == "Mjqqt, Btwqi!"

    def test_empty_string(self) -> None:
        assert encrypt("", 5) == ""

    def test_zero_shift(self) -> None:
        assert encrypt("abc", 0) == "abc"

    def test_full_rotation(self) -> None:
        assert encrypt("abc", 26) == "abc"


class TestDecrypt:
    def test_simple_decrypt(self) -> None:
        assert decrypt("bcd", 1) == "abc"

    def test_round_trip(self) -> None:
        assert decrypt(encrypt("test", 13), 13) == "test"
