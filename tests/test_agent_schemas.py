import pytest
from pydantic import ValidationError

from app.schemas import AgentCreate


def valid_payload():
    return {
        "name": "San Diego Camrys",
        "phone_number": "+14155552671",
        "instructions": "Prefer clean-title vehicles.",
        "schedule_minutes": 30,
        "notify_threshold": 80,
        "filters": {
            "category": "vehicles",
            "min_price": 5000,
            "max_price": 18000,
            "keywords": ["Toyota", "Camry"],
            "exclude_keywords": ["salvage"],
            "locations": [{"state_code": "CA", "city": "San Diego", "radius_miles": 50}],
        },
    }


def test_agent_configuration_is_valid():
    agent = AgentCreate(**valid_payload())
    assert agent.filters.locations[0].state_code == "CA"
    assert agent.phone_number == "+14155552671"


def test_agent_requires_a_location():
    payload = valid_payload()
    payload["filters"]["locations"] = []
    with pytest.raises(ValidationError):
        AgentCreate(**payload)


def test_agent_rejects_invalid_price_range():
    payload = valid_payload()
    payload["filters"]["min_price"] = 20000
    payload["filters"]["max_price"] = 10000
    with pytest.raises(ValidationError):
        AgentCreate(**payload)


def test_agent_requires_e164_phone_number():
    payload = valid_payload()
    payload["phone_number"] = "4155552671"
    with pytest.raises(ValidationError):
        AgentCreate(**payload)
