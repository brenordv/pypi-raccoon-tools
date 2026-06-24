from datetime import datetime

import pytest

from raccoontools.comparators.dict_comparators import (
    DictComparison,
    DictDiff,
    DictListComparison,
    DictListDiff,
    compare_dict_lists,
    compare_dicts,
    dict_lists_are_equal,
    dicts_are_equal,
)


# ---------------------------------------------------------------------------
# dicts_are_equal
# ---------------------------------------------------------------------------
class TestDictsAreEqual:
    def test_identical_flat_dicts(self):
        assert dicts_are_equal({"a": 1, "b": 2}, {"a": 1, "b": 2})

    def test_key_order_is_ignored(self):
        assert dicts_are_equal({"a": 1, "b": 2}, {"b": 2, "a": 1})

    def test_different_values(self):
        assert not dicts_are_equal({"a": 1}, {"a": 2})

    def test_missing_key(self):
        assert not dicts_are_equal({"a": 1, "b": 2}, {"a": 1})

    def test_extra_key(self):
        assert not dicts_are_equal({"a": 1}, {"a": 1, "b": 2})

    def test_empty_dicts_are_equal(self):
        assert dicts_are_equal({}, {})

    def test_nested_dicts_equal(self):
        a = {"user": {"name": "Ada", "address": {"zip": "12345"}}}
        b = {"user": {"address": {"zip": "12345"}, "name": "Ada"}}
        assert dicts_are_equal(a, b)

    def test_nested_dicts_unequal(self):
        a = {"user": {"address": {"zip": "12345"}}}
        b = {"user": {"address": {"zip": "54321"}}}
        assert not dicts_are_equal(a, b)

    def test_datetime_values_equal(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        assert dicts_are_equal({"t": dt}, {"t": datetime(2024, 1, 1, 12, 0, 0)})

    def test_datetime_values_unequal(self):
        assert not dicts_are_equal(
            {"t": datetime(2024, 1, 1)}, {"t": datetime(2024, 1, 2)}
        )

    def test_nested_list_order_is_significant(self):
        # Lists nested inside dicts follow native '==' (order matters).
        assert not dicts_are_equal({"items": [1, 2, 3]}, {"items": [3, 2, 1]})

    def test_nested_list_equal_when_same_order(self):
        assert dicts_are_equal({"items": [1, 2, 3]}, {"items": [1, 2, 3]})

    def test_same_object_is_equal_to_itself(self):
        d = {"x": float("nan")}
        # Same object on both sides: identity short-circuit makes it equal,
        # mirroring dict '==' even though NaN != NaN.
        assert dicts_are_equal(d, d)


# ---------------------------------------------------------------------------
# compare_dicts
# ---------------------------------------------------------------------------
class TestCompareDicts:
    def test_returns_dict_comparison_type(self):
        result = compare_dicts({"a": 1}, {"a": 1})
        assert isinstance(result, DictComparison)
        assert isinstance(result.differences, DictDiff)

    def test_equal_dicts_have_empty_diff(self):
        result = compare_dicts({"a": 1, "b": 2}, {"b": 2, "a": 1})
        assert result.are_equal is True
        assert result.differences == DictDiff(added={}, removed={}, changed={})

    def test_changed_value_at_root(self):
        result = compare_dicts({"role": "dev"}, {"role": "lead"})
        assert result.are_equal is False
        assert result.differences.changed == {"role": ("dev", "lead")}
        assert result.differences.added == {}
        assert result.differences.removed == {}

    def test_added_key(self):
        result = compare_dicts({"a": 1}, {"a": 1, "b": 2})
        assert result.differences.added == {"b": 2}
        assert result.differences.changed == {}
        assert result.differences.removed == {}

    def test_removed_key(self):
        result = compare_dicts({"a": 1, "b": 2}, {"a": 1})
        assert result.differences.removed == {"b": 2}
        assert result.differences.added == {}

    def test_nested_changed_uses_dotted_path(self):
        a = {"user": {"address": {"zip": "12345"}}}
        b = {"user": {"address": {"zip": "54321"}}}
        result = compare_dicts(a, b)
        assert result.differences.changed == {
            "user.address.zip": ("12345", "54321")
        }

    def test_nested_added_and_removed_paths(self):
        a = {"user": {"name": "Ada"}}
        b = {"user": {"role": "lead"}}
        result = compare_dicts(a, b)
        assert result.differences.removed == {"user.name": "Ada"}
        assert result.differences.added == {"user.role": "lead"}
        assert result.differences.changed == {}

    def test_dict_replaced_by_scalar_is_changed(self):
        a = {"user": {"name": "Ada"}}
        b = {"user": 5}
        result = compare_dicts(a, b)
        assert result.differences.changed == {"user": ({"name": "Ada"}, 5)}

    def test_nested_list_reported_as_single_changed_entry(self):
        a = {"items": [1, 2, 3]}
        b = {"items": [3, 2, 1]}
        result = compare_dicts(a, b)
        assert result.differences.changed == {"items": ([1, 2, 3], [3, 2, 1])}

    def test_mixed_changes_in_one_pass(self):
        a = {"keep": 1, "drop": 2, "mod": 3}
        b = {"keep": 1, "mod": 30, "new": 4}
        result = compare_dicts(a, b)
        assert result.differences.removed == {"drop": 2}
        assert result.differences.added == {"new": 4}
        assert result.differences.changed == {"mod": (3, 30)}

    def test_unpackable_like_a_tuple(self):
        are_equal, differences = compare_dicts({"a": 1}, {"a": 2})
        assert are_equal is False
        assert differences.changed == {"a": (1, 2)}

    def test_non_string_keys_are_stringified_in_path(self):
        result = compare_dicts({1: "a"}, {1: "b"})
        assert result.differences.changed == {"1": ("a", "b")}


# ---------------------------------------------------------------------------
# dict_lists_are_equal
# ---------------------------------------------------------------------------
class TestDictListsAreEqual:
    def test_identical_lists(self):
        assert dict_lists_are_equal([{"a": 1}], [{"a": 1}])

    def test_order_is_ignored(self):
        a = [{"id": 1}, {"id": 2}, {"id": 3}]
        b = [{"id": 3}, {"id": 1}, {"id": 2}]
        assert dict_lists_are_equal(a, b)

    def test_both_empty(self):
        assert dict_lists_are_equal([], [])

    def test_different_lengths(self):
        assert not dict_lists_are_equal([{"a": 1}], [{"a": 1}, {"a": 1}])

    def test_duplicates_are_counted(self):
        a = [{"x": 1}, {"x": 1}]
        b = [{"x": 1}, {"x": 1}]
        assert dict_lists_are_equal(a, b)

    def test_duplicate_count_mismatch(self):
        a = [{"x": 1}, {"x": 1}]
        b = [{"x": 1}, {"x": 2}]
        assert not dict_lists_are_equal(a, b)

    def test_nested_structures_with_unordered_outer_list(self):
        a = [{"tags": ["a", "b"], "n": 1}, {"n": 2}]
        b = [{"n": 2}, {"n": 1, "tags": ["a", "b"]}]
        assert dict_lists_are_equal(a, b)

    def test_nested_list_order_still_matters(self):
        a = [{"tags": ["a", "b"]}]
        b = [{"tags": ["b", "a"]}]
        assert not dict_lists_are_equal(a, b)

    def test_datetime_in_elements(self):
        dt = datetime(2024, 1, 1)
        assert dict_lists_are_equal([{"t": dt}], [{"t": datetime(2024, 1, 1)}])


# ---------------------------------------------------------------------------
# compare_dict_lists
# ---------------------------------------------------------------------------
class TestCompareDictLists:
    def test_returns_dict_list_comparison_type(self):
        result = compare_dict_lists([{"a": 1}], [{"a": 1}])
        assert isinstance(result, DictListComparison)
        assert isinstance(result.differences, DictListDiff)

    def test_equal_lists_have_empty_diff(self):
        result = compare_dict_lists([{"a": 1}], [{"a": 1}])
        assert result.are_equal is True
        assert result.differences == DictListDiff(only_in_a=[], only_in_b=[])

    def test_only_in_a_and_only_in_b(self):
        result = compare_dict_lists([{"id": 1}, {"id": 2}], [{"id": 2}, {"id": 3}])
        assert result.are_equal is False
        assert result.differences.only_in_a == [{"id": 1}]
        assert result.differences.only_in_b == [{"id": 3}]

    def test_only_in_a_preserves_source_order(self):
        a = [{"id": 3}, {"id": 1}, {"id": 2}]
        b = [{"id": 2}]
        result = compare_dict_lists(a, b)
        assert result.differences.only_in_a == [{"id": 3}, {"id": 1}]
        assert result.differences.only_in_b == []

    def test_duplicates_are_reported_per_surplus_count(self):
        a = [{"x": 1}, {"x": 1}, {"x": 1}]
        b = [{"x": 1}]
        result = compare_dict_lists(a, b)
        assert result.differences.only_in_a == [{"x": 1}, {"x": 1}]
        assert result.differences.only_in_b == []

    def test_reordered_lists_are_equal(self):
        a = [{"id": 1}, {"id": 2}]
        b = [{"id": 2}, {"id": 1}]
        result = compare_dict_lists(a, b)
        assert result.are_equal is True
        assert result.differences.only_in_a == []
        assert result.differences.only_in_b == []

    def test_unpackable_like_a_tuple(self):
        are_equal, differences = compare_dict_lists([{"a": 1}], [{"a": 2}])
        assert are_equal is False
        assert differences.only_in_a == [{"a": 1}]
        assert differences.only_in_b == [{"a": 2}]


# ---------------------------------------------------------------------------
# Canonicalization of complex leaf types in list comparison
# ---------------------------------------------------------------------------
class TestListLeafTypes:
    def test_set_values_are_order_independent(self):
        a = [{"tags": {1, 2, 3}}]
        b = [{"tags": {3, 2, 1}}]
        assert dict_lists_are_equal(a, b)

    def test_frozenset_values(self):
        a = [{"tags": frozenset({1, 2})}]
        b = [{"tags": frozenset({2, 1})}]
        assert dict_lists_are_equal(a, b)

    def test_tuple_values_are_order_sensitive(self):
        assert dict_lists_are_equal([{"t": (1, 2)}], [{"t": (1, 2)}])
        assert not dict_lists_are_equal([{"t": (1, 2)}], [{"t": (2, 1)}])

    def test_container_type_does_not_collide(self):
        # A list and a tuple holding the same items must not be treated equal.
        assert not dict_lists_are_equal([{"v": [1, 2]}], [{"v": (1, 2)}])

    def test_unhashable_leaf_raises_type_error(self):
        with pytest.raises(TypeError, match="unhashable"):
            compare_dict_lists([{"data": bytearray(b"x")}], [])


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
class TestValidation:
    @pytest.mark.parametrize("value", [None, 1, "x", ["a"], (1, 2), {1, 2}])
    def test_compare_dicts_rejects_non_dict_a(self, value):
        with pytest.raises(TypeError):
            compare_dicts(value, {})

    @pytest.mark.parametrize("value", [None, 1, "x", ["a"]])
    def test_compare_dicts_rejects_non_dict_b(self, value):
        with pytest.raises(TypeError):
            compare_dicts({}, value)

    @pytest.mark.parametrize("value", [None, 1, "x", {"a": 1}])
    def test_compare_dict_lists_rejects_non_list_a(self, value):
        with pytest.raises(TypeError):
            compare_dict_lists(value, [])

    @pytest.mark.parametrize("value", [None, 1, "x", {"a": 1}])
    def test_compare_dict_lists_rejects_non_list_b(self, value):
        with pytest.raises(TypeError):
            compare_dict_lists([], value)

    def test_compare_dict_lists_rejects_non_dict_element(self):
        with pytest.raises(TypeError):
            compare_dict_lists([{"a": 1}, "not a dict"], [])

    def test_error_message_names_offending_index(self):
        with pytest.raises(TypeError, match="index 1"):
            compare_dict_lists([{"a": 1}, 42], [])

    def test_dicts_are_equal_rejects_non_dict(self):
        with pytest.raises(TypeError):
            dicts_are_equal({"a": 1}, None)

    def test_dict_lists_are_equal_rejects_non_list(self):
        with pytest.raises(TypeError):
            dict_lists_are_equal([{"a": 1}], None)


# ---------------------------------------------------------------------------
# Consistency invariant: *_are_equal must agree with compare_* .are_equal
# ---------------------------------------------------------------------------
class TestConsistency:
    _DICT_CASES = [
        ({}, {}),
        ({"a": 1}, {"a": 1}),
        ({"a": 1}, {"a": 2}),
        ({"a": {"b": 1}}, {"a": {"b": 1}}),
        ({"a": {"b": 1}}, {"a": {"b": 2}}),
        ({"a": [1, 2]}, {"a": [2, 1]}),
    ]

    _LIST_CASES = [
        ([], []),
        ([{"a": 1}], [{"a": 1}]),
        ([{"a": 1}], [{"a": 2}]),
        ([{"a": 1}, {"b": 2}], [{"b": 2}, {"a": 1}]),
        ([{"a": 1}, {"a": 1}], [{"a": 1}]),
    ]

    @pytest.mark.parametrize(("a", "b"), _DICT_CASES)
    def test_dict_bool_matches_comparison(self, a, b):
        assert dicts_are_equal(a, b) == compare_dicts(a, b).are_equal

    @pytest.mark.parametrize(("a", "b"), _LIST_CASES)
    def test_list_bool_matches_comparison(self, a, b):
        assert dict_lists_are_equal(a, b) == compare_dict_lists(a, b).are_equal
