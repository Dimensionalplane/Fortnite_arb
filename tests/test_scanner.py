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

    @patch('src.scanner.os.path.exists')
    def test_load_config_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        scanner = SteamMarketScanner()
        self.assertEqual(len(scanner.items_to_scan), 0)

    @patch('src.scanner.requests.get')
    def test_fetch_item_price_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "lowest_price": "2,50€",
            "volume": "1,234",
            "median_price": "2,45€"
        }
        mock_get.return_value = mock_response

        scanner = SteamMarketScanner(config_path="non_existent.json")
        result = scanner.fetch_item_price(730, "AK-47 | Redline (Field-Tested)")

        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["lowest_price"], "2,50€")

    @patch('src.scanner.SteamMarketScanner.fetch_item_price')
    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47"}]}')
    def test_scan_market(self, mock_file, mock_exists, mock_fetch):
        mock_exists.return_value = True
        mock_fetch.return_value = {"success": True, "lowest_price": "10€"}

        scanner = SteamMarketScanner()
        results = scanner.scan_market()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["item"], "AK-47")
        self.assertEqual(results[0]["price_data"]["lowest_price"], "10€")

if __name__ == '__main__':
    unittest.main()
