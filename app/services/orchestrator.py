from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.collectors.mock import MockCollector
from app.models import Agent, AgentRun, SavedSearch, SearchLocation
from app.services.pipeline import SearchPipeline


class AgentOrchestrator:
    def due_agents(self, db: Session) -> list[Agent]:
        now = datetime.utcnow()
        return list(
            db.scalars(
                select(Agent)
                .where(Agent.enabled.is_(True))
                .where((Agent.next_run_at.is_(None)) | (Agent.next_run_at <= now))
                .order_by(Agent.next_run_at.asc().nullsfirst())
            ).all()
        )

    def ensure_search(self, db: Session, agent: Agent) -> SavedSearch:
        search = db.scalar(
            select(SavedSearch)
            .where(SavedSearch.agent_id == agent.id)
            .options(selectinload(SavedSearch.locations))
        )
        filters = agent.filters or {}
        if search is None:
            search = SavedSearch(agent_id=agent.id, name=f"{agent.name} search")
            db.add(search)

        search.name = f"{agent.name} search"
        search.category = filters.get("category") or None
        search.keywords = filters.get("keywords") or []
        search.exclude_keywords = filters.get("exclude_keywords") or []
        search.min_price = filters.get("min_price")
        search.max_price = filters.get("max_price")
        search.notify_threshold = agent.notify_threshold
        search.enabled = agent.enabled

        locations = filters.get("locations") or []
        search.locations.clear()
        for location in locations:
            search.locations.append(
                SearchLocation(
                    country_code="US",
                    state_code=str(location.get("state_code", "")).upper(),
                    city=location.get("city") or None,
                    postal_code=location.get("postal_code") or None,
                    latitude=location.get("latitude"),
                    longitude=location.get("longitude"),
                    radius_miles=location.get("radius_miles"),
                )
            )
        db.flush()
        return search

    def run_agent(self, db: Session, agent: Agent, trigger: str = "manual") -> AgentRun:
        run = AgentRun(agent_id=agent.id, trigger=trigger, status="running", started_at=datetime.utcnow())
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            search = self.ensure_search(db, agent)
            result = SearchPipeline(MockCollector()).run(db, search, agent=agent, run_id=run.id)
            run.collected = result["collected"]
            run.matched = result["matched"]
            run.notified = result["notified"]
            run.status = "succeeded"
            run.finished_at = datetime.utcnow()
            agent.last_run_at = run.finished_at
            agent.next_run_at = run.finished_at + timedelta(minutes=max(agent.schedule_minutes, 1))
            db.commit()
        except Exception as exc:
            db.rollback()
            run = db.get(AgentRun, run.id)
            agent = db.get(Agent, agent.id)
            if run:
                run.status = "failed"
                run.error = str(exc)[:4000]
                run.finished_at = datetime.utcnow()
            if agent:
                agent.last_run_at = datetime.utcnow()
                agent.next_run_at = datetime.utcnow() + timedelta(minutes=max(agent.schedule_minutes, 1))
            db.commit()
        return run
