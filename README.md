# Facebook Marketplace Agent

US-focused marketplace monitoring agent that collects listings from a pluggable source, filters by state/city/radius and listing attributes, ranks candidates with AI, deduplicates them, and sends high-quality matches through WhatsApp Cloud API.

> Important: the repository intentionally isolates Marketplace collection behind a provider interface. Use only data access methods that you are authorized to use and that comply with Meta's applicable terms and policies.

## MVP architecture

- **FastAPI**: saved searches, listings, health endpoints
- **PostgreSQL + PostGIS-ready location model**: searches, locations, listings, matches, analyses, notifications
- **Worker pipeline**: collect -> normalize -> deterministic filter -> AI score -> notify
- **Collector abstraction**: mock collector included; browser/provider implementations can be added without changing the rest of the app
- **OpenAI**: optional listing scoring and concise deal summaries
- **WhatsApp Cloud API**: optional notifications
- **Docker Compose**: API + PostgreSQL for local development
- **GitHub Actions**: lint/test CI

## Location filtering

The US is the only enabled country in the MVP. A search supports:

- one or more states
- one or more cities
- city + radius in miles
- ZIP/postal code fields
- deterministic latitude/longitude distance checks when coordinates are available

Example:

```json
{
  "name": "Toyota deals in SoCal",
  "category": "vehicles",
  "keywords": ["Toyota", "Camry"],
  "min_price": 5000,
  "max_price": 18000,
  "locations": [
    {
      "state_code": "CA",
      "city": "San Diego",
      "radius_miles": 40,
      "latitude": 32.7157,
      "longitude": -117.1611
    }
  ]
}
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API docs: `http://localhost:8000/docs`

Run tests locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Main endpoints

- `GET /health`
- `POST /api/v1/searches`
- `GET /api/v1/searches`
- `GET /api/v1/searches/{id}`
- `POST /api/v1/searches/{id}/run`
- `GET /api/v1/listings`

`POST /api/v1/searches/{id}/run` uses the configured collector. The default `mock` collector makes the whole pipeline testable without Facebook credentials or browser automation.

## Environment

See `.env.example`. AI and WhatsApp integrations are optional and degrade gracefully when credentials are absent.

## Next production steps

1. Add an authorized Marketplace data/provider implementation behind `Collector`.
2. Move synchronous search execution to SQS workers.
3. Add EventBridge schedules for saved searches.
4. Enable PostGIS geography columns/indexes for large-scale radius searches.
5. Add authentication and per-user WhatsApp destinations.
6. Add a lightweight Next.js admin UI.
