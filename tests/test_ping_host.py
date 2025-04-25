import pytest
from unittest.mock import call

from joby_challenge.utils import ping_host

from tests.constants import TEST_SINGLE_IP

PING_HOST_TEST_PARAMS = [
    ([None], True, []),
    ([Exception("Connection timeout"), None], True, [call(0.5)]),
    (
        [
            Exception("Connection timeout"),
            Exception("Connection timeout"),
            None,
        ],
        True,
        [call(0.5), call(1.0)],
    ),
    (
        [
            Exception("Connection timeout"),
            Exception("Connection timeout"),
            Exception("Connection timeout"),
        ],
        "raises",
        [call(0.5), call(1.0)],
    ),
    (
        [TimeoutError("Ping timeout"), ConnectionError("Network error"), None],
        True,
        [call(0.5), call(1.0)],
    ),
]

class TestPingHost:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "mock_ping_with_side_effects,expected_result,expected_sleep_calls",
        PING_HOST_TEST_PARAMS,
        ids=[
            "success_first_attempt",
            "success_after_one_retry",
            "success_after_two_retries",
            "all_attempts_fail",
            "mixed_exception_types",
        ],
        indirect=["mock_ping_with_side_effects"],
    )
    async def test_ping_host_scenarios(
        self,
        mock_ping_with_side_effects,
        mock_async_sleep,
        expected_result,
        expected_sleep_calls,
    ):
        """Test ping_host with various retry scenarios."""
        ip_address = TEST_SINGLE_IP

        # Handle the case where we expect an exception
        if expected_result == "raises":
            with pytest.raises(Exception, match="max attempts"):
                await ping_host(ip_address)
        else:
            result = await ping_host(ip_address)
            assert result is expected_result

        # Check sleep calls
        assert mock_async_sleep.call_count == len(expected_sleep_calls)
        if expected_sleep_calls:
            mock_async_sleep.assert_has_calls(expected_sleep_calls)

        # Verify ping was called with right parameters
        for call_args in mock_ping_with_side_effects.call_args_list:
            # check IP address
            assert call_args.args[0] == ip_address
            # check timeout
            assert call_args.kwargs.get("timeout") == 1.0
