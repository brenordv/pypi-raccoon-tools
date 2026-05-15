import math
from datetime import datetime, timedelta, timezone, tzinfo

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

_VALID_UNITS = frozenset({"s", "ms", "us", "ns"})

_VALID_TIME_PIECES = frozenset({
    "milliseconds", "seconds", "minutes", "hours", "days", "weeks",
})

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
    float rounding. Falls back to "datetime.fromtimestamp" for float inputs.

    Args:
        timestamp (int | float): The numeric timestamp value to convert.
        unit (str): Unit of the input: "s", "ms", "us", or "ns".
            Default is "ms".
        tz (tzinfo | None): Target timezone. Defaults to "timezone.utc".
            Pass "None" to get a naive datetime (discouraged).

    Returns:
        datetime: Timezone-aware datetime by default (UTC).

    Raises:
        ValueError: If "unit" is not one of the recognized values or if "timestamp" is not finite.

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


def _plural(count: int, unit: str) -> str:
    """Return ``'count unit'`` with pluralization.

    Examples:
        >>> _plural(1, "year")
        '1 year'
        >>> _plural(2, "year")
        '2 years'
    """
    return f"{count} {unit}" if count == 1 else f"{count} {unit}s"


def _join_time_parts(parts: list[str]) -> str:
    """Join time parts with commas and ``'and'`` before the last element.

    Examples:
        >>> _join_time_parts(["1 year"])
        '1 year'
        >>> _join_time_parts(["1 year", "2 months"])
        '1 year and 2 months'
        >>> _join_time_parts(["1 year", "2 months", "3 days"])
        '1 year, 2 months and 3 days'
    """
    if len(parts) == 1:
        return parts[0]
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


def timedelta_to_readable_elapsed_time(
    delta: timedelta,
    suffix: str | None = "ago",
    zero_delta_label: str = "just now",
    zero_delta_threshold: timedelta | None = timedelta(seconds=60),
) -> str:
    """Convert a timedelta to a human-readable elapsed time string.

    Uses approximate month (30 days) and year (365 days) lengths.

    Args:
        delta: The time difference to format. Must be non-negative.
        suffix: Text appended after the time string (default: ``"ago"``).
            A space is inserted automatically. Pass ``""`` or ``None``
            to omit.
        zero_delta_label: Returned when the delta falls below *zero_delta_threshold* (default: ``"just now"``).
            The suffix is **not** appended to this label.
        zero_delta_threshold: Deltas below this value return
            *zero_delta_label* (default: ``timedelta(seconds=60)``).
            Pass ``None`` to always show the real representation
            (e.g. ``"30 seconds ago"`` instead of ``"just now"``).

    Returns:
        A string like ``"2 years, 3 months and 5 days ago"`` or
        ``"just now"``.

    Raises:
        ValueError: If *delta* is negative.

    Example:
        >>> from datetime import timedelta
        >>> timedelta_to_readable_elapsed_time(timedelta(days=400))
        '1 year, 1 month and 5 days ago'
        >>> timedelta_to_readable_elapsed_time(timedelta(seconds=30))
        'just now'
        >>> timedelta_to_readable_elapsed_time(
        ...     timedelta(seconds=30), zero_delta_threshold=None,
        ... )
        '30 seconds ago'
    """
    if delta < timedelta(0):
        raise ValueError(
            f"delta must be non-negative, got {delta!r}."
        )

    if zero_delta_threshold is not None and delta < zero_delta_threshold:
        return zero_delta_label

    def _format(text: str) -> str:
        if suffix:
            return f"{text} {suffix}"
        return text

    if delta.days >= 365:
        years = delta.days // 365
        remaining_days = delta.days % 365
        months = remaining_days // 30
        days = remaining_days % 30

        parts = [_plural(years, "year")]
        if months > 0:
            parts.append(_plural(months, "month"))
        if days > 0:
            parts.append(_plural(days, "day"))
        return _format(_join_time_parts(parts))

    if delta.days >= 30:
        months = delta.days // 30
        days = delta.days % 30
        parts = [_plural(months, "month")]
        if days > 0:
            parts.append(_plural(days, "day"))
        return _format(_join_time_parts(parts))

    if delta.days > 0:
        parts = [_plural(delta.days, "day")]
        hours = delta.seconds // 3600
        if hours > 0:
            parts.append(_plural(hours, "hour"))
        return _format(_join_time_parts(parts))

    if delta.seconds >= 3600:
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        parts = [_plural(hours, "hour")]
        if minutes > 0:
            parts.append(_plural(minutes, "minute"))
        return _format(_join_time_parts(parts))

    if delta.seconds >= 60:
        return _format(_plural(delta.seconds // 60, "minute"))

    if delta.seconds > 0:
        return _format(_plural(delta.seconds, "second"))

    return zero_delta_label


def time_value_to_readable_elapsed_time(
    value: int | float,
    time_piece: str = "seconds",
    suffix: str | None = "ago",
    zero_delta_label: str = "just now",
    zero_delta_threshold: timedelta | None = timedelta(seconds=60),
) -> str:
    """Convert a numeric time value to a human-readable elapsed time string.

    Convenience wrapper: builds a ``timedelta`` from *value* + *time_piece*,
    then delegates to :func:`timedelta_to_readable_elapsed_time`.

    Args:
        value: The numeric amount (must be non-negative and finite).
        time_piece: Unit — one of ``"milliseconds"``, ``"seconds"``,
            ``"minutes"``, ``"hours"``, ``"days"``, ``"weeks"``
            (default: ``"seconds"``).
        suffix: Text appended after the time string (default: ``"ago"``).
        zero_delta_label: Returned when the resulting delta falls at
            or below *zero_delta_threshold* (default: ``"just now"``).
        zero_delta_threshold: Deltas below this value return
            *zero_delta_label* (default: ``timedelta(seconds=60)``).
            Pass ``None`` to always show the real representation.

    Returns:
        A string like ``"1 hour ago"`` or ``"just now"``.

    Raises:
        ValueError: If *time_piece* is invalid, *value* is negative,
            or *value* is non-finite.

    Example:
        >>> time_value_to_readable_elapsed_time(3600)
        '1 hour ago'
        >>> time_value_to_readable_elapsed_time(2, time_piece="days")
        '2 days ago'
    """
    if time_piece not in _VALID_TIME_PIECES:
        raise ValueError(
            f"Invalid time_piece '{time_piece}'. "
            f"Must be one of: {', '.join(sorted(_VALID_TIME_PIECES))}."
        )

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(
            f"value must be a finite number, got {value}."
        )

    if value < 0:
        raise ValueError(
            f"value must be non-negative, got {value}."
        )

    delta = timedelta(**{time_piece: value})
    return timedelta_to_readable_elapsed_time(
        delta,
        suffix=suffix,
        zero_delta_label=zero_delta_label,
        zero_delta_threshold=zero_delta_threshold,
    )
