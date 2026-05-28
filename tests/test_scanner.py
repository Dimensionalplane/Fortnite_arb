import unittest
from src.scanner import SteamMarketScanner

class TestSteamMarketScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = SteamMarketScanner()

    def test_fetch_item_price_returns_dict(self):
        result = self.scanner.fetch_item_price(730, "AK-47 | Redline (Field-Tested)")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["app_id"], 730)
        self.assertEqual(result["market_hash_name"], "AK-47 | Redline (Field-Tested)")

    def test_scan_market_returns_list(self):
        result = self.scanner.scan_market(730)
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
