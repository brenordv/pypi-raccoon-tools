from datetime import datetime, timedelta, timezone

import pytest

from raccoontools.converters.datetime_converters import (
    EPOCH,
    _join_time_parts,
    _plural,
    time_value_to_readable_elapsed_time,
    timedelta_to_readable_elapsed_time,
    timestamp_to_datetime,
)

UTC = timezone.utc


class TestTimestampToDatetimeMilliseconds:
    def test_epoch_zero(self):
        result = timestamp_to_datetime(0)
        assert result == datetime(1970, 1, 1, tzinfo=UTC)

    def test_known_nightscout_timestamp(self):
        result = timestamp_to_datetime(1_700_000_000_000)
        assert result == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)

    def test_negative_timestamp_before_epoch(self):
        result = timestamp_to_datetime(-86_400_000)
        assert result == datetime(1969, 12, 31, tzinfo=UTC)

    def test_millisecond_precision_preserved(self):
        result = timestamp_to_datetime(1_700_000_000_123)
        assert result.microsecond == 123_000

    def test_large_future_timestamp(self):
        result = timestamp_to_datetime(32_503_680_000_000)
        assert result == datetime(3000, 1, 1, tzinfo=UTC)


class TestTimestampToDatetimeUnits:
    def test_seconds_int(self):
        result = timestamp_to_datetime(1_700_000_000, unit="s")
        assert result == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)

    def test_seconds_float(self):
        result = timestamp_to_datetime(1_700_000_000.123, unit="s")
        assert abs(result.microsecond - 123_000) <= 1

    def test_microseconds(self):
        result = timestamp_to_datetime(1_700_000_000_000_000, unit="us")
        assert result == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)

    def test_microseconds_with_precision(self):
        result = timestamp_to_datetime(1_700_000_000_123_456, unit="us")
        assert result.microsecond == 123_456

    def test_nanoseconds(self):
        result = timestamp_to_datetime(1_700_000_000_000_000_000, unit="ns")
        assert result == datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC)

    def test_nanoseconds_truncates_sub_microsecond(self):
        result = timestamp_to_datetime(1_700_000_000_123_456_789, unit="ns")
        assert result.microsecond == 123_456


class TestTimestampToDatetimeTimezone:
    def test_default_is_utc(self):
        result = timestamp_to_datetime(0)
        assert result.tzinfo == UTC

    def test_explicit_utc(self):
        result = timestamp_to_datetime(0, tz=UTC)
        assert result == timestamp_to_datetime(0)

    def test_fixed_offset_positive(self):
        tz_ist = timezone(timedelta(hours=5, minutes=30))
        result = timestamp_to_datetime(0, tz=tz_ist)
        assert result.hour == 5
        assert result.minute == 30

    def test_fixed_offset_negative(self):
        tz_minus3 = timezone(timedelta(hours=-3))
        result = timestamp_to_datetime(0, tz=tz_minus3)
        assert result.day == 31
        assert result.hour == 21

    def test_naive_datetime_when_tz_none(self):
        result = timestamp_to_datetime(0, tz=None)
        assert result.tzinfo is None


class TestTimestampToDatetimeIntVsFloat:
    def test_int_path_exact_microseconds(self):
        result = timestamp_to_datetime(1_700_000_000_123)
        assert result.microsecond == 123_000

    def test_float_seconds_reasonable_precision(self):
        result = timestamp_to_datetime(1_700_000_000.123456, unit="s")
        assert abs(result.microsecond - 123_456) <= 1

    def test_int_and_float_equivalent_for_round_values(self):
        int_result = timestamp_to_datetime(1_700_000_000_000)
        float_result = timestamp_to_datetime(1_700_000_000.0, unit="s")
        assert int_result == float_result


class TestTimestampToDatetimeValidation:
    def test_invalid_unit_raises_valueerror(self):
        with pytest.raises(ValueError, match="Invalid unit"):
            timestamp_to_datetime(0, unit="hours")

    def test_nan_raises_valueerror(self):
        with pytest.raises(ValueError, match="finite"):
            timestamp_to_datetime(float("nan"))

    def test_inf_raises_valueerror(self):
        with pytest.raises(ValueError, match="finite"):
            timestamp_to_datetime(float("inf"))

    def test_negative_inf_raises_valueerror(self):
        with pytest.raises(ValueError, match="finite"):
            timestamp_to_datetime(float("-inf"))


class TestEpochConstant:
    def test_epoch_is_utc_aware(self):
        assert EPOCH.tzinfo == UTC

    def test_epoch_is_1970(self):
        assert EPOCH.year == 1970
        assert EPOCH.month == 1
        assert EPOCH.day == 1
        assert EPOCH.hour == 0
        assert EPOCH.minute == 0
        assert EPOCH.second == 0
        assert EPOCH.microsecond == 0


# --- _plural ---


class TestPlural:
    def test_singular(self):
        assert _plural(1, "year") == "1 year"

    def test_plural(self):
        assert _plural(2, "year") == "2 years"

    def test_zero_is_plural(self):
        assert _plural(0, "day") == "0 days"

    def test_large_number(self):
        assert _plural(100, "minute") == "100 minutes"


# --- _join_time_parts ---


class TestJoinTimeParts:
    def test_single_part(self):
        assert _join_time_parts(["1 year"]) == "1 year"

    def test_two_parts(self):
        assert _join_time_parts(["1 year", "2 months"]) == "1 year and 2 months"

    def test_three_parts(self):
        result = _join_time_parts(["1 year", "2 months", "3 days"])
        assert result == "1 year, 2 months and 3 days"

    def test_four_parts(self):
        result = _join_time_parts(["1 year", "2 months", "3 days", "4 hours"])
        assert result == "1 year, 2 months, 3 days and 4 hours"


# --- timedelta_to_readable_elapsed_time: years ---


class TestTimedeltaToReadableYears:
    def test_exactly_one_year(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=365))
        assert result == "1 year ago"

    def test_two_years(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=730))
        assert result == "2 years ago"

    def test_year_and_months(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=365 + 60))
        assert result == "1 year and 2 months ago"

    def test_year_and_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=365 + 5))
        assert result == "1 year and 5 days ago"

    def test_year_months_and_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=400))
        # 400 days = 1 year (365) + 35 remaining = 1 month (30) + 5 days
        assert result == "1 year, 1 month and 5 days ago"

    def test_multiple_years_months_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=365 * 3 + 75))
        # 75 remaining = 2 months (60) + 15 days
        assert result == "3 years, 2 months and 15 days ago"


# --- timedelta_to_readable_elapsed_time: months ---


class TestTimedeltaToReadableMonths:
    def test_exactly_one_month(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=30))
        assert result == "1 month ago"

    def test_two_months(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=60))
        assert result == "2 months ago"

    def test_month_and_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=45))
        assert result == "1 month and 15 days ago"

    def test_eleven_months(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=330))
        assert result == "11 months ago"

    def test_upper_boundary(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=364))
        # 364 = 12 months (360) + 4 days
        assert result == "12 months and 4 days ago"


# --- timedelta_to_readable_elapsed_time: days ---


class TestTimedeltaToReadableDays:
    def test_one_day(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=1))
        assert result == "1 day ago"

    def test_multiple_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=15))
        assert result == "15 days ago"

    def test_twenty_nine_days(self):
        result = timedelta_to_readable_elapsed_time(timedelta(days=29))
        assert result == "29 days ago"

    def test_day_with_hours(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(days=2, hours=5)
        )
        assert result == "2 days and 5 hours ago"

    def test_day_without_extra_hours(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(days=3, minutes=30)
        )
        assert result == "3 days ago"


# --- timedelta_to_readable_elapsed_time: hours ---


class TestTimedeltaToReadableHours:
    def test_one_hour(self):
        result = timedelta_to_readable_elapsed_time(timedelta(hours=1))
        assert result == "1 hour ago"

    def test_multiple_hours(self):
        result = timedelta_to_readable_elapsed_time(timedelta(hours=5))
        assert result == "5 hours ago"

    def test_twenty_three_hours(self):
        result = timedelta_to_readable_elapsed_time(timedelta(hours=23))
        assert result == "23 hours ago"

    def test_hour_with_minutes(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(hours=1, minutes=30)
        )
        assert result == "1 hour and 30 minutes ago"

    def test_hours_without_extra_minutes(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(hours=2, seconds=45)
        )
        assert result == "2 hours ago"


# --- timedelta_to_readable_elapsed_time: minutes ---


class TestTimedeltaToReadableMinutes:
    def test_one_minute(self):
        result = timedelta_to_readable_elapsed_time(timedelta(minutes=1))
        assert result == "1 minute ago"

    def test_multiple_minutes(self):
        result = timedelta_to_readable_elapsed_time(timedelta(minutes=45))
        assert result == "45 minutes ago"

    def test_fifty_nine_minutes(self):
        result = timedelta_to_readable_elapsed_time(timedelta(minutes=59))
        assert result == "59 minutes ago"


# --- timedelta_to_readable_elapsed_time: zero/sub-minute ---


class TestTimedeltaToReadableZeroDelta:
    def test_zero_delta(self):
        result = timedelta_to_readable_elapsed_time(timedelta(0))
        assert result == "just now"

    def test_one_second(self):
        result = timedelta_to_readable_elapsed_time(timedelta(seconds=1))
        assert result == "just now"

    def test_fifty_nine_seconds(self):
        result = timedelta_to_readable_elapsed_time(timedelta(seconds=59))
        assert result == "just now"

    def test_custom_zero_label(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=10), zero_delta_label="moments ago"
        )
        assert result == "moments ago"

    def test_zero_label_has_no_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(0), suffix="ago"
        )
        assert result == "just now"


# --- timedelta_to_readable_elapsed_time: suffix ---


class TestTimedeltaToReadableSuffix:
    def test_default_suffix(self):
        result = timedelta_to_readable_elapsed_time(timedelta(hours=1))
        assert result == "1 hour ago"

    def test_custom_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(hours=1), suffix="elapsed"
        )
        assert result == "1 hour elapsed"

    def test_empty_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(hours=1), suffix=""
        )
        assert result == "1 hour"

    def test_none_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(hours=1), suffix=None
        )
        assert result == "1 hour"


# --- timedelta_to_readable_elapsed_time: zero_delta_threshold ---


class TestTimedeltaToReadableThreshold:
    def test_default_threshold_hides_seconds(self):
        result = timedelta_to_readable_elapsed_time(timedelta(seconds=30))
        assert result == "just now"

    def test_none_threshold_shows_seconds(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=30), zero_delta_threshold=None
        )
        assert result == "30 seconds ago"

    def test_none_threshold_shows_one_second(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=1), zero_delta_threshold=None
        )
        assert result == "1 second ago"

    def test_none_threshold_zero_delta_still_returns_label(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(0), zero_delta_threshold=None
        )
        assert result == "just now"

    def test_custom_threshold_hides_below(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=90),
            zero_delta_threshold=timedelta(minutes=5),
        )
        assert result == "just now"

    def test_custom_threshold_shows_above(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(minutes=10),
            zero_delta_threshold=timedelta(minutes=5),
        )
        assert result == "10 minutes ago"

    def test_exact_threshold_boundary_shows_value(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=60),
            zero_delta_threshold=timedelta(seconds=60),
        )
        assert result == "1 minute ago"

    def test_none_threshold_with_custom_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=45),
            suffix="elapsed",
            zero_delta_threshold=None,
        )
        assert result == "45 seconds elapsed"

    def test_none_threshold_with_no_suffix(self):
        result = timedelta_to_readable_elapsed_time(
            timedelta(seconds=10),
            suffix=None,
            zero_delta_threshold=None,
        )
        assert result == "10 seconds"

    def test_wrapper_passes_threshold_none(self):
        result = time_value_to_readable_elapsed_time(
            30, zero_delta_threshold=None
        )
        assert result == "30 seconds ago"

    def test_wrapper_passes_custom_threshold(self):
        result = time_value_to_readable_elapsed_time(
            90, zero_delta_threshold=timedelta(minutes=5)
        )
        assert result == "just now"


# --- timedelta_to_readable_elapsed_time: validation ---


class TestTimedeltaToReadableValidation:
    def test_negative_delta_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            timedelta_to_readable_elapsed_time(timedelta(seconds=-1))

    def test_large_negative_delta_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            timedelta_to_readable_elapsed_time(timedelta(days=-30))


# --- time_value_to_readable_elapsed_time ---


class TestTimeValueToReadable:
    def test_seconds_default(self):
        result = time_value_to_readable_elapsed_time(3600)
        assert result == "1 hour ago"

    def test_milliseconds(self):
        result = time_value_to_readable_elapsed_time(
            3_600_000, time_piece="milliseconds"
        )
        assert result == "1 hour ago"

    def test_minutes(self):
        result = time_value_to_readable_elapsed_time(
            90, time_piece="minutes"
        )
        assert result == "1 hour and 30 minutes ago"

    def test_hours(self):
        result = time_value_to_readable_elapsed_time(
            2, time_piece="hours"
        )
        assert result == "2 hours ago"

    def test_days(self):
        result = time_value_to_readable_elapsed_time(
            7, time_piece="days"
        )
        assert result == "7 days ago"

    def test_weeks(self):
        result = time_value_to_readable_elapsed_time(
            2, time_piece="weeks"
        )
        assert result == "14 days ago"

    def test_float_value(self):
        result = time_value_to_readable_elapsed_time(
            1.5, time_piece="hours"
        )
        assert result == "1 hour and 30 minutes ago"

    def test_zero_value(self):
        result = time_value_to_readable_elapsed_time(0)
        assert result == "just now"

    def test_passes_suffix(self):
        result = time_value_to_readable_elapsed_time(
            3600, suffix="elapsed"
        )
        assert result == "1 hour elapsed"

    def test_passes_zero_delta_label(self):
        result = time_value_to_readable_elapsed_time(
            0, zero_delta_label="now"
        )
        assert result == "now"


# --- time_value_to_readable_elapsed_time: validation ---


class TestTimeValueToReadableValidation:
    def test_invalid_time_piece_raises(self):
        with pytest.raises(ValueError, match="Invalid time_piece"):
            time_value_to_readable_elapsed_time(1, time_piece="months")

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            time_value_to_readable_elapsed_time(-1)

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="finite"):
            time_value_to_readable_elapsed_time(float("nan"))

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="finite"):
            time_value_to_readable_elapsed_time(float("inf"))

    def test_negative_inf_raises(self):
        with pytest.raises(ValueError, match="finite"):
            time_value_to_readable_elapsed_time(float("-inf"))
