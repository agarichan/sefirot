import pytest
from src.toy.binary_search import binary_search


class TestBinarySearchNormal:
    def test_find_middle_element(self):
        assert binary_search([1, 3, 5, 7, 9], 5) == 2

    def test_find_first_element(self):
        assert binary_search([1, 3, 5, 7, 9], 1) == 0

    def test_find_last_element(self):
        assert binary_search([1, 3, 5, 7, 9], 9) == 4

    def test_element_not_found(self):
        assert binary_search([1, 3, 5, 7, 9], 4) == -1


class TestBinarySearchBoundary:
    def test_empty_list(self):
        assert binary_search([], 5) == -1

    def test_single_element_found(self):
        assert binary_search([1], 1) == 0

    def test_single_element_not_found(self):
        assert binary_search([1], 2) == -1

    def test_two_elements_find_first(self):
        assert binary_search([1, 2], 1) == 0

    def test_two_elements_find_last(self):
        assert binary_search([1, 2], 2) == 1
