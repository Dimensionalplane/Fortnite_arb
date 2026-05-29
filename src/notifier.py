import logging
import requests

logger = logging.getLogger(__name__)

class DiscordNotifier:
    """
    Handles sending notifications to Discord via webhooks.
    """

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_notification(self, opportunity):
        """
        Sends an arbitrage opportunity alert to Discord.
        """
        if not self.webhook_url:
            logger.debug("Discord webhook URL not configured. Skipping notification.")
            return False

        payload = {
            "embeds": [{
                "title": "🚨 Arbitrage Opportunity Found!",
                "color": 3066993,  # Green
                "fields": [
                    {"name": "Item", "value": opportunity['item'], "inline": True},
                    {"name": "App ID", "value": str(opportunity.get('app_id', 'N/A')), "inline": True},
                    {"name": "Current Price", "value": f"{opportunity['current_price']}", "inline": True},
                    {"name": "Target Price", "value": f"{opportunity['target_price']}", "inline": True},
                    {"name": "Margin", "value": f"{opportunity['margin']:.2%}", "inline": True}
                ],
                "footer": {"text": "Steam Market Arb Bot"}
            }]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Notification sent to Discord for {opportunity['item']}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
