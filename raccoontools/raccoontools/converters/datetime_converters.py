import math
from datetime import datetime, timedelta, timezone, tzinfo

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

_VALID_UNITS = frozenset({"s", "ms", "us", "ns"})

_INT_UNIT_TO_MICROSECONDS = {
    "s": (1_000_000, 1),
    "ms": (1_000, 1),
    "us": (1, 1),
    "ns": (1, 1_000),
}

_FLOAT_UNIT_TO_SECONDS_DIVISOR = {
    "s": 1,
    "ms": 1_000,
    "us": 1_000_000,
    "ns": 1_000_000_000,
}


def timestamp_to_datetime(
    timestamp: int | float,
    unit: str = "ms",
    tz: tzinfo | None = timezone.utc,
) -> datetime:
    """
    Convert a numeric timestamp to a datetime object.

    Uses integer arithmetic when the input is an int to avoid IEEE-754
    float rounding. Falls back to ``datetime.fromtimestamp`` for float inputs.

    Args:
        timestamp (int | float): The numeric timestamp value to convert.
        unit (str): Unit of the input: ``"s"``, ``"ms"``, ``"us"``, or ``"ns"``.
            Default is ``"ms"``.
        tz (tzinfo | None): Target timezone. Defaults to ``timezone.utc``.
            Pass ``None`` to get a naive datetime (discouraged).

    Returns:
        datetime: Timezone-aware datetime by default (UTC).

    Raises:
        ValueError: If ``unit`` is not one of the recognized values or if
            ``timestamp`` is not finite.

    Example:
        >>> from raccoontools.converters.datetime_converters import timestamp_to_datetime
        >>> dt = timestamp_to_datetime(1_700_000_000_000)
        >>> dt.year, dt.month, dt.day
        (2023, 11, 14)
    """
    if unit not in _VALID_UNITS:
        raise ValueError(
            f"Invalid unit '{unit}'. Must be one of: {', '.join(sorted(_VALID_UNITS))}."
        )

    if isinstance(timestamp, float) and not math.isfinite(timestamp):
        raise ValueError(
            f"Timestamp must be a finite number, got {timestamp}."
        )

    if isinstance(timestamp, int):
        return _convert_int(timestamp, unit, tz)

    return _convert_float(timestamp, unit, tz)


def _convert_int(timestamp: int, unit: str, tz: tzinfo | None) -> datetime:
    """Convert an integer timestamp using exact timedelta arithmetic."""
    mul, div = _INT_UNIT_TO_MICROSECONDS[unit]
    microseconds = timestamp * mul // div

    result = EPOCH + timedelta(microseconds=microseconds)

    if tz is not None and tz != timezone.utc:
        result = result.astimezone(tz)
    elif tz is None:
        result = result.replace(tzinfo=None)

    return result


def _convert_float(timestamp: float, unit: str, tz: tzinfo | None) -> datetime:
    """Convert a float timestamp via datetime.fromtimestamp."""
    seconds = timestamp / _FLOAT_UNIT_TO_SECONDS_DIVISOR[unit]
    return datetime.fromtimestamp(seconds, tz=tz)
