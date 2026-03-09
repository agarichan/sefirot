from src.toy.reverse import reverse_string, reverse_words


class TestReverseString:
    def test_hello(self):
        assert reverse_string("hello") == "olleh"

    def test_empty(self):
        assert reverse_string("") == ""

    def test_single_char(self):
        assert reverse_string("a") == "a"

    def test_two_chars(self):
        assert reverse_string("ab") == "ba"


class TestReverseWords:
    def test_two_words(self):
        assert reverse_words("hello world") == "world hello"

    def test_single_word(self):
        assert reverse_words("one") == "one"

    def test_empty(self):
        assert reverse_words("") == ""

    def test_three_words(self):
        assert reverse_words("a b c") == "c b a"
