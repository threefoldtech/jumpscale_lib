from .Container import cpu_used, count_appearance
import pytest


@pytest.mark.parametrize("input,expected", [
    ("1", [1]),
    ("1,2,3", [1, 2, 3]),
    ("1-3", [1, 2, 3]),
    ("1-2,4-5,6-10", [1, 2, 4, 5, 6, 7, 8, 9, 10]),
])
def test_cpu_used(input, expected):
    assert cpu_used(input) == expected
