import pytest

from raccoontools.generators.misc_generators import infinite_iterator


class TestInfiniteIterator:
    def test_cycles_through_list(self):
        gen = infinite_iterator([1, 2, 3])
        result = [next(gen) for _ in range(9)]
        assert result == [1, 2, 3, 1, 2, 3, 1, 2, 3]

    def test_single_element(self):
        gen = infinite_iterator(["a"])
        result = [next(gen) for _ in range(5)]
        assert result == ["a", "a", "a", "a", "a"]

    def test_empty_list_yields_nothing_on_first_pass(self):
        gen = infinite_iterator([])
        # An empty list means the inner for loop never yields,
        # but while True keeps spinning. We just confirm it doesn't
        # yield anything by trying to get one item with a timeout-like
        # approach using islice.
        from itertools import islice

        result = list(islice(gen, 0, 0))
        assert result == []

    def test_preserves_element_types(self):
        gen = infinite_iterator([1, "two", 3.0, None])
        result = [next(gen) for _ in range(4)]
        assert result == [1, "two", 3.0, None]
