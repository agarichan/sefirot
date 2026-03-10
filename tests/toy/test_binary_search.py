from toy.binary_search import binary_search


def test_binary_search_first_element():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_binary_search_middle_element():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_binary_search_last_element():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_binary_search_not_found():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1


def test_binary_search_empty_list():
    assert binary_search([], 1) == -1


def test_binary_search_single_element_found():
    assert binary_search([5], 5) == 0


def test_binary_search_single_element_not_found():
    assert binary_search([5], 3) == -1
