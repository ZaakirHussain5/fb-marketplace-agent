from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import CollectedListing, Collector
from app.models import Agent, Listing, ListingMatch, SavedSearch
from app.services.filtering import listing_matches_search
from app.services.scoring import ListingScorer
from app.services.whatsapp import WhatsAppNotifier


class SearchPipeline:
    def __init__(self, collector: Collector) -> None:
        self.collector = collector
        self.scorer = ListingScorer()
        self.notifier = WhatsAppNotifier()

    def run(
        self,
        db: Session,
        search: SavedSearch,
        agent: Agent | None = None,
        run_id: int | None = None,
    ) -> dict[str, int]:
        collected = self.collector.collect(search)
        matched = 0
        notified = 0

        for item in collected:
            listing = self._upsert_listing(db, item)
            if not listing_matches_search(listing, search):
                continue

            matched += 1
            existing_match = db.scalar(
                select(ListingMatch).where(
                    ListingMatch.search_id == search.id,
                    ListingMatch.listing_id == listing.id,
                )
            )
            if existing_match:
                continue

            score, reasons, risks, should_notify = self.scorer.score(
                listing,
                search,
                instructions=agent.instructions if agent else "",
            )
            threshold = agent.notify_threshold if agent else search.notify_threshold
            should_notify = bool(should_notify and score >= threshold)

            match = ListingMatch(
                search_id=search.id,
                listing_id=listing.id,
                run_id=run_id,
                score=score,
                reasons=reasons,
                risks=risks,
                should_notify=should_notify,
                delivery_status="pending" if should_notify else "not_requested",
            )
            db.add(match)
            db.flush()

            if should_notify:
                try:
                    if self.notifier.send_listing(
                        listing,
                        score,
                        reasons,
                        risks,
                        recipient=agent.phone_number if agent else None,
                    ):
                        match.notified_at = datetime.utcnow()
                        match.delivery_status = "sent"
                        notified += 1
                    else:
                        match.delivery_status = "skipped_unconfigured"
                except Exception as exc:
                    match.delivery_status = "failed"
                    match.delivery_error = str(exc)[:2000]

        db.commit()
        return {"collected": len(collected), "matched": matched, "notified": notified}

    @staticmethod
    def _upsert_listing(db: Session, item: CollectedListing) -> Listing:
        listing = db.scalar(select(Listing).where(Listing.external_id == item.external_id))
        now = datetime.utcnow()
        values = {
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "price": item.price,
            "currency": item.currency,
            "url": item.url,
            "image_url": item.image_url,
            "country_code": item.country_code,
            "state_code": item.state_code,
            "city": item.city,
            "postal_code": item.postal_code,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "raw_payload": item.raw_payload,
            "last_seen_at": now,
        }
        if listing:
            for key, value in values.items():
                setattr(listing, key, value)
            db.flush()
            return listing

        listing = Listing(external_id=item.external_id, first_seen_at=now, **values)
        db.add(listing)
        db.flush()
        return listing
