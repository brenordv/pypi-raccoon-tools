"""
This module provides a set of functions to make requests to a server using the requests library.

The functions provided here are just wrappers around the requests library, but with the retry_request decorator applied.

The ``global_*`` module settings configure every request made through these wrappers. They are read on each call, so
changing them after import takes effect on the next request. ``global_timeout`` is passed as the requests ``timeout``
unless the caller passes its own (``timeout=None`` disables it).

Example:
    >>> import raccoontools.shared.requests_with_retry as requests
    >>> response = requests.get("https://www.google.com")  # This will retry the request 3 times before giving up.
    >>> print(response.status_code)
    200
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

import requests

from raccoontools.decorators.retry import retry_request
from raccoontools.shared.serializer import serialize_to_dict

global_retries = 3
global_delay = 1
global_delay_is_exponential = True
global_skip_retry_on_404 = False
global_retry_only_on_status_codes: list[int] | None = None
global_get_new_token_on_401: Callable[[], str] | None = None
global_get_new_token_on_403: Callable[[], str] | None = None
global_timeout: float | tuple[float, float] | None = 30


def _get_decorator_config() -> dict[str, Any]:
    """
    Get the configuration for the retry_request decorator.
    This way we can use the same configuration for all requests, and change it if needed.

    :return: The configuration for the decorator.
    """
    status_codes = global_retry_only_on_status_codes
    return {
        "retries": global_retries,
        "delay": global_delay,
        "delay_is_exponential": global_delay_is_exponential,
        "skip_retry_on_404": global_skip_retry_on_404,
        "retry_only_on_status_codes": None if status_codes is None else list(status_codes),
        "get_new_token_on_401": global_get_new_token_on_401,
        "get_new_token_on_403": global_get_new_token_on_403,
    }


def _with_retry(func: Callable[..., requests.Response]) -> Callable[..., requests.Response]:
    """
    Wrap a request function with ``retry_request``, configured from the current module settings.

    The decorated function is rebuilt only when the settings differ from the ones it was built with, so the retry
    logger is configured once per settings change rather than on every request.

    :param func: The undecorated request function.
    :return: The wrapped function.
    """
    decorated: Callable[..., requests.Response] | None = None
    decorated_config: dict[str, Any] | None = None

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> requests.Response:
        nonlocal decorated, decorated_config
        config = _get_decorator_config()
        if decorated is None or config != decorated_config:
            decorated = retry_request(**config)(func)
            decorated_config = config

        kwargs.setdefault("timeout", global_timeout)
        return decorated(*args, **kwargs)

    return wrapper


@_with_retry
def get(url: str | bytes, params: Any = None, **kwargs: Any) -> requests.Response:
    """Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.get(url, params=params, **kwargs)


@_with_retry
def options(url: str | bytes, **kwargs: Any) -> requests.Response:
    """Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.options(url, **kwargs)


@_with_retry
def head(url: str | bytes, **kwargs: Any) -> requests.Response:
    """Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.head(url, **kwargs)


@_with_retry
def post(url: str | bytes, data: Any = None, json: Any = None, **kwargs: Any) -> requests.Response:
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the
        body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    send_as_is = kwargs.pop("send_json_as_is", False)
    payload = json if send_as_is else serialize_to_dict(json)

    return requests.post(url, data=data, json=payload, **kwargs)


@_with_retry
def put(url: str | bytes, data: Any = None, **kwargs: Any) -> requests.Response:
    """Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the
        body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    send_as_is = kwargs.pop("send_json_as_is", False)
    if "json" in kwargs and not send_as_is:
        kwargs["json"] = serialize_to_dict(kwargs["json"])

    return requests.put(url, data=data, **kwargs)


@_with_retry
def patch(url: str | bytes, data: Any = None, **kwargs: Any) -> requests.Response:
    """Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the
        body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    send_as_is = kwargs.pop("send_json_as_is", False)
    if "json" in kwargs and not send_as_is:
        kwargs["json"] = serialize_to_dict(kwargs["json"])

    return requests.patch(url, data=data, **kwargs)


@_with_retry
def delete(url: str | bytes, **kwargs: Any) -> requests.Response:
    """Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.delete(url, **kwargs)
