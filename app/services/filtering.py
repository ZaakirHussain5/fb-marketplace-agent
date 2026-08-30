from math import asin, cos, radians, sin, sqrt

from app.models import Listing, SavedSearch, SearchLocation


def distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 3958.7613
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * radius * asin(sqrt(a))


def location_matches(listing: Listing, location: SearchLocation) -> bool:
    if listing.country_code.upper() != "US" or location.country_code.upper() != "US":
        return False
    if not listing.state_code or listing.state_code.upper() != location.state_code.upper():
        return False

    if location.city and listing.city and listing.city.casefold() != location.city.casefold():
        if not all(
            value is not None
            for value in (location.latitude, location.longitude, listing.latitude, listing.longitude)
        ):
            return False

    if location.postal_code and listing.postal_code != location.postal_code:
        return False

    if location.radius_miles is not None:
        coordinates = (location.latitude, location.longitude, listing.latitude, listing.longitude)
        if any(value is None for value in coordinates):
            return False
        return distance_miles(*coordinates) <= location.radius_miles  # type: ignore[arg-type]

    return True


def listing_matches_search(listing: Listing, search: SavedSearch) -> bool:
    if listing.country_code.upper() != "US":
        return False
    if search.category and listing.category and search.category.casefold() != listing.category.casefold():
        return False

    price = float(listing.price) if listing.price is not None else None
    if search.min_price is not None and (price is None or price < float(search.min_price)):
        return False
    if search.max_price is not None and (price is None or price > float(search.max_price)):
        return False

    haystack = f"{listing.title} {listing.description or ''}".casefold()
    if search.keywords and not any(word.casefold() in haystack for word in search.keywords):
        return False
    if any(word.casefold() in haystack for word in search.exclude_keywords):
        return False

    return any(location_matches(listing, location) for location in search.locations)
