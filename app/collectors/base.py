from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CollectedListing:
    external_id: str
    title: str
    url: str
    price: float | None = None
    currency: str = "USD"
    description: str | None = None
    category: str | None = None
    image_url: str | None = None
    country_code: str = "US"
    state_code: str | None = None
    city: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)


class Collector(ABC):
    @abstractmethod
    def collect(self, search) -> list[CollectedListing]:
        raise NotImplementedError
