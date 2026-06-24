"""Utilities for comparing dictionaries and lists of dictionaries.

These helpers complement Python's built-in ``==`` operator by also reporting
*what* differs, in a streamlined and predictable structure.

Two kinds of comparison are provided:

* **Dict comparison** (``dicts_are_equal`` / ``compare_dicts``) performs a deep,
  key-order-independent comparison. Nested dictionaries are recursed into;
  every other value (including nested lists, ``datetime`` objects and custom
  types) is compared as an opaque leaf via ``==``.
* **List-of-dict comparison** (``dict_lists_are_equal`` / ``compare_dict_lists``)
  compares two lists of dictionaries **ignoring their order** (the lists are
  treated as multisets, so duplicates are accounted for).

The ``*_are_equal`` functions delegate to their ``compare_*`` counterparts so
the boolean and the detailed result can never disagree.
"""

from collections import Counter
from collections.abc import Hashable
from typing import Any, NamedTuple


class DictDiff(NamedTuple):
    """Differences between two dictionaries.

    Each mapping is keyed by a dotted path to the differing key
    (e.g. ``"user.address.zip"``). Non-string keys are rendered with ``str``.
    """

    added: dict[str, Any]
    """Paths present only in ``b``, mapped to their value in ``b``."""

    removed: dict[str, Any]
    """Paths present only in ``a``, mapped to their value in ``a``."""

    changed: dict[str, tuple[Any, Any]]
    """Paths present in both, mapped to ``(value_in_a, value_in_b)``."""


class DictComparison(NamedTuple):
    """Result of :func:`compare_dicts`."""

    are_equal: bool
    differences: DictDiff


class DictListDiff(NamedTuple):
    """Differences between two lists of dictionaries (order-independent)."""

    only_in_a: list[dict]
    """Elements of ``a`` with no matching element left in ``b`` (a's order)."""

    only_in_b: list[dict]
    """Elements of ``b`` with no matching element left in ``a`` (b's order)."""


class DictListComparison(NamedTuple):
    """Result of :func:`compare_dict_lists`."""

    are_equal: bool
    differences: DictListDiff


def _ensure_dict(value: Any, name: str) -> None:
    """Raise ``TypeError`` if *value* is not a ``dict``."""
    if not isinstance(value, dict):
        raise TypeError(
            f"Expected '{name}' to be a dict, got {type(value).__name__}."
        )


def _ensure_list_of_dicts(value: Any, name: str) -> None:
    """Raise ``TypeError`` if *value* is not a ``list`` of ``dict`` items."""
    if not isinstance(value, list):
        raise TypeError(
            f"Expected '{name}' to be a list, got {type(value).__name__}."
        )

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise TypeError(
                f"Expected every item in '{name}' to be a dict, but the item "
                f"at index {index} is {type(item).__name__}."
            )


def _join_path(prefix: str, key: Any) -> str:
    """Append *key* to a dotted *prefix*, coercing the key to ``str``."""
    key_str = str(key)
    return f"{prefix}.{key_str}" if prefix else key_str


def _diff_dicts(a: dict, b: dict, prefix: str = "") -> DictDiff:
    """Recursively diff two dictionaries into added/removed/changed maps.

    Nested dictionaries are recursed into; any other pair of values is compared
    with ``==`` and, when unequal, reported as a single ``changed`` entry.
    """
    added: dict[str, Any] = {}
    removed: dict[str, Any] = {}
    changed: dict[str, tuple[Any, Any]] = {}

    for key, a_value in a.items():
        path = _join_path(prefix, key)

        if key not in b:
            removed[path] = a_value
            continue

        b_value = b[key]

        # Identity short-circuit: mirrors dict '==' (which checks 'is' first),
        # so a value compared against itself is always equal (e.g. NaN).
        if a_value is b_value:
            continue

        if isinstance(a_value, dict) and isinstance(b_value, dict):
            nested = _diff_dicts(a_value, b_value, path)
            added.update(nested.added)
            removed.update(nested.removed)
            changed.update(nested.changed)
        elif a_value != b_value:
            changed[path] = (a_value, b_value)

    for key, b_value in b.items():
        if key not in a:
            added[_join_path(prefix, key)] = b_value

    return DictDiff(added=added, removed=removed, changed=changed)


def compare_dicts(a: dict, b: dict) -> DictComparison:
    """Deeply compare two dictionaries and report their differences.

    The comparison ignores key order and recurses into nested dictionaries.
    Any other value (nested lists, ``datetime`` objects, custom types, ...) is
    compared as an opaque leaf via ``==``.

    Args:
        a: The left-hand dictionary.
        b: The right-hand dictionary.

    Returns:
        DictComparison: A named tuple ``(are_equal, differences)`` where
        ``differences`` is a :class:`DictDiff`. The result is unpackable, so
        ``are_equal, diff = compare_dicts(a, b)`` works.

    Raises:
        TypeError: If *a* or *b* is not a ``dict``.

    Example:
        >>> from raccoontools.comparators.dict_comparators import compare_dicts
        >>> result = compare_dicts(
        ...     {"name": "Ada", "role": "dev"},
        ...     {"name": "Ada", "role": "lead", "active": True},
        ... )
        >>> result.are_equal
        False
        >>> result.differences.changed
        {'role': ('dev', 'lead')}
        >>> result.differences.added
        {'active': True}
    """
    _ensure_dict(a, "a")
    _ensure_dict(b, "b")

    differences = _diff_dicts(a, b)
    are_equal = not (differences.added or differences.removed or differences.changed)
    return DictComparison(are_equal=are_equal, differences=differences)


def dicts_are_equal(a: dict, b: dict) -> bool:
    """Return ``True`` if two dictionaries are deeply equal.

    Convenience wrapper over :func:`compare_dicts` that discards the detailed
    diff. Key order is ignored and nested dictionaries are compared recursively.

    Args:
        a: The left-hand dictionary.
        b: The right-hand dictionary.

    Returns:
        bool: ``True`` if the dictionaries are equal, ``False`` otherwise.

    Raises:
        TypeError: If *a* or *b* is not a ``dict``.

    Example:
        >>> from raccoontools.comparators.dict_comparators import dicts_are_equal
        >>> dicts_are_equal({"a": 1, "b": 2}, {"b": 2, "a": 1})
        True
    """
    return compare_dicts(a, b).are_equal


def _freeze(value: Any) -> Hashable:
    """Convert *value* into a stable, hashable, order-aware representation.

    Containers are type-tagged so that, for example, a ``dict`` can never
    collide with a ``list`` that happens to hold the same items. Dictionaries
    and sets are frozen order-independently; lists and tuples preserve order.
    Scalars are returned unchanged, which keeps ``==`` semantics (note that
    ``1``, ``1.0`` and ``True`` therefore compare equal).

    Raises:
        TypeError: If *value* contains an unhashable leaf that is not one of
            the recognized container types.
    """
    if isinstance(value, dict):
        return ("__dict__", frozenset(
            (_freeze(k), _freeze(v)) for k, v in value.items()
        ))

    if isinstance(value, (set, frozenset)):
        return ("__set__", frozenset(_freeze(item) for item in value))

    if isinstance(value, list):
        return ("__list__", tuple(_freeze(item) for item in value))

    if isinstance(value, tuple):
        return ("__tuple__", tuple(_freeze(item) for item in value))

    try:
        hash(value)
    except TypeError as exc:
        raise TypeError(
            f"Cannot compare lists containing an unhashable value of type "
            f"{type(value).__name__}: {value!r}."
        ) from exc

    return value


def _collect_surplus(
    originals: list[dict],
    frozen: list[Hashable],
    surplus: Counter,
) -> list[dict]:
    """Return the original dicts that make up a multiset *surplus*.

    Iterates *originals* in order, emitting each element while the surplus count
    for its frozen key remains positive. This preserves the source order and
    respects duplicate counts.
    """
    if not surplus:
        return []

    remaining = dict(surplus)
    result: list[dict] = []
    for original, key in zip(originals, frozen):
        if remaining.get(key, 0) > 0:
            result.append(original)
            remaining[key] -= 1

    return result


def compare_dict_lists(a: list[dict], b: list[dict]) -> DictListComparison:
    """Compare two lists of dictionaries, ignoring element order.

    The lists are treated as multisets: order is irrelevant but duplicates are
    counted. Each element is compared deeply (nested dicts, lists, ``datetime``,
    etc.). The result lists the elements that could not be matched between the
    two inputs.

    Args:
        a: The left-hand list of dictionaries.
        b: The right-hand list of dictionaries.

    Returns:
        DictListComparison: A named tuple ``(are_equal, differences)`` where
        ``differences`` is a :class:`DictListDiff`. ``only_in_a`` preserves the
        order of *a*; ``only_in_b`` preserves the order of *b*.

    Raises:
        TypeError: If *a* or *b* is not a ``list``, if any element is not a
            ``dict``, or if an element contains an unhashable leaf value.

    Example:
        >>> from raccoontools.comparators.dict_comparators import compare_dict_lists
        >>> result = compare_dict_lists(
        ...     [{"id": 1}, {"id": 2}],
        ...     [{"id": 2}, {"id": 3}],
        ... )
        >>> result.are_equal
        False
        >>> result.differences.only_in_a
        [{'id': 1}]
        >>> result.differences.only_in_b
        [{'id': 3}]
    """
    _ensure_list_of_dicts(a, "a")
    _ensure_list_of_dicts(b, "b")

    frozen_a = [_freeze(item) for item in a]
    frozen_b = [_freeze(item) for item in b]

    counter_a = Counter(frozen_a)
    counter_b = Counter(frozen_b)

    only_in_a = _collect_surplus(a, frozen_a, counter_a - counter_b)
    only_in_b = _collect_surplus(b, frozen_b, counter_b - counter_a)

    are_equal = not only_in_a and not only_in_b
    return DictListComparison(
        are_equal=are_equal,
        differences=DictListDiff(only_in_a=only_in_a, only_in_b=only_in_b),
    )


def dict_lists_are_equal(a: list[dict], b: list[dict]) -> bool:
    """Return ``True`` if two lists of dictionaries are equal, ignoring order.

    Convenience wrapper over :func:`compare_dict_lists` that discards the
    detailed diff. The lists are treated as multisets (duplicates counted).

    Args:
        a: The left-hand list of dictionaries.
        b: The right-hand list of dictionaries.

    Returns:
        bool: ``True`` if the lists hold the same dictionaries (in any order),
        ``False`` otherwise.

    Raises:
        TypeError: If *a* or *b* is not a ``list``, if any element is not a
            ``dict``, or if an element contains an unhashable leaf value.

    Example:
        >>> from raccoontools.comparators.dict_comparators import dict_lists_are_equal
        >>> dict_lists_are_equal([{"id": 1}, {"id": 2}], [{"id": 2}, {"id": 1}])
        True
    """
    return compare_dict_lists(a, b).are_equal
