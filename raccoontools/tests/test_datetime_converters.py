from datetime import datetime, timedelta, timezone

import pytest

from raccoontools.converters.datetime_converters import (
    EPOCH,
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
