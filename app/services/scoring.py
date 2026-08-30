import json

from openai import OpenAI

from app.config import get_settings
from app.models import Listing, SavedSearch


class ListingScorer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    def score(self, listing: Listing, search: SavedSearch) -> tuple[int, list[str], list[str], bool]:
        if not self.client:
            return self._fallback_score(listing, search)

        prompt = {
            "task": "Score how strongly this marketplace listing matches the saved search. Be conservative.",
            "search": {
                "name": search.name,
                "category": search.category,
                "keywords": search.keywords,
                "exclude_keywords": search.exclude_keywords,
                "min_price": float(search.min_price) if search.min_price is not None else None,
                "max_price": float(search.max_price) if search.max_price is not None else None,
            },
            "listing": {
                "title": listing.title,
                "description": listing.description,
                "category": listing.category,
                "price": float(listing.price) if listing.price is not None else None,
                "city": listing.city,
                "state": listing.state_code,
            },
            "output": {
                "score": "integer 0-100",
                "reasons": "array of short strings",
                "risks": "array of short strings",
            },
        }
        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=json.dumps(prompt),
        )
        try:
            data = json.loads(response.output_text)
            score = max(0, min(100, int(data.get("score", 0))))
            reasons = [str(item) for item in data.get("reasons", [])][:5]
            risks = [str(item) for item in data.get("risks", [])][:5]
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._fallback_score(listing, search)
        return score, reasons, risks, score >= search.notify_threshold

    @staticmethod
    def _fallback_score(listing: Listing, search: SavedSearch) -> tuple[int, list[str], list[str], bool]:
        score = 70
        reasons = ["Passed deterministic location, keyword, category, and price filters"]
        risks: list[str] = []
        haystack = f"{listing.title} {listing.description or ''}".casefold()
        keyword_hits = sum(1 for word in search.keywords if word.casefold() in haystack)
        score += min(20, keyword_hits * 5)
        if listing.price is not None and search.max_price is not None:
            if float(listing.price) <= float(search.max_price) * 0.9:
                score += 5
                reasons.append("Price is comfortably below the configured maximum")
        score = min(score, 100)
        return score, reasons, risks, score >= search.notify_threshold
