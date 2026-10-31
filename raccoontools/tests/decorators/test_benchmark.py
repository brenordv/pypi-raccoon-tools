import time
from datetime import datetime, timedelta

from raccoontools.decorators.benchmark import benchmark


class TestBenchmark:
    def test_returns_function_result(self):
        @benchmark
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_get_benchmark_info_before_call_returns_nones(self):
        @benchmark
        def noop():
            pass

        info = noop.get_benchmark_info()
        assert info["started_at"] is None
        assert info["stopped_at"] is None
        assert info["start_timer"] is None
        assert info["end_timer"] is None
        assert info["elapsed_time"] is None

    def test_get_benchmark_info_after_call(self):
        @benchmark
        def noop():
            pass

        noop()
        info = noop.get_benchmark_info()

        assert isinstance(info["started_at"], datetime)
        assert isinstance(info["stopped_at"], datetime)
        assert isinstance(info["start_timer"], float)
        assert isinstance(info["end_timer"], float)
        assert isinstance(info["elapsed_time"], timedelta)

    def test_timestamps_are_timezone_aware(self):
        """UTC compat: started_at and stopped_at must have tzinfo set."""

        @benchmark
        def noop():
            pass

        noop()
        info = noop.get_benchmark_info()

        assert info["started_at"].tzinfo is not None
        assert info["stopped_at"].tzinfo is not None

    def test_stopped_at_is_after_started_at(self):
        @benchmark
        def noop():
            pass

        noop()
        info = noop.get_benchmark_info()
        assert info["stopped_at"] >= info["started_at"]

    def test_elapsed_time_reflects_actual_duration(self):
        @benchmark
        def slow():
            time.sleep(0.05)

        slow()
        info = slow.get_benchmark_info()
        assert info["elapsed_time"].total_seconds() >= 0.04

    def test_preserves_function_metadata(self):
        @benchmark
        def my_func():
            """Docstring."""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "Docstring."

    def test_passes_args_and_kwargs(self):
        @benchmark
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        assert greet("World") == "Hello, World!"
        assert greet("World", greeting="Hi") == "Hi, World!"

    def test_successive_calls_update_info(self):
        @benchmark
        def noop():
            pass

        noop()
        first_started = noop.get_benchmark_info()["started_at"]

        time.sleep(0.01)
        noop()
        second_started = noop.get_benchmark_info()["started_at"]

        assert second_started > first_started
