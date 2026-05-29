import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
import json
from src.scanner import SteamMarketScanner

class TestSteamMarketScanner(unittest.TestCase):

    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47"}]}')
    def test_load_config_success(self, mock_file, mock_exists):
        mock_exists.return_value = True
        scanner = SteamMarketScanner()
        self.assertEqual(len(scanner.items_to_scan), 1)
        self.assertEqual(scanner.items_to_scan[0]["market_hash_name"], "AK-47")

    def test_parse_price(self):
        scanner = SteamMarketScanner(config_path="non_existent.json")
        self.assertEqual(scanner._parse_price("$15.00"), 15.0)
        self.assertEqual(scanner._parse_price("15,00€"), 15.0)
        self.assertEqual(scanner._parse_price("£10.50"), 10.5)
        self.assertEqual(scanner._parse_price("$1,200.50"), 1200.5)
        self.assertEqual(scanner._parse_price(None), 0.0)

    def test_analyze_opportunity_found(self):
        scanner = SteamMarketScanner(config_path="non_existent.json")
        item_config = {
            "market_hash_name": "AK-47",
            "target_buy_price": 20.0,
            "min_profit_margin": 0.1
        }
        price_data = {"lowest_price": "$15.00"}

        opp = scanner.analyze_opportunity(item_config, price_data)

        self.assertIsNotNone(opp)
        self.assertEqual(opp["item"], "AK-47")
        self.assertEqual(opp["margin"], 0.25)

    @patch('src.scanner.SteamMarketScanner.fetch_item_price')
    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47", "target_buy_price": 20.0, "min_profit_margin": 0.1}]}')
    def test_scan_market(self, mock_file, mock_exists, mock_fetch):
        mock_exists.return_value = True
        mock_fetch.return_value = {"success": True, "lowest_price": "$15.00"}

        scanner = SteamMarketScanner()
        opportunities = scanner.scan_market(delay=0)

        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0]["item"], "AK-47")

if __name__ == '__main__':
    unittest.main()
