import unittest
from unittest.mock import patch, MagicMock
import requests
from src.scanner import SteamMarketScanner

class TestSteamMarketScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = SteamMarketScanner()

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

        result = self.scanner.fetch_item_price(730, "AK-47 | Redline (Field-Tested)")

        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["lowest_price"], "2,50€")
        mock_get.assert_called_once()

    @patch('src.scanner.requests.get')
    def test_fetch_item_price_failure(self, mock_get):
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_get.return_value = mock_response

        result = self.scanner.fetch_item_price(730, "Non-Existent Item")

        self.assertIsNone(result)

    def test_scan_market_returns_list(self):
        result = self.scanner.scan_market(730)
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
