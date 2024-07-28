import logging
from functools import wraps
from time import sleep
from typing import Callable, Any, List, Type, Optional, Union
import requests

from simple_log_factory.log_factory import log_factory

__logger_name = "RN.T:Retry"  # Racoon Ninja Tools: Retry Decorator


def retry(
        func: Optional[Callable] = None,
        *,
        retries: int = 3,
        delay: float = 1,
        delay_is_exponential: bool = False,
        only_exceptions_of_type: List[Type[BaseException]] = None,
        log_level: int = logging.ERROR
) -> Union[Callable, Any]:
    """
    A decorator that retries a function call a number of times before giving up.

    The results will be logged using the logger.module - DEBUG level.
    Except for the last attempt, where it will log an ERROR level message.


    :param func: The function to retry. This should not be set manually. Python set's it when using the decorator
    without parenthesis.
    :param retries: Maximum number of retries before giving up
    :param delay: Delay in seconds between each retry
    :param delay_is_exponential: If True, the delay between retries will increase exponentially
    :param only_exceptions_of_type: A list of exception types to catch and retry on. If None, all exceptions are caught.
    :param log_level: The log level that will be used by the decorator. (Default: ERROR)
    :return: The decorated function
    """
    logger: logging = log_factory(__logger_name, log_level=log_level, unique_handler_types=True)

    if retries < 1:
        raise ValueError("The number of retries must be greater than 0.")

    if delay < 0:
        raise ValueError("The delay between retries must be greater than or equal to 0.")

    def decorator(inner_func: Callable) -> Callable:
        @wraps(inner_func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay

            for i in range(1, retries + 1):
                try:
                    logger.debug(f"Attempt {i} of {retries} for {inner_func.__name__}.")
                    return inner_func(*args, **kwargs)
                except Exception as e:
                    if (only_exceptions_of_type and
                            not any(isinstance(e, exception_type) for exception_type in only_exceptions_of_type)):
                        logger.debug(f"Not allowed to retry on exception type {type(e)}.")
                        raise e

                    if i >= retries:
                        logger.error(f"Failed execution of {inner_func.__name__} after {retries} attempts.")
                        break

                    logger.debug(f"Retrying {inner_func.__name__} in {current_delay} seconds. Last error: {repr(e)}")

                    sleep(current_delay)

                    if delay_is_exponential:
                        current_delay *= 2

        return wrapper

    return decorator if func is None else decorator(func)


def retry_request(
        func: Optional[Callable] = None,
        *,
        retries: int = 3,
        delay: float = 1,
        delay_is_exponential: bool = False,
        skip_retry_on_404: bool = False,
        retry_only_on_status_codes: List[int] = None,
        get_new_token_on_401: Optional[Callable[[], str]] = None,
        get_new_token_on_403: Optional[Callable[[], str]] = None,
        log_level: int = logging.ERROR
) -> Union[Callable, Any]:
    """
    A decorator that retries a http request a number of times before giving up.

    The results will be logged using the logger.module - DEBUG level.
    Except for the last attempt, where it will log an ERROR level message.

    If all retries failed, the response from the last attempt will be returned to the caller.

    :param log_level:
    :param func: The function to retry. This should not be set manually. Python sets it when using the decorator
    without parentheses.
    :param retries: Maximum number of retries before giving up
    :param delay: Delay in seconds between each retry
    :param delay_is_exponential: If True, the delay between retries will increase exponentially
    :param skip_retry_on_404: If True, the decorator will not retry on 404 responses
    :param retry_only_on_status_codes: A list of HTTP status codes to retry on. If None, no retries will be made.
    :param get_new_token_on_401: An optional callable to execute and get a new token when a 401 response is received.
    :param get_new_token_on_403: An optional callable to execute and get a new token when a 403 response is received.
    :param log_level: The log level that will be used by the decorator. (Default: ERROR)
    :return: The decorated function
    """
    logger: logging = log_factory(__logger_name, log_level=log_level, unique_handler_types=True)

    if retries < 1:
        raise ValueError("The number of retries must be greater than 0.")

    if delay < 0:
        raise ValueError("The delay between retries must be greater than or equal to 0.")

    if retry_only_on_status_codes is None:
        retry_only_on_status_codes = []

    is_restricting_retry_status_code = len(retry_only_on_status_codes) > 0

    def _can_retry(status_code: int) -> bool:
        return (not is_restricting_retry_status_code or status_code in retry_only_on_status_codes) \
            and status_code >= 400

    def _can_update_token(**kwargs) -> bool:
        return "headers" in kwargs \
            and "Authorization" in kwargs["headers"] \
            and kwargs["headers"]["Authorization"].startswith("Bearer ")

    def decorator(inner_func: Callable) -> Callable:
        @wraps(inner_func)
        def wrapper(*args, **kwargs) -> requests.Response:
            current_delay = delay
            new_token = None
            for i in range(1, retries + 1):
                if new_token and _can_update_token(**kwargs):
                    kwargs["headers"]["Authorization"] = f"Bearer {new_token}"
                    new_token = None

                response = inner_func(*args, **kwargs)
                status_code = response.status_code

                if not _can_retry(status_code):
                    # We either cannot retry or the request was successful
                    return response

                if status_code == 404 and skip_retry_on_404:
                    logger.debug(f"404 (Not Found) detected and set to skip. Will not retry.")
                    return response

                if status_code == 401 and get_new_token_on_401:
                    logger.debug(f"401 Unauthorized detected. Executing on_401 callable.")
                    new_token = get_new_token_on_401()

                if status_code == 403 and get_new_token_on_403:
                    logger.debug(f"403 Forbidden detected. Executing on_403 callable.")
                    new_token = get_new_token_on_403()

                if i >= retries:
                    logger.error(f"Failed execution of {inner_func.__name__} after {retries} attempts.")
                    return response

                logger.debug(f"Attempt {i} of {retries} for {inner_func.__name__}. "
                             f"Retrying in {current_delay} seconds. Status code: {status_code}")

                sleep(current_delay)

                if delay_is_exponential:
                    current_delay *= 2

        return wrapper

    return decorator if func is None else decorator(func)
