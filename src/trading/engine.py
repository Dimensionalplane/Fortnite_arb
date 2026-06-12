import logging
import asyncio
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
        Executes a single trading cycle: Scan -> Analyze -> (Future) Execute.
        """
        logger.info("Starting trading cycle...")
        opportunities = await self.scanner.scan_market()

        if opportunities:
            logger.info(f"Identified {len(opportunities)} profitable opportunities.")
            for opp in opportunities:
                # Execution logic will be implemented here
                logger.info(f"Ready to execute trade for: {opp['item']}")
        else:
            logger.info("No profitable opportunities found in this cycle.")

    async def start(self, interval=3600):
        """
        Starts the trading engine loop.
        """
        logger.info(f"TradingEngine loop started with interval of {interval} seconds.")
        while True:
            await self.run_cycle()
            await asyncio.sleep(interval)

if __name__ == "__main__":
    engine = TradingEngine()
    asyncio.run(engine.run_cycle())
