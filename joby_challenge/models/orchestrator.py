import logging
from joby_challenge.models.network_data_collector import NetworkDataCollector
from joby_challenge.models.async_worker_pool import AsyncWorkerPool
from joby_challenge.models.ip_address_handler import IPAddressHandler
from joby_challenge.utils import ping_host

DEFAULT_MAX_CONCURRENT_WORKERS = 50

logger = logging.getLogger("Orchestrator")

class Orchestrator:
    """
    Main controller for ping application
    """
    def __init__(self, networks, skips=None, max_concurrent=DEFAULT_MAX_CONCURRENT_WORKERS):
        self.address_handler = IPAddressHandler(networks, skips)

        self.data_collector = NetworkDataCollector()
        
        # Create worker pool with a callback to our data collector
        self.worker_pool = AsyncWorkerPool(
            ping_host, 
            result_callback=self.data_collector.add_result,
            max_concurrent=max_concurrent
        )

    async def start(self):
        """Start pinging hosts and collect results."""
        logger.info(f"Starting ping scan")

        # Execute all ping operations
        await self.worker_pool.start(self.ip_addresses)

        self.data_collector.log_mismatches()

        return self.data_collector.get_all_results()
    
    @property
    def data(self):
        """Access all collected data."""
        return self.data_collector.get_all_results()
    
    @property
    def ip_addresses(self):
        return self.address_handler.ip_addresses