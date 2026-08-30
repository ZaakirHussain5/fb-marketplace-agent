from types import SimpleNamespace

from app.services.filtering import distance_miles, location_matches


def test_distance_miles_between_la_and_san_diego_is_reasonable():
    distance = distance_miles(34.0522, -118.2437, 32.7157, -117.1611)
    assert 105 < distance < 130


def test_location_matches_city_radius():
    listing = SimpleNamespace(
        country_code="US",
        state_code="CA",
        city="La Jolla",
        postal_code="92037",
        latitude=32.8328,
        longitude=-117.2713,
    )
    location = SimpleNamespace(
        country_code="US",
        state_code="CA",
        city="San Diego",
        postal_code=None,
        latitude=32.7157,
        longitude=-117.1611,
        radius_miles=20,
    )
    assert location_matches(listing, location)


def test_location_rejects_wrong_state():
    listing = SimpleNamespace(
        country_code="US",
        state_code="NV",
        city="Las Vegas",
        postal_code=None,
        latitude=36.1716,
        longitude=-115.1391,
    )
    location = SimpleNamespace(
        country_code="US",
        state_code="CA",
        city=None,
        postal_code=None,
        latitude=None,
        longitude=None,
        radius_miles=None,
    )
    assert not location_matches(listing, location)
