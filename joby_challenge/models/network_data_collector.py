import logging

logger = logging.getLogger("NetworkDataCollector")

# index of last octet when ip address is split by period
DEFAULT_OCTET=3

class NetworkDataCollector:
    """
    Handles data collection and storage.
    """
    def __init__(self, octet_position=DEFAULT_OCTET):
        self.data = {}
        self.octet_position=octet_position
        self.mismatches = []
        self.reachable_map = {
            True: "IS REACHABLE",
            False: "IS NOT REACHABLE"
        }

    def add_result(self, ip_address, reachable):
        """Add a single result."""
        octets = ip_address.split('.')
        target_octet = octets[self.octet_position]

        # Initialize the entry if it doesn't exist
        if target_octet not in self.data:
            self.data[target_octet] = {}
        
        # Store the result
        self.data[target_octet][ip_address] = reachable
        self.check_mismatches(self.data[target_octet])

    def get_all_results(self):
        """Get all results."""
        return self.data
    
    def check_mismatches(self, ip_address_map):
        if len(ip_address_map) < 2:
            # haven't tried both ranges yet, no need to check
            return
        
        results = ip_address_map.values()

        # check where ip address is pingable in one range, but not the other
        if True in results and False in results:
            self.mismatches.append(ip_address_map)
            
    def log_mismatches(self):
        """Log all mismatches in a single consolidated report."""
        if not self.mismatches:
            logger.info("No mismatches found between networks")
            return

        logger.info("**********MISMATCH ANALYSIS START***********")
        
        for result in self.mismatches:
            for ip_addr, reachable in result.items():
                reachable = self.reachable_map[reachable]
                logger.info(f"{ip_addr} {reachable}")
            logger.info("----------------------------------")
        logger.info("**********MISMATCH ANALYSIS END***********")