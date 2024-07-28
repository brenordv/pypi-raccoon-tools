"""
This module provides a set of functions to make requests to a server using the requests library.

The functions provided here are just wrappers around the requests library, but with the retry_request decorator applied.

Example:
    >>> import raccoontools.shared.requests_with_retry as requests
    >>> response = requests.get("https://www.google.com")  # This will retry the request 3 times before giving up.
    >>> print(response.status_code)
    200
"""

import requests

from raccoontools.decorators.retry import retry_request
from raccoontools.shared.serializer import serialize_to_dict

global_retries = 3
global_delay = 1
global_delay_is_exponential = True
global_skip_retry_on_404 = False
global_retry_only_on_status_codes = None
global_get_new_token_on_401 = None
global_get_new_token_on_403 = None


def _get_decorator_config() -> dict:
    """
    Get the configuration for the retry_request decorator.
    This way we can use the same configuration for all requests, and change it if needed.

    :return: The configuration for the decorator.
    """
    return {
        "retries": global_retries,
        "delay": global_delay,
        "delay_is_exponential": global_delay_is_exponential,
        "skip_retry_on_404": global_skip_retry_on_404,
        "retry_only_on_status_codes": global_retry_only_on_status_codes,
        "get_new_token_on_401": global_get_new_token_on_401,
        "get_new_token_on_403": global_get_new_token_on_403
    }


@retry_request(**_get_decorator_config())
def get(url, params=None, **kwargs) -> requests.Response:
    """Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.get(url, params=params, **kwargs)


@retry_request(**_get_decorator_config())
def options(url, **kwargs) -> requests.Response:
    """Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.options(url, **kwargs)


@retry_request(**_get_decorator_config())
def head(url, **kwargs) -> requests.Response:
    """Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.head(url, **kwargs)


@retry_request(**_get_decorator_config())
def post(url, data=None, json=None, **kwargs) -> requests.Response:
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    payload = json if kwargs.get("send_json_as_is", False) else serialize_to_dict(json)

    return requests.post(url, data=data, json=payload, **kwargs)


@retry_request(**_get_decorator_config())
def put(url, data=None, **kwargs) -> requests.Response:
    """Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    if "json" in kwargs and not kwargs.get("send_json_as_is", False):
        kwargs["json"] = serialize_to_dict(kwargs["json"])

    return requests.put(url, data=data, **kwargs)


@retry_request(**_get_decorator_config())
def patch(url, data=None, **kwargs) -> requests.Response:
    """Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object (not necessarily a dict or List[dict]) to send in the body of the :class:`Request`.
    :param send_json_as_is: (optional) If true, will skip the serialization of the data to dictionary.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    if "json" in kwargs and not kwargs.get("send_json_as_is", False):
        kwargs["json"] = serialize_to_dict(kwargs["json"])

    return requests.patch(url, data=data, **kwargs)


@retry_request(**_get_decorator_config())
def delete(url, **kwargs) -> requests.Response:
    """Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.delete(url, **kwargs)
