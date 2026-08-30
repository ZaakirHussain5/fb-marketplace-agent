import httpx

from app.config import get_settings
from app.models import Listing


class WhatsAppNotifier:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(
            self.settings.whatsapp_access_token
            and self.settings.whatsapp_phone_number_id
            and self.settings.whatsapp_recipient
        )

    def send_listing(self, listing: Listing, score: int, reasons: list[str], risks: list[str]) -> bool:
        if not self.enabled:
            return False

        reason_text = "\n".join(f"• {item}" for item in reasons[:3]) or "• Strong saved-search match"
        risk_text = "\n".join(f"• {item}" for item in risks[:2])
        body = (
            f"🔥 {score}% Marketplace match\n\n"
            f"{listing.title}\n"
            f"${float(listing.price):,.0f}\n" if listing.price is not None else f"{listing.title}\n"
        )
        body += f"{listing.city or ''}{', ' + listing.state_code if listing.state_code else ''}\n\n{reason_text}"
        if risk_text:
            body += f"\n\n⚠️ Watch for:\n{risk_text}"
        body += f"\n\nView listing: {listing.url}"

        url = (
            f"https://graph.facebook.com/{self.settings.meta_graph_version}/"
            f"{self.settings.whatsapp_phone_number_id}/messages"
        )
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": self.settings.whatsapp_recipient,
                "type": "text",
                "text": {"preview_url": True, "body": body},
            },
            timeout=20,
        )
        response.raise_for_status()
        return True
