import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
import json
import asyncio
from src.scanner import SteamMarketScanner
from src.notifier import NotificationManager

class TestSteamMarketScanner(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

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

    @patch('src.notifier.aiohttp.ClientSession.post')
    def test_discord_notification_send(self, mock_post):
        async def run_test():
            config = {"notifications": {"discord_webhook_url": "http://mock-webhook"}}
            notifier = NotificationManager(config)
            opp = {"item": "AK-47", "current_price": 10.0, "target_price": 20.0, "margin": 0.5}

            mock_resp = MagicMock()
            mock_resp.status = 204
            mock_resp.__aenter__.return_value = mock_resp
            mock_post.return_value = mock_resp

            import aiohttp
            async with aiohttp.ClientSession() as session:
                result = await notifier.send_discord(session, opp)
                self.assertTrue(result)

        self.loop.run_until_complete(run_test())

    @patch('src.scanner.SteamMarketScanner.fetch_item_price')
    @patch('src.notifier.NotificationManager.notify_all')
    @patch('src.scanner.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"items": [{"app_id": 730, "market_hash_name": "AK-47", "target_buy_price": 20.0, "min_profit_margin": 0.1}]}')
    def test_scan_market_triggers_notification(self, mock_file, mock_exists, mock_notify, mock_fetch):
        async def run_test():
            mock_exists.return_value = True
            mock_fetch.return_value = {"success": True, "lowest_price": "$15.00"}

            scanner = SteamMarketScanner()
            opportunities = await scanner.scan_market()

            self.assertEqual(len(opportunities), 1)
            mock_notify.assert_called_once()

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
