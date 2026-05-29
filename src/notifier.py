import logging
import requests
import smtplib
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
        try:
            requests.post(self.discord_url, json=payload).raise_for_status()
            logger.info(f"Discord alert sent for {opportunity['item']}")
            return True
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False

    def send_email(self, opportunity):
        if not self.email_config.get("enabled"):
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get("sender")
            msg['To'] = self.email_config.get("receiver")
            msg['Subject'] = f"Arbitrage Alert: {opportunity['item']}"

            body = f"""
            Arbitrage Opportunity Found!

            Item: {opportunity['item']}
            App ID: {opportunity.get('app_id')}
            Current Price: {opportunity['current_price']}
            Target Price: {opportunity['target_price']}
            Margin: {opportunity['margin']:.2%}
            """
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config.get("smtp_server"), self.email_config.get("smtp_port"))
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
