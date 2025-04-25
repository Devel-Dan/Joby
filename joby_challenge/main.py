import argparse
import asyncio
import logging
from joby_challenge.models.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("main")

def parse_args():
    """
    Argument Parser function for user to run network ping tool
    """
    parser = argparse.ArgumentParser(description="joby challenge, 2 network scanner that can check for mismatches")
    parser.add_argument(
        "--network_1",
        default="192.168.1.0/24",
        help="first ip address range, string written in CIDR (Classless Inter-Domain Routing) notation",
    )
    parser.add_argument(
        "--network_2",
        default="192.168.2.0/24",
        help="second ip address range, string written in CIDR (Classless Inter-Domain Routing) notation",
    )
    parser.add_argument(
        "--skips",
        nargs="*",
        help="last octet of an ip address to skip, space separated for multiple",
    )

    return parser.parse_args()

async def main():
    """ grabs user arguments and starts tool"""
    args = parse_args()
    networks = [args.network_1, args.network_2]

    if args.skips:
        args.skips = set(args.skips)

    scanner = Orchestrator(networks, args.skips)
    await scanner.start()

def run():
    """asyncio Entry point"""
    asyncio.run(main())

if __name__ == "__main__":
    run()