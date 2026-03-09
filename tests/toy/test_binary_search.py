from src.toy.binary_search import binary_search


class TestBinarySearchFound:
    def test_middle_element(self):
        assert binary_search([1, 2, 3, 4, 5], 3) == 2

    def test_first_element(self):
        assert binary_search([1, 2, 3, 4, 5], 1) == 0

    def test_last_element(self):
        assert binary_search([1, 2, 3, 4, 5], 5) == 4


class TestBinarySearchNotFound:
    def test_greater_than_all(self):
        assert binary_search([1, 2, 3, 4, 5], 6) == -1

    def test_less_than_all(self):
        assert binary_search([1, 2, 3, 4, 5], 0) == -1


class TestBinarySearchBoundary:
    def test_empty_list(self):
        assert binary_search([], 1) == -1

    def test_single_element_found(self):
        assert binary_search([1], 1) == 0

    def test_single_element_not_found(self):
        assert binary_search([1], 2) == -1
