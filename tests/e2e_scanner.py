import time
import logging
from src.scanner import SteamMarketScanner

# Configure logging for E2E
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2E-Tester")

def run_e2e_test():
    logger.info("Starting E2E Market Scan Test...")
    start_time = time.time()

    # Initialize scanner with a limited test config
    scanner = SteamMarketScanner()
    # We only scan one item for E2E to be polite to the API
    scanner.items_to_scan = scanner.items_to_scan[:1]

    logger.info(f"Scanning item: {scanner.items_to_scan[0]['market_hash_name']}")
    results = scanner.scan_market(delay=0.1)

    duration = time.time() - start_time
    logger.info(f"E2E Scan completed in {duration:.2f} seconds.")

    if results is not None:
        logger.info("E2E Test PASSED: Results received from API.")
        return True
    else:
        logger.error("E2E Test FAILED: No results received.")
        return False

if __name__ == "__main__":
    success = run_e2e_test()
    exit(0 if success else 1)
