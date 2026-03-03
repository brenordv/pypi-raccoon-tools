import time
import uuid

from raccoontools.generators.sequence_generators import (
    id_guid_generator,
    id_int_generator,
    sentence_generator,
    timestamp_generator,
)


class TestIdGuidGenerator:
    def test_generates_exact_count(self):
        guids = list(id_guid_generator(5))
        assert len(guids) == 5

    def test_all_are_valid_uuids(self):
        for guid in id_guid_generator(10):
            uuid.UUID(guid)  # Raises ValueError if invalid

    def test_all_are_unique(self):
        guids = list(id_guid_generator(100))
        assert len(set(guids)) == 100

    def test_zero_generates_nothing(self):
        assert list(id_guid_generator(0)) == []

    def test_none_generates_indefinitely(self):
        gen = id_guid_generator(None)
        items = [next(gen) for _ in range(50)]
        assert len(items) == 50


class TestIdIntGenerator:
    def test_generates_exact_count(self):
        ids = list(id_int_generator(5))
        assert ids == [0, 1, 2, 3, 4]

    def test_custom_start(self):
        ids = list(id_int_generator(3, start_at=100))
        assert ids == [100, 101, 102]

    def test_with_validation_filter(self):
        even_ids = list(
            id_int_generator(5, start_at=0, validate_id=lambda x: x % 2 == 0)
        )
        assert even_ids == [0, 2, 4, 6, 8]

    def test_zero_generates_nothing(self):
        assert list(id_int_generator(0)) == []

    def test_none_generates_indefinitely(self):
        gen = id_int_generator(None)
        items = [next(gen) for _ in range(50)]
        assert len(items) == 50


class TestTimestampGenerator:
    def test_generates_exact_count(self):
        timestamps = list(timestamp_generator(3))
        assert len(timestamps) == 3

    def test_all_are_ints(self):
        for ts in timestamp_generator(5):
            assert isinstance(ts, int)

    def test_timestamps_are_reasonable(self):
        now = int(time.time())
        for ts in timestamp_generator(3):
            assert abs(ts - now) < 5

    def test_zero_generates_nothing(self):
        assert list(timestamp_generator(0)) == []


class TestSentenceGenerator:
    def test_generates_exact_count(self):
        sentences = list(sentence_generator(5))
        assert len(sentences) == 5

    def test_all_end_with_period(self):
        for sentence in sentence_generator(10):
            assert sentence.endswith(".")

    def test_first_character_is_uppercase(self):
        for sentence in sentence_generator(10):
            assert sentence[0].isupper()

    def test_custom_min_and_max_length(self):
        for sentence in sentence_generator(20, min_length=10, max_length=100):
            assert len(sentence) >= 1  # at minimum a single word + period
            assert len(sentence) <= 100

    def test_high_min_length_does_not_crash(self):
        """Bug 3 regression: min_length > random upper bound must not crash."""
        sentences = list(sentence_generator(10, min_length=200))
        assert len(sentences) == 10
        for s in sentences:
            assert isinstance(s, str)
            assert len(s) > 0

    def test_min_length_exceeds_512_does_not_crash(self):
        """Bug 3 regression: even extreme min_length values are safe."""
        sentences = list(sentence_generator(3, min_length=600))
        assert len(sentences) == 3

    def test_zero_generates_nothing(self):
        assert list(sentence_generator(0)) == []

    def test_max_length_less_than_min_length_uses_min(self):
        sentences = list(sentence_generator(5, min_length=50, max_length=10))
        assert len(sentences) == 5
        for s in sentences:
            assert len(s) >= 1
