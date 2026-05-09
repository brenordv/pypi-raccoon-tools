import pytest

from raccoontools.shared.http import (
    DEFAULT_FAKE_BROWSER_USER_AGENT,
    _get_header_user_agent,
    _get_header_value,
    get_headers,
)


class TestGetHeaderUserAgent:
    def test_no_agent_no_fake_returns_empty(self):
        assert _get_header_user_agent() == {}

    def test_custom_user_agent(self):
        result = _get_header_user_agent(user_agent="MyBot/1.0")
        assert result == {"User-Agent": "MyBot/1.0"}

    def test_fake_browser_user_agent(self):
        result = _get_header_user_agent(fake_browser_user_agent=True)
        assert result == {"User-Agent": DEFAULT_FAKE_BROWSER_USER_AGENT}

    def test_custom_agent_takes_precedence_over_fake(self):
        result = _get_header_user_agent(
            user_agent="Custom/1.0", fake_browser_user_agent=True
        )
        assert result == {"User-Agent": "Custom/1.0"}


class TestGetHeaderValue:
    def test_returns_header_when_value_set(self):
        assert _get_header_value("X-Custom", "val") == {"X-Custom": "val"}

    def test_returns_empty_when_no_value(self):
        assert _get_header_value("X-Custom", "") == {}
        assert _get_header_value("X-Custom", None) == {}


class TestGetHeaders:
    def test_basic_headers_with_token(self):
        headers = get_headers(token="abc123")
        assert headers["Authorization"] == "Bearer abc123"
        assert headers["Content-Type"] == "application/json"

    def test_no_authorization_when_token_is_none(self):
        """Bug 5 regression: None token must not produce an Authorization header."""
        headers = get_headers(token=None)
        assert "Authorization" not in headers

    def test_no_authorization_when_token_is_empty(self):
        """Bug 5 regression: empty string token must not produce an Authorization header."""
        headers = get_headers(token="")
        assert "Authorization" not in headers

    def test_custom_content_type(self):
        headers = get_headers(token="t", content_type="text/plain")
        assert headers["Content-Type"] == "text/plain"

    def test_extra_args_merged(self):
        headers = get_headers(
            token="t",
            extra_args={"X-Custom": "value"},
        )
        assert headers["X-Custom"] == "value"

    def test_fake_browser_agent(self):
        headers = get_headers(
            token="t", fake_browser_user_agent=True
        )
        assert headers["User-Agent"] == DEFAULT_FAKE_BROWSER_USER_AGENT

    def test_custom_user_agent(self):
        headers = get_headers(token="t", user_agent="Bot/1.0")
        assert headers["User-Agent"] == "Bot/1.0"
