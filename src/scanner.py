import logging
import requests
import json
import os

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

    def __init__(self, api_key=None, config_path="config/items.json"):
        self.api_key = api_key
        self.config_path = config_path
        self.base_url = "https://steamcommunity.com/market/priceoverview/"
        self.items_to_scan = self._load_config()
        logger.info("SteamMarketScanner initialized.")

    def _load_config(self):
        """
        Loads the list of items to scan from the configuration file.
        """
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            return []

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                items = config.get("items", [])
                logger.info(f"Loaded {len(items)} items from configuration.")
                return items
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration: {e}")
            return []

    def fetch_item_price(self, app_id, market_hash_name, currency=1):
        """
        Fetches the current price of an item from the Steam Market.
        """
        params = {
            "appid": app_id,
            "market_hash_name": market_hash_name,
            "currency": currency
        }
        logger.info(f"Fetching price for item: {market_hash_name} (App ID: {app_id})")

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                logger.info(f"Successfully fetched price for {market_hash_name}: {data.get('lowest_price')}")
                return data
            else:
                logger.warning(f"Failed to fetch price for {market_hash_name}: Success flag False")
                return None
        except requests.RequestException as e:
            logger.error(f"Error fetching price for {market_hash_name}: {e}")
            return None

    def scan_market(self):
        """
        Scans the market for all items defined in the configuration.
        """
        logger.info(f"Scanning market for {len(self.items_to_scan)} items.")
        results = []
        for item in self.items_to_scan:
            app_id = item.get("app_id")
            market_hash_name = item.get("market_hash_name")
            if app_id and market_hash_name:
                price_data = self.fetch_item_price(app_id, market_hash_name)
                if price_data:
                    results.append({
                        "item": market_hash_name,
                        "app_id": app_id,
                        "price_data": price_data
                    })
        return results
