# test_network_data_collector.py
import pytest
import logging
from joby_challenge.models.network_data_collector import NetworkDataCollector, DEFAULT_OCTET
from tests.constants import TEST_SINGLE_IP

NO_MISMATCH_TEXT = "No mismatches found between networks"
TEST_REACHABLE_MAP = {True: "IS REACHABLE", False: "IS NOT REACHABLE"}
TEST_SINGLE_IP_2 = "192.168.2.1"
TEST_SINGLE_LAST_OCTET_2 = "192.168.1.2"
MISMATCH_TEST_CASES = [
    ({}, 0),
    ({TEST_SINGLE_IP: True}, 0),
    ({TEST_SINGLE_IP: True, TEST_SINGLE_IP_2: True}, 0),
    ({TEST_SINGLE_IP: True, TEST_SINGLE_IP_2: False}, 1),
]


class TestNetworkDataCollector:

    def test_network_data_collector_init(self):
        """ tests the initialization"""
        # Test initialization with default values
        collector = NetworkDataCollector()
        assert collector.data == {}
        assert collector.octet_position == DEFAULT_OCTET
        assert collector.mismatches == []
        assert collector.reachable_map == TEST_REACHABLE_MAP

        # Test initialization with custom octet position
        collector = NetworkDataCollector(octet_position=2)
        assert collector.octet_position == 2

    def test_add_result(self, collector, address_handler):
        """ tests the add_result function"""

        # Add a single result
        collector.add_result(TEST_SINGLE_IP, True)

        # Check data structure
        last_octet = address_handler.get_last_octet(TEST_SINGLE_IP)
        assert last_octet in collector.data
        assert TEST_SINGLE_IP in collector.data[last_octet]
        assert collector.data[last_octet][TEST_SINGLE_IP] is True

        # Add another result for the same octet but different network
        collector.add_result(TEST_SINGLE_IP_2, False)

        # Check data structure again
        assert len(collector.data[last_octet]) == 2
        assert collector.data[last_octet][TEST_SINGLE_IP_2] is False

        # Check that mismatches were detected
        assert len(collector.mismatches) == 1
        assert collector.mismatches[0] == collector.data[last_octet]

    def test_get_all_results(self, collector, address_handler):
        """ tests the get_all_results function"""
        # Add some results
        collector.add_result(TEST_SINGLE_IP, True)
        collector.add_result(TEST_SINGLE_LAST_OCTET_2, False)

        # Check get_all_results
        results = collector.get_all_results()
        last_octet_1 = address_handler.get_last_octet(TEST_SINGLE_IP)
        last_octet_2 = address_handler.get_last_octet(TEST_SINGLE_LAST_OCTET_2)

        assert results == collector.data
        assert last_octet_1 in results
        assert last_octet_2 in results
        assert results[last_octet_1][TEST_SINGLE_IP] is True
        assert results[last_octet_2][TEST_SINGLE_LAST_OCTET_2] is False

    @pytest.mark.parametrize(
        "ip_address_map,mismatches",
        MISMATCH_TEST_CASES,
        ids=[
            "no reults",
            "single result",
            "multiple results, no mismatch",
            "multiple results, mismatch",
        ],
    )
    def test_check_mismatches(self, collector, ip_address_map, mismatches):
        """tests the check mismatches function"""
        collector.check_mismatches(ip_address_map)
        assert len(collector.mismatches) == mismatches

    def test_log_mismatches(self, caplog, collector):
        """tests the log mismatches function"""
        caplog.set_level(logging.INFO)

        # Test with no mismatches
        collector.log_mismatches()
        assert NO_MISMATCH_TEXT in caplog.text

        # Clear log
        caplog.clear()

        # Test with mismatches
        collector.mismatches = [{TEST_SINGLE_IP: True, TEST_SINGLE_IP_2: False}]
        collector.log_mismatches()

        assert f"{TEST_SINGLE_IP} {TEST_REACHABLE_MAP[True]}" in caplog.text
        assert  f"{TEST_SINGLE_IP_2} {TEST_REACHABLE_MAP[False]}" in caplog.text
