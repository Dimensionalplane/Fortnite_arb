import logging
import aiohttp
import asyncio
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages multiple notification channels (Discord, Email) asynchronously.
    """

    def __init__(self, config):
        self.config = config.get("notifications", {})
        self.discord_url = self.config.get("discord_webhook_url")
        self.email_config = self.config.get("email", {})

    async def _post_with_retry(self, session, url, json_payload, max_retries=3):
        for attempt in range(max_retries):
            try:
                async with session.post(url, json=json_payload, timeout=10) as response:
                    if response.status >= 500:
                        logger.warning(f"Server error {response.status}. Retrying...")
                    else:
                        response.raise_for_status()
                        return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        return False

    async def send_discord(self, session, opportunity):
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
        success = await self._post_with_retry(session, self.discord_url, payload)
        if success:
            logger.info(f"Discord alert sent for {opportunity['item']}")
        return success

    async def send_summary_report(self, session, opportunities):
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
        return await self._post_with_retry(session, self.discord_url, payload)

    async def send_email(self, opportunity):
        if not self.email_config.get("enabled"):
            return False

        # Email sending is still blocking in this implementation as smtplib doesn't natively support asyncio.
        # We wrap it in a thread to prevent blocking the event loop.
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_email_sync, opportunity)

    def _send_email_sync(self, opportunity):
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

    async def notify_all(self, opportunities):
        async with aiohttp.ClientSession() as session:
            tasks = []
            # For each opportunity, send a discord alert and an email
            if isinstance(opportunities, list):
                # We usually get the full list for summary
                tasks.append(self.send_summary_report(session, opportunities))
                for opp in opportunities:
                    tasks.append(self.send_email(opp))
            else:
                # Handle single opportunity
                tasks.append(self.send_discord(session, opportunities))
                tasks.append(self.send_email(opportunities))

            await asyncio.gather(*tasks)
