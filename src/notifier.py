import logging
import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages multiple notification channels (Discord, Email).
    """

    def __init__(self, config):
        self.config = config.get("notifications", {})
        self.discord_url = self.config.get("discord_webhook_url")
        self.email_config = self.config.get("email", {})

    def _post_with_retry(self, url, json_payload, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=json_payload, timeout=10)
                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}. Retrying...")
                else:
                    response.raise_for_status()
                    return True
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) # Exponential backoff
        return False

    def send_discord(self, opportunity):
        if not self.discord_url:
            return False

        payload = {
            "embeds": [{
                "title": "🚨 Arbitrage Opportunity Found!",
                "color": 3066993,
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
        success = self._post_with_retry(self.discord_url, payload)
        if success:
            logger.info(f"Discord alert sent for {opportunity['item']}")
        return success

    def send_summary_report(self, opportunities):
        if not self.discord_url or not opportunities:
            return False

        fields = []
        for opp in opportunities:
            fields.append({"name": opp['item'], "value": f"Price: {opp['current_price']} | Margin: {opp['margin']:.2%}", "inline": False})

        payload = {
            "embeds": [{
                "title": f"📊 Scan Summary: {len(opportunities)} Opportunities Found",
                "color": 3447003,
                "fields": fields[:25],
                "footer": {"text": "Steam Market Arb Bot"}
            }]
        }
        return self._post_with_retry(self.discord_url, payload)

    def send_email(self, opportunity):
        if not self.email_config.get("enabled"):
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get("sender")
            msg['To'] = self.email_config.get("receiver")
            msg['Subject'] = f"Arbitrage Alert: {opportunity['item']}"

            body = f"Arbitrage Opportunity Found!\n\nItem: {opportunity['item']}\nMargin: {opportunity['margin']:.2%}"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config.get("smtp_server"), self.email_config.get("smtp_port"), timeout=15)
            server.starttls()
            server.login(self.email_config.get("sender"), self.email_config.get("password"))
            server.send_message(msg)
            server.quit()
            logger.info(f"Email alert sent for {opportunity['item']}")
            return True
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False

    def notify_all(self, opportunity):
        self.send_discord(opportunity)
        self.send_email(opportunity)
