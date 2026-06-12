import unittest
import asyncio
from unittest.mock import patch, MagicMock
from src.trading.engine import TradingEngine

class TestTradingEngine(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    @patch('src.scanner.SteamMarketScanner.scan_market')
    def test_run_cycle(self, mock_scan):
        async def run_test():
            mock_scan.return_value = [{"item": "AK-47", "margin": 0.1}]
            engine = TradingEngine()
            await engine.run_cycle()
            mock_scan.assert_called_once()

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
