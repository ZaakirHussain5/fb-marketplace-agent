import httpx

from app.config import get_settings
from app.models import Listing


class WhatsAppNotifier:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.whatsapp_access_token and self.settings.whatsapp_phone_number_id)

    def send_listing(
        self,
        listing: Listing,
        score: int,
        reasons: list[str],
        risks: list[str],
        recipient: str | None = None,
    ) -> bool:
        to = recipient or self.settings.whatsapp_recipient
        if not self.enabled or not to:
            return False

        reason_text = "\n".join(f"• {item}" for item in reasons[:3]) or "• Strong saved-search match"
        risk_text = "\n".join(f"• {item}" for item in risks[:2])
        price_line = f"${float(listing.price):,.0f}\n" if listing.price is not None else ""
        body = f"🔥 {score}% Marketplace match\n\n{listing.title}\n{price_line}"
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
                "to": to,
                "type": "text",
                "text": {"preview_url": True, "body": body},
            },
            timeout=20,
        )
        response.raise_for_status()
        return True
