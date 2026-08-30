from app.collectors.base import CollectedListing, Collector


class MockCollector(Collector):
    """Safe local collector used until an authorized Marketplace source is configured."""

    def collect(self, search) -> list[CollectedListing]:
        location = search.locations[0]
        return [
            CollectedListing(
                external_id=f"mock-{search.id}-1",
                title="2021 Toyota Camry SE",
                description="Clean title, automatic, service records available",
                category=search.category or "vehicles",
                price=17500,
                url="https://example.com/listing/mock-1",
                state_code=location.state_code,
                city=location.city,
                postal_code=location.postal_code,
                latitude=location.latitude,
                longitude=location.longitude,
            ),
            CollectedListing(
                external_id=f"mock-{search.id}-2",
                title="Toyota Camry project car",
                description="Accident damage, needs repair",
                category=search.category or "vehicles",
                price=4500,
                url="https://example.com/listing/mock-2",
                state_code=location.state_code,
                city=location.city,
                postal_code=location.postal_code,
                latitude=location.latitude,
                longitude=location.longitude,
            ),
        ]
