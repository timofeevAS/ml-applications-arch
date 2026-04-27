from general.sum import sum


def test_positive_numbers():
    assert sum(1, 1) == 2

def test_zero():
    assert sum(5, 0) == 5

def test_negative_numbers():
    assert sum(-1, -2) == -3
