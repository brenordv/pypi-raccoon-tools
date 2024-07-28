from typing import Dict

# Now, why would you want to do something like this?
DEFAULT_FAKE_BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"


def _get_header_user_agent(user_agent: str = None, fake_browser_user_agent: bool = False) -> Dict[str, str]:
    if not user_agent and not fake_browser_user_agent:
        return {}

    return {
        "User-Agent": user_agent if user_agent else DEFAULT_FAKE_BROWSER_USER_AGENT
    }


def _get_header_value(key: str, value: str) -> Dict[str, str]:
    if not value:
        return {}

    return {
        key: value
    }


def get_headers(
        token: str,
        content_type: str = "application/json",
        user_agent: str = None,
        fake_browser_user_agent: bool = False,
        extra_args: Dict[str, str] = None) -> Dict[str, str]:
    """
    Get the headers for an HTTP request.
    :param token: Authentication token.
    :param content_type: Content type of the request. (Default: application/json)
    :param user_agent: User agent of the request. (Optional)
    :param fake_browser_user_agent: Use a fake browser user agent. (Default: False)
    :param extra_args: Extra headers to add to the request. (Optional)
    :return: The headers for the request.
    """
    if extra_args is None:
        extra_args = {}

    headers = {
        **_get_header_user_agent(user_agent, fake_browser_user_agent),
        **_get_header_value("Authorization", f"Bearer {token}"),
        **_get_header_value("Content-Type", content_type),
        **extra_args
    }

    return headers
