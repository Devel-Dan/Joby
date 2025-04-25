import pytest
from unittest.mock import MagicMock
from joby_challenge.models.orchestrator import Orchestrator, DEFAULT_MAX_CONCURRENT_WORKERS
from tests.constants import (
    TEST_NETWORK_CIDR,
    TEST_NETWORK_CIDR_2,
    TEST_SKIP_VALUES,
    TEST_MAX_CONCURRENT,
)

ORCHESTRATOR_INIT_TEST_CASES = [
    (
        [TEST_NETWORK_CIDR, TEST_NETWORK_CIDR_2],
        None,
        DEFAULT_MAX_CONCURRENT_WORKERS,
    ),
    (
        [TEST_NETWORK_CIDR],
        TEST_SKIP_VALUES,
        TEST_MAX_CONCURRENT,
    ),
]
ORCHESTRATOR_START_RESULT = {
    "1": {"192.168.1.1": False, "192.168.2.1": False},
    "2": {"192.168.1.2": True, "192.168.2.2": True},
    "3": {"192.168.1.3": False, "192.168.2.3": False},
    "4": {"192.168.1.4": True, "192.168.2.4": True},
    "5": {"192.168.1.5": False, "192.168.2.5": False},
    "6": {"192.168.1.6": True, "192.168.2.6": True},
}


def ping_side_effect(host, timeout=None):
    last_octet = int(host.split(".")[-1])
    if last_octet % 2 == 0:
        return None
    else:
        raise Exception("ping failure")


class TestOrchestrator:

    @pytest.mark.parametrize(
        "networks,skips,max_concurrent",
        ORCHESTRATOR_INIT_TEST_CASES,
        ids=["defaults", "custom"],
    )
    def test_orchestrator_init(self, networks, skips, max_concurrent):
        """Test Orchestrator initialization with different parameters."""
        # Create orchestrator with test parameters
        orchestrator = Orchestrator(networks, skips, max_concurrent=max_concurrent)

        # Check that the address handler is correctly initialized
        assert orchestrator.address_handler.ip_addresses
        assert orchestrator.address_handler.skips == skips

        # Check that the data collector is correctly initialized
        assert orchestrator.data_collector.data == {}

        # Check that the worker pool is correctly initialized
        assert orchestrator.worker_pool.target_function.__name__ == "ping_host"
        assert orchestrator.worker_pool.concurrent_workers == max_concurrent

    @pytest.mark.parametrize(
        "mock_ping_with_side_effects", [ping_side_effect], indirect=True
    )
    @pytest.mark.asyncio
    async def test_start(
        self, orchestrator, mock_ping_with_side_effects, mock_async_sleep
    ):
        """Test the start method of Orchestrator with even/odd ping responses."""

        orchestrator.data_collector.log_mismatches = MagicMock(
            wraps=orchestrator.data_collector.log_mismatches
        )

        result = await orchestrator.start()

        # Check that data_collector.log_mismatches was called
        orchestrator.data_collector.log_mismatches.assert_called_once()

        # Check that the result matches our expected value
        assert result == ORCHESTRATOR_START_RESULT
