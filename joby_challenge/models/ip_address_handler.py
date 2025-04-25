import ipaddress
import logging

logger = logging.getLogger("IPAddressHandler")

class IPAddressHandler:
    def __init__(self, ip_addresses, skips=None):
        self.skips = skips
        self.ip_addresses = self.set_ip_addresses(ip_addresses)
        
    def set_ip_addresses(self, ip_addresses):
        addresses = []

        if not isinstance(ip_addresses, list):
            raise TypeError(f"Expected list for ip_addresses, got {type(ip_addresses).__name__}")
        
        for ip_address in ip_addresses:
            logger.debug(f"Parsing IP: {ip_address}")
            
            parsed_addresses = self.parse_ip_addresses(ip_address)
            addresses += parsed_addresses

            logger.debug(f"Added {len(parsed_addresses)} IPs from {ip_address}")

        return addresses

    def parse_ip_addresses(self, ip_address):
        logger.debug(f"Parsing target: {ip_address}")
        addresses = []
        try:
            # Try to parse as a network first
            try:
                network = ipaddress.ip_network(ip_address, strict=False)
                # Skip the network address (.0) and broadcast address (.255)
                addresses = [str(ip) for ip in network.hosts()]

                logger.debug(
                    f"Successfully parsed as network with {len(addresses)} addresses"
                )
                return addresses
            except ValueError:
                # If not a network, treat as a single IP
                ipaddress.ip_address(ip_address)  # Validate it's a valid IP
                logger.debug(f"Successfully parsed as single IP address")

                addresses = [ip_address]
            
        except ValueError as e:
            logger.error(f"Failed to parse IP {ip_address}: {str(e)}")
        finally:
            if self.skips:
                logger.debug(
                    f"filtering out any addresses with last octects in {str(self.skips)}"
                )
                addresses = [ip for ip in addresses if self.get_last_octet(ip) not in self.skips]

            return addresses

    def get_last_octet(self, ip_address):
        return ip_address.split('.')[-1]