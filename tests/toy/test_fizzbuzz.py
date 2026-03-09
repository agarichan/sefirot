from toy.fizzbuzz import fizzbuzz


class TestFizzbuzz:
    def test_single(self):
        assert fizzbuzz(1) == ["1"]

    def test_fizz(self):
        assert fizzbuzz(3) == ["1", "2", "Fizz"]

    def test_buzz(self):
        result = fizzbuzz(5)
        assert result[-1] == "Buzz"

    def test_fizzbuzz(self):
        result = fizzbuzz(15)
        assert result[-1] == "FizzBuzz"

    def test_length(self):
        assert len(fizzbuzz(15)) == 15

    def test_zero(self):
        assert fizzbuzz(0) == []

    def test_negative(self):
        assert fizzbuzz(-1) == []
