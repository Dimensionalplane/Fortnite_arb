import logging
import requests
import json
import os
import re
import time
from datetime import datetime

try:
    from src.notifier import NotificationManager
except ImportError:
    from notifier import NotificationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SteamMarketScanner:
    """
    A scanner for the Steam Market to identify arbitrage opportunities.
    """

    def __init__(self, config_path="config/items.json", history_path="data/scan_history.json"):
        self.config_path = config_path
        self.history_path = history_path
        self.base_url = "https://steamcommunity.com/market/priceoverview/"
        self.config = self._load_config()
        self.items_to_scan = self.config.get("items", [])
        self.notifier = NotificationManager(self.config)
        logger.info("SteamMarketScanner initialized.")

    def _load_config(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration: {e}")
            return {}

    def _parse_price(self, price_str):
        if not price_str:
            return 0.0
        cleaned = re.sub(r'[^\d,.]', '', price_str)
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def fetch_item_price(self, app_id, market_hash_name, currency=1):
        params = {"appid": app_id, "market_hash_name": market_hash_name, "currency": currency}
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data if data.get("success") else None
        except requests.RequestException:
            return None

    def analyze_opportunity(self, item_config, price_data):
        lowest_price = self._parse_price(price_data.get("lowest_price"))
        target_buy_price = item_config.get("target_buy_price", 0.0)
        min_profit_margin = item_config.get("min_profit_margin", 0.0)

        if lowest_price > 0 and lowest_price <= target_buy_price:
            profit = target_buy_price - lowest_price
            margin = profit / target_buy_price if target_buy_price > 0 else 0
            if margin >= min_profit_margin:
                opp = {
                    "item": item_config.get("market_hash_name"),
                    "app_id": item_config.get("app_id"),
                    "current_price": lowest_price,
                    "target_price": target_buy_price,
                    "margin": margin,
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"ARBITRAGE OPPORTUNITY FOUND: {opp['item']} - Margin: {margin:.2%}")
                return opp
        return None

    def _save_to_history(self, opportunities):
        if not opportunities:
            return

        history = []
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
            except (json.JSONDecodeError, IOError):
                history = []

        history.extend(opportunities)
        history = history[-100:]

        try:
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(history, f, indent=4)
            logger.info(f"Saved {len(opportunities)} items to history.")
        except IOError as e:
            logger.error(f"Failed to save history: {e}")

    def scan_market(self, delay=1.0):
        logger.info(f"Scanning market for {len(self.items_to_scan)} items.")
        opportunities = []
        for item in self.items_to_scan:
            app_id = item.get("app_id")
            market_hash_name = item.get("market_hash_name")
            if app_id and market_hash_name:
                price_data = self.fetch_item_price(app_id, market_hash_name)
                if price_data:
                    opp = self.analyze_opportunity(item, price_data)
                    if opp:
                        opportunities.append(opp)
                        self.notifier.notify_all(opp)
                time.sleep(delay)

        if opportunities:
            self.notifier.send_summary_report(opportunities)
            self._save_to_history(opportunities)

        logger.info(f"Scan complete. Found {len(opportunities)} opportunities.")
        return opportunities

if __name__ == "__main__":
    scanner = SteamMarketScanner()
    scanner.scan_market()
