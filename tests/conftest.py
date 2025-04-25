import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from joby_challenge.models.network_data_collector import NetworkDataCollector
from joby_challenge.models.ip_address_handler import IPAddressHandler
from joby_challenge.models.async_worker_pool import AsyncWorkerPool
from joby_challenge.models.orchestrator import Orchestrator

from tests.constants import TEST_NETWORK_CIDR, TEST_NETWORK_CIDR_2, TEST_SKIP_VALUES


@pytest.fixture
def mock_async_sleep():
    """Fixture to mock asyncio.sleep."""
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_ping_with_side_effects(request, mock_async_sleep):
    """Configurable ping mock with side effects passed as a parameter."""
    with patch('aioping.ping', new_callable=AsyncMock) as mock:
        # Set the side_effect based on the parameter from the test
        mock.side_effect = request.param
        yield mock

@pytest.fixture
def collector():
    """Fixture that returns a basic NetworkDataCollector instance."""
    return NetworkDataCollector()

@pytest.fixture
def sample_networks():
    return [TEST_NETWORK_CIDR, TEST_NETWORK_CIDR_2]

@pytest.fixture
def handler_with_skips(sample_networks):
    """Fixture that returns a handler with skips."""
    return IPAddressHandler(sample_networks, skips=TEST_SKIP_VALUES)

@pytest.fixture
def address_handler():
    """Fixture that returns an IPAddressHandler with no networks or skips."""
    return IPAddressHandler([])

@pytest.fixture
def result_callback():
    """Fixture that returns a mock result callback."""
    return MagicMock()

@pytest.fixture
def target_function():
    """Fixture that returns a mock target function."""
    return AsyncMock(return_value=True)

@pytest.fixture
def pool(target_function, result_callback):
    """Fixture that returns a basic AsyncWorkerPool instance."""
    return AsyncWorkerPool(target_function, result_callback)


@pytest.fixture
def orchestrator(sample_networks):
    """Fixture that returns a basic Orchestrator instance."""
    return Orchestrator(sample_networks)
