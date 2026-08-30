# Facebook Marketplace Agent

US-focused marketplace monitoring platform that manages multiple independent agents. Each agent has its own WhatsApp destination, filters, instructions, cadence and notification threshold.

> The Marketplace collection layer is intentionally isolated behind a provider interface. Use only data access methods that you are authorized to use and that comply with Meta's applicable terms and policies.

## Monorepo

```text
fb-marketplace-agent/
├── apps/
│   └── web/                 # Next.js agent management UI
├── app/                     # FastAPI service
│   ├── collectors/          # Replaceable listing collectors
│   ├── services/            # filtering, AI, notifications, pipeline
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/                   # backend tests
├── package.json             # npm workspace root
├── pyproject.toml           # Python service dependencies
└── docker-compose.yml       # Postgres + API + web
```

The repo is a heterogeneous monorepo: the Next.js application is managed through the root npm workspace and the FastAPI service uses the root Python project.

## Multi-agent management

The Next.js UI at `http://localhost:3000` provides:

- agent dashboard with active/paused status
- create, edit and delete agents
- activate/pause agents
- WhatsApp phone number per agent
- custom natural-language instructions
- category filters
- minimum/maximum price
- include/exclude keywords
- US state selection
- city and radius filtering
- polling cadence
- AI notification score threshold
- quick agent search

Each agent persists fields similar to:

```json
{
  "name": "California Toyota deals",
  "phone_number": "+14155552671",
  "instructions": "Only notify me for clean-title vehicles with clear descriptions.",
  "enabled": true,
  "schedule_minutes": 30,
  "notify_threshold": 85,
  "filters": {
    "category": "vehicles",
    "min_price": 5000,
    "max_price": 18000,
    "keywords": ["Toyota", "Camry"],
    "exclude_keywords": ["salvage", "parts"],
    "locations": [
      {
        "state_code": "CA",
        "city": "San Diego",
        "radius_miles": 50
      }
    ]
  }
}
```

## Backend API

- `GET /health`
- `POST /api/v1/agents`
- `GET /api/v1/agents`
- `GET /api/v1/agents/{id}`
- `PATCH /api/v1/agents/{id}`
- `DELETE /api/v1/agents/{id}`
- `POST /api/v1/searches`
- `GET /api/v1/searches?agent_id=<id>`
- `POST /api/v1/searches/{id}/run`
- `GET /api/v1/listings`

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web UI: `http://localhost:3000`
- FastAPI docs: `http://localhost:8000/docs`

For frontend-only development:

```bash
npm install
npm run dev:web
```

For backend tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Architecture

```text
Next.js management UI
        ↓
FastAPI agent/search API
        ↓
PostgreSQL
        ↓
Scheduler / queue
        ↓
Marketplace collector provider
        ↓
Deterministic filters
        ↓
AI scoring + instructions
        ↓
WhatsApp Cloud API
```

Location, price, category and keyword filters should remain deterministic. AI is used after those filters for ranking, interpretation and agent-specific instructions.

## Current collection mode

The default collector is a mock provider so the full application can be developed and tested without Facebook credentials or browser automation. A real authorized listing source can be added behind the collector interface without changing the UI, filtering pipeline or notification architecture.

## Next production steps

1. Add an authorized Marketplace data/provider implementation.
2. Move agent execution to SQS workers.
3. Use EventBridge schedules based on each agent's `schedule_minutes`.
4. Add PostGIS geography columns/indexes for large-scale radius searches.
5. Store WhatsApp credentials securely and add delivery history.
6. Add authentication and tenant/user ownership for agents.
7. Add run history, listing matches and notification analytics to the UI.
