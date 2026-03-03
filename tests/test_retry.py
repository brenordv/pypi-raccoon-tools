import logging
from unittest.mock import MagicMock, patch

import pytest
import requests

from raccoontools.decorators.retry import retry, retry_request


# ---------------------------------------------------------------------------
# retry decorator
# ---------------------------------------------------------------------------
class TestRetryDecorator:
    """Tests for the @retry decorator."""

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_succeeds_on_first_attempt(self, mock_sleep):
        @retry
        def succeed():
            return "ok"

        assert succeed() == "ok"
        mock_sleep.assert_not_called()

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_retries_and_succeeds(self, mock_sleep):
        call_count = 0

        @retry(retries=3, delay=0)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        assert flaky() == "ok"
        assert call_count == 3

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_raises_after_all_retries_exhausted(self, mock_sleep):
        """Bug 1 regression: must re-raise, not return None."""

        @retry(retries=2, delay=0)
        def always_fail():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            always_fail()

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_does_not_retry_on_unmatched_exception_type(self, mock_sleep):
        @retry(retries=3, delay=0, only_exceptions_of_type=[ValueError])
        def wrong_error():
            raise TypeError("wrong type")

        with pytest.raises(TypeError, match="wrong type"):
            wrong_error()
        mock_sleep.assert_not_called()

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_retries_only_on_matched_exception_type(self, mock_sleep):
        call_count = 0

        @retry(retries=3, delay=0, only_exceptions_of_type=[ValueError])
        def selective():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("retry me")
            return "done"

        assert selective() == "done"
        assert call_count == 3

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_exponential_delay(self, mock_sleep):
        @retry(retries=3, delay=1, delay_is_exponential=True)
        def always_fail():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            always_fail()

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1, 2]

    def test_invalid_retries_raises_value_error(self):
        with pytest.raises(ValueError, match="greater than 0"):
            @retry(retries=0)
            def noop():
                pass

    def test_invalid_delay_raises_value_error(self):
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            @retry(delay=-1)
            def noop():
                pass

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_preserves_function_metadata(self, mock_sleep):
        @retry
        def documented():
            """My docstring."""
            return 1

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "My docstring."

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_decorator_with_parentheses_no_args(self, mock_sleep):
        @retry()
        def simple():
            return 42

        assert simple() == 42


# ---------------------------------------------------------------------------
# retry_request decorator
# ---------------------------------------------------------------------------
class TestRetryRequestDecorator:
    """Tests for the @retry_request decorator."""

    def _mock_response(self, status_code=200):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = status_code
        return resp

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_returns_immediately_on_success(self, mock_sleep):
        @retry_request(retries=3, delay=0)
        def do_request():
            return self._mock_response(200)

        resp = do_request()
        assert resp.status_code == 200
        mock_sleep.assert_not_called()

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_retries_on_server_error(self, mock_sleep):
        call_count = 0

        @retry_request(retries=3, delay=0)
        def flaky_request():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return self._mock_response(500)
            return self._mock_response(200)

        resp = flaky_request()
        assert resp.status_code == 200
        assert call_count == 3

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_returns_last_response_after_exhausted_retries(self, mock_sleep):
        @retry_request(retries=2, delay=0)
        def always_500():
            return self._mock_response(500)

        resp = always_500()
        assert resp.status_code == 500

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_skip_retry_on_404(self, mock_sleep):
        call_count = 0

        @retry_request(retries=3, delay=0, skip_retry_on_404=True)
        def not_found():
            nonlocal call_count
            call_count += 1
            return self._mock_response(404)

        resp = not_found()
        assert resp.status_code == 404
        assert call_count == 1

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_retry_only_on_specific_status_codes(self, mock_sleep):
        call_count = 0

        @retry_request(
            retries=3,
            delay=0,
            retry_only_on_status_codes=[503],
        )
        def server_error():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return self._mock_response(500)
            return self._mock_response(200)

        resp = server_error()
        # 500 is not in the retry list, so it returns immediately
        assert resp.status_code == 500
        assert call_count == 1

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_get_new_token_on_401(self, mock_sleep):
        token_func = MagicMock(return_value="new-token")
        call_count = 0

        @retry_request(
            retries=3,
            delay=0,
            get_new_token_on_401=token_func,
        )
        def auth_request(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return self._mock_response(401)
            return self._mock_response(200)

        resp = auth_request(
            headers={"Authorization": "Bearer old-token"}
        )
        assert resp.status_code == 200
        token_func.assert_called_once()

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_does_not_retry_on_client_success(self, mock_sleep):
        @retry_request(retries=3, delay=0)
        def ok_request():
            return self._mock_response(201)

        resp = ok_request()
        assert resp.status_code == 201
        mock_sleep.assert_not_called()

    def test_invalid_retries_raises_value_error(self):
        with pytest.raises(ValueError, match="greater than 0"):
            @retry_request(retries=0)
            def noop():
                pass

    def test_invalid_delay_raises_value_error(self):
        with pytest.raises(ValueError, match="greater than or equal to 0"):
            @retry_request(delay=-1)
            def noop():
                pass

    @patch("raccoontools.decorators.retry.sleep", return_value=None)
    def test_exponential_delay_for_request(self, mock_sleep):
        @retry_request(retries=3, delay=1, delay_is_exponential=True)
        def always_fail():
            return self._mock_response(500)

        always_fail()
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1, 2]
