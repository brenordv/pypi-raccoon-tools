import logging
from functools import wraps
from typing import Callable, Any, Union
from datetime import datetime, timedelta
from timeit import default_timer as timer
from typing_extensions import TypedDict


class TimerInfo(TypedDict):
    started_at: Union[datetime, None]
    stopped_at: Union[datetime, None]
    start_timer: Union[float, None]
    end_timer: Union[float, None]
    elapsed_time: Union[timedelta, None]


def benchmark(func: Callable) -> Callable:
    """
    A decorator that benchmarks the execution time of a function.

    The results will be logged using the logging module - INFO level.

    If you want to access the timer information, you can call the decorated function with the
    method get_benchmark_info().

    :param func: The function to benchmark
    :return: The decorated function
    """
    started_at: Union[datetime, None] = None
    stopped_at: Union[datetime, None] = None
    start_timer: Union[float, None] = None
    end_timer: Union[float, None] = None
    elapsed_time: Union[timedelta, None] = None

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        nonlocal started_at
        nonlocal stopped_at
        nonlocal start_timer
        nonlocal end_timer
        nonlocal elapsed_time

        started_at = datetime.utcnow()
        start_timer = timer()

        result: Any = func(*args, **kwargs)

        stopped_at = datetime.utcnow()
        end_timer = timer()

        elapsed_time = timedelta(seconds=end_timer - start_timer)
        logging.info(f"{func.__name__} took {elapsed_time} to execute.")

        return result

    def get_benchmark_info() -> TimerInfo:
        return {
            "started_at": started_at,
            "stopped_at": stopped_at,
            "start_timer": start_timer,
            "end_timer": end_timer,
            "elapsed_time": elapsed_time
        }

    wrapper.get_benchmark_info = get_benchmark_info

    return wrapper
