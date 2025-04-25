import logging
import aioping
import asyncio
import functools

logger = logging.getLogger("pings")

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_DELAY_SECONDS = 0.5
DEFAULT_PING_TIMEOUT_SECONDS = 1.0

def async_retry(attempts=DEFAULT_MAX_ATTEMPTS, delay=DEFAULT_DELAY_SECONDS):
    """
    Retry decorator for async functions.
    Args:
        attempts: Maximum number of attempts (including the first attempt)
        delay: Delay between retries in seconds
    Returns:
        Decorated function that will retry on failure
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                caught = ""

                try:
                    result = await func(*args, **kwargs)
                except Exception as e:
                    result = False
                    caught = str(e)
                finally:
                    if result == False:
                        logger.debug(f"Attempt {attempt} failed! {caught}")

                        if attempt == attempts:
                            raise Exception(f"max attempts({attempts}) reached")

                        back_off_seconds = delay * attempt
                        logger.debug(f"retrying in {back_off_seconds}s...")

                        await asyncio.sleep(back_off_seconds)
                    else:
                        return result

        return wrapper

    return decorator


@async_retry()
async def ping_host(host, timeout=DEFAULT_PING_TIMEOUT_SECONDS):
    """
    Check if a host is reachable via ICMP ping.

    Args:
        host: IP address to ping
        timeout: Timeout in seconds

    Returns:
        bool: True if host is reachable, False otherwise
    """
    logger.debug(f"Pinging {host} with aioping")

    try:
        await aioping.ping(host, timeout=timeout)
        logger.info(f"{host} is reachable")
        return True
    except Exception as e:
        # Log the specific failure
        logger.debug(f"{host} ping failed: {str(e)}")
        return False
    