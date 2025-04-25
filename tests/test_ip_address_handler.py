# test_ip_address_handler.py
import pytest
from joby_challenge.models.ip_address_handler import IPAddressHandler
from tests.constants import TEST_NETWORK_CIDR, TEST_SKIP_VALUES, TEST_SINGLE_IP, TEST_INVALID_IP

CIDR_IP_ADDRESSES = [
    "192.168.1.1",
    "192.168.1.2",
    "192.168.1.3",
    "192.168.1.4",
    "192.168.1.5",
    "192.168.1.6",
]
CIDR_2_IP_ADDRESSES = [
    "192.168.2.1",
    "192.168.2.2",
    "192.168.2.3",
    "192.168.2.4",
    "192.168.2.5",
    "192.168.2.6",
]
SKIPPED_ADDRESSES = ["192.168.1.1", "192.168.1.3", "192.168.1.5"]
NOT_SKIPPED_ADDRESSES = ["192.168.1.2", "192.168.1.4", "192.168.1.6"]
LAST_OCTEST_TEST_CASES = [
    ("192.168.1.1", "1"),
    ("10.0.0.255", "255"),
    ("172.16.32.44", "44"),
]


class TestIPAddressHandler:

    def test_ip_address_handler_init(self, sample_networks):
        """ tests the initializtion"""
        # Test initialization with IP addresses and no skips
        handler = IPAddressHandler(sample_networks)
        
        # check that ip addresses match what we expect
        assert sorted(handler.ip_addresses) == sorted(
            CIDR_IP_ADDRESSES + CIDR_2_IP_ADDRESSES
        )

        assert handler.skips is None
        assert len(handler.ip_addresses) == len(CIDR_2_IP_ADDRESSES + CIDR_IP_ADDRESSES)

    @pytest.mark.parametrize(
        "ip_string,expected_count,expected_ips",
        [
            (TEST_NETWORK_CIDR, 6, CIDR_IP_ADDRESSES),
            (TEST_SINGLE_IP, 1, [TEST_SINGLE_IP]),
            (TEST_INVALID_IP, 0, []),
        ],
        ids=["Good network", "Good Ip Address", "Bad Ip Address"],
    )
    def test_parse_ip_addresses(
        self, address_handler, ip_string, expected_count, expected_ips
    ):
        """Test that parse_ip_addresses correctly handles different address formats."""
        addresses = address_handler.parse_ip_addresses(ip_string)
        assert len(addresses) == expected_count
        assert sorted(addresses) == sorted(expected_ips)

    @pytest.mark.parametrize(
        "invalid_input",
        [
            TEST_SINGLE_IP,
            123,
            {"ip": TEST_SINGLE_IP},
            None,
        ],
        ids=["string", "Integer", "Dictionary", "None"],
    )
    def test_set_ip_addresses_with_invalid_input(self, address_handler, invalid_input):
        """Test that set_ip_addresses raises TypeError for non-list inputs."""
        with pytest.raises(TypeError):
            address_handler.set_ip_addresses(invalid_input)

    def test_set_ip_addresses_with_valid_list(self, address_handler):
        """Test that set_ip_addresses works with a valid list of IP addresses."""
        addresses = address_handler.set_ip_addresses(
            [TEST_NETWORK_CIDR, TEST_SINGLE_IP]
        )
        # Both a network and a single IP should be processed correctly
        assert "192.168.1.1" in addresses
        assert "192.168.1.2" in addresses
        assert TEST_SINGLE_IP in addresses

    def test_skips(self, handler_with_skips):
        assert handler_with_skips.skips == TEST_SKIP_VALUES

        for address in SKIPPED_ADDRESSES:
            assert address not in handler_with_skips.ip_addresses

        for address in NOT_SKIPPED_ADDRESSES:
            assert address in handler_with_skips.ip_addresses

    @pytest.mark.parametrize("test_address,expected_octet", LAST_OCTEST_TEST_CASES)
    def test_get_last_octet(self, address_handler, test_address, expected_octet):
        """Test that get_last_octet returns the correct value."""

        assert address_handler.get_last_octet(test_address) == expected_octet
