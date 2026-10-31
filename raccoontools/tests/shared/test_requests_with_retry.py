import logging
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
import requests as real_requests

import raccoontools.shared.requests_with_retry as rwr


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock(spec=real_requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


class TestGet:
    @patch("raccoontools.shared.requests_with_retry.requests.get")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_get_success(self, mock_sleep, mock_get):
        mock_get.return_value = _mock_response(200)
        resp = rwr.get("https://example.com")
        assert resp.status_code == 200
        mock_get.assert_called_once()


class TestPost:
    @patch("raccoontools.shared.requests_with_retry.requests.post")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_post_success(self, mock_sleep, mock_post):
        mock_post.return_value = _mock_response(201)
        resp = rwr.post("https://example.com", json={"key": "val"})
        assert resp.status_code == 201

    @patch("raccoontools.shared.requests_with_retry.requests.post")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_post_send_json_as_is_does_not_leak(self, mock_sleep, mock_post):
        """Bug 2 regression: send_json_as_is must not be passed to requests."""
        mock_post.return_value = _mock_response(200)
        rwr.post(
            "https://example.com",
            json={"raw": True},
            send_json_as_is=True,
        )
        # Verify send_json_as_is is NOT in the kwargs passed to requests.post
        _, kwargs = mock_post.call_args
        assert "send_json_as_is" not in kwargs


class TestPut:
    @patch("raccoontools.shared.requests_with_retry.requests.put")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_put_success(self, mock_sleep, mock_put):
        mock_put.return_value = _mock_response(200)
        resp = rwr.put("https://example.com", json={"key": "val"})
        assert resp.status_code == 200

    @patch("raccoontools.shared.requests_with_retry.requests.put")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_put_send_json_as_is_does_not_leak(self, mock_sleep, mock_put):
        """Bug 2 regression."""
        mock_put.return_value = _mock_response(200)
        rwr.put(
            "https://example.com",
            json={"raw": True},
            send_json_as_is=True,
        )
        _, kwargs = mock_put.call_args
        assert "send_json_as_is" not in kwargs


class TestPatch:
    @patch("raccoontools.shared.requests_with_retry.requests.patch")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_patch_success(self, mock_sleep, mock_patch):
        mock_patch.return_value = _mock_response(200)
        resp = rwr.patch("https://example.com", json={"key": "val"})
        assert resp.status_code == 200

    @patch("raccoontools.shared.requests_with_retry.requests.patch")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_patch_send_json_as_is_does_not_leak(self, mock_sleep, mock_patch):
        """Bug 2 regression."""
        mock_patch.return_value = _mock_response(200)
        rwr.patch(
            "https://example.com",
            json={"raw": True},
            send_json_as_is=True,
        )
        _, kwargs = mock_patch.call_args
        assert "send_json_as_is" not in kwargs


class TestDelete:
    @patch("raccoontools.shared.requests_with_retry.requests.delete")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_delete_success(self, mock_sleep, mock_delete):
        mock_delete.return_value = _mock_response(204)
        resp = rwr.delete("https://example.com/1")
        assert resp.status_code == 204


class TestOptions:
    @patch("raccoontools.shared.requests_with_retry.requests.options")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_options_success(self, mock_sleep, mock_options):
        mock_options.return_value = _mock_response(200)
        resp = rwr.options("https://example.com")
        assert resp.status_code == 200


class TestHead:
    @patch("raccoontools.shared.requests_with_retry.requests.head")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_head_success(self, mock_sleep, mock_head):
        mock_head.return_value = _mock_response(200)
        resp = rwr.head("https://example.com")
        assert resp.status_code == 200


@pytest.fixture
def retry_logger() -> Iterator[logging.Logger]:
    """The logger shared by the retry decorators, with its level restored after the test."""
    logger = logging.getLogger("RN.T:Retry")
    original_level = logger.level
    yield logger
    logger.setLevel(original_level)


class TestModuleSettings:
    @patch("raccoontools.shared.requests_with_retry.requests.get")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_changed_global_retries_apply_to_the_next_call(
        self, mock_sleep: MagicMock, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_get.return_value = _mock_response(500)
        monkeypatch.setattr(rwr, "global_retries", 2)

        rwr.get("https://example.com")

        assert mock_get.call_count == 2

    @patch("raccoontools.shared.requests_with_retry.requests.get")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_status_codes_changed_in_place_apply_to_the_next_call(
        self, mock_sleep: MagicMock, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_get.return_value = _mock_response(500)
        status_codes: list[int] = []
        monkeypatch.setattr(rwr, "global_retry_only_on_status_codes", status_codes)
        rwr.get("https://example.com")
        mock_get.reset_mock()

        status_codes.append(503)
        rwr.get("https://example.com")

        assert mock_get.call_count == 1

    @patch("raccoontools.shared.requests_with_retry.requests.get")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_repeated_calls_keep_the_retry_logger_level(
        self, mock_sleep: MagicMock, mock_get: MagicMock, retry_logger: logging.Logger
    ) -> None:
        mock_get.return_value = _mock_response(200)
        rwr.get("https://example.com")
        retry_logger.setLevel(logging.CRITICAL)

        rwr.get("https://example.com")

        assert retry_logger.level == logging.CRITICAL

    @patch("raccoontools.shared.requests_with_retry.requests.get")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_global_timeout_is_sent_when_caller_omits_timeout(
        self, mock_sleep: MagicMock, mock_get: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_get.return_value = _mock_response(200)
        monkeypatch.setattr(rwr, "global_timeout", 12)

        rwr.get("https://example.com")

        assert mock_get.call_args.kwargs["timeout"] == 12

    @patch("raccoontools.shared.requests_with_retry.requests.post")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_caller_timeout_wins_over_global_timeout(self, mock_sleep: MagicMock, mock_post: MagicMock) -> None:
        mock_post.return_value = _mock_response(200)

        rwr.post("https://example.com", json={"key": "val"}, timeout=None)

        assert mock_post.call_args.kwargs["timeout"] is None

    @patch("raccoontools.shared.requests_with_retry.requests.post")
    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_post_sends_lists_of_primitives(self, mock_sleep: MagicMock, mock_post: MagicMock) -> None:
        mock_post.return_value = _mock_response(200)

        rwr.post("https://example.com", json={"tags": ["a", "b"]})

        assert mock_post.call_args.kwargs["json"] == {"tags": ["a", "b"]}
