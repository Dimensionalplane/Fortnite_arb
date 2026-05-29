import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
import json
from src.scanner import SteamMarketScanner
from src.notifier import DiscordNotifier

class TestSteamMarketScanner(unittest.TestCase):

    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47"}]}')
    def test_load_config_success(self, mock_file, mock_exists):
        mock_exists.return_value = True
        scanner = SteamMarketScanner()
        self.assertEqual(len(scanner.items_to_scan), 1)

    def test_parse_price(self):
        scanner = SteamMarketScanner(config_path="non_existent.json")
        self.assertEqual(scanner._parse_price("$15.00"), 15.0)
        self.assertEqual(scanner._parse_price("15,00€"), 15.0)

    @patch('src.notifier.requests.post')
    def test_discord_notification_send(self, mock_post):
        notifier = DiscordNotifier("http://mock-webhook")
        opp = {"item": "AK-47", "current_price": 10.0, "target_price": 20.0, "margin": 0.5}

        mock_post.return_value.status_code = 204
        result = notifier.send_notification(opp)

        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('src.notifier.requests.post')
    def test_discord_notification_no_url(self, mock_post):
        notifier = DiscordNotifier("")
        opp = {"item": "AK-47"}

        result = notifier.send_notification(opp)

        self.assertFalse(result)
        mock_post.assert_not_called()

    @patch('src.scanner.SteamMarketScanner.fetch_item_price')
    @patch('src.notifier.DiscordNotifier.send_notification')
    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47", "target_buy_price": 20.0, "min_profit_margin": 0.1}]}')
    def test_scan_market_triggers_notification(self, mock_file, mock_exists, mock_notify, mock_fetch):
        mock_exists.return_value = True
        mock_fetch.return_value = {"success": True, "lowest_price": "$15.00"}

        scanner = SteamMarketScanner()
        opportunities = scanner.scan_market(delay=0)

        self.assertEqual(len(opportunities), 1)
        mock_notify.assert_called_once()

if __name__ == '__main__':
    unittest.main()
