import logging
import asyncio
import time
from src.scanner import SteamMarketScanner

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    The main trading engine that orchestrates scanning and trade execution.
    """

    def __init__(self, config_path="config/items.json"):
        self.scanner = SteamMarketScanner(config_path=config_path)
        logger.info("TradingEngine initialized.")

    async def run_cycle(self):
        """
        Executes a single trading cycle and measures latency.
        """
        start_time = time.time()
        logger.info("Starting trading cycle...")
        opportunities = await self.scanner.scan_market()

        latency = time.time() - start_time
        logger.info(f"Cycle latency: {latency:.4f} seconds.")

        if opportunities:
            logger.info(f"Identified {len(opportunities)} profitable opportunities.")
        else:
            logger.info("No profitable opportunities found in this cycle.")

        return opportunities, latency

    async def start(self, interval=3600):
        while True:
            await self.run_cycle()
            await asyncio.sleep(interval)

if __name__ == "__main__":
    engine = TradingEngine()
    asyncio.run(engine.run_cycle())
