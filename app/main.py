from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.collectors.mock import MockCollector
from app.db import Base, engine, get_db
from app.models import Agent, Listing, SavedSearch, SearchLocation
from app.schemas import (
    AgentCreate,
    AgentRead,
    AgentUpdate,
    ListingRead,
    SearchCreate,
    SearchRead,
    SearchRunResult,
)
from app.services.pipeline import SearchPipeline

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketplace Deal Agent", version="0.2.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/agents", response_model=AgentRead)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    agent = Agent(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@app.get("/api/v1/agents", response_model=list[AgentRead])
def list_agents(db: Session = Depends(get_db)):
    return db.scalars(select(Agent).order_by(Agent.created_at.desc())).all()


@app.get("/api/v1/agents/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.patch("/api/v1/agents/{agent_id}", response_model=AgentRead)
def update_agent(agent_id: int, payload: AgentUpdate, db: Session = Depends(get_db)):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, key, value)
    db.commit()
    db.refresh(agent)
    return agent


@app.delete("/api/v1/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"deleted": True}


@app.post("/api/v1/searches", response_model=SearchRead)
def create_search(payload: SearchCreate, db: Session = Depends(get_db)):
    if payload.min_price is not None and payload.max_price is not None and payload.min_price > payload.max_price:
        raise HTTPException(status_code=422, detail="min_price cannot exceed max_price")
    if payload.agent_id is not None and not db.get(Agent, payload.agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    search = SavedSearch(
        agent_id=payload.agent_id,
        name=payload.name,
        category=payload.category,
        keywords=payload.keywords,
        exclude_keywords=payload.exclude_keywords,
        min_price=payload.min_price,
        max_price=payload.max_price,
        notify_threshold=payload.notify_threshold,
    )
    search.locations = [SearchLocation(**location.model_dump()) for location in payload.locations]
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


@app.get("/api/v1/searches", response_model=list[SearchRead])
def list_searches(agent_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(SavedSearch).options(selectinload(SavedSearch.locations))
    if agent_id is not None:
        stmt = stmt.where(SavedSearch.agent_id == agent_id)
    return db.scalars(stmt.order_by(SavedSearch.created_at.desc())).all()


@app.get("/api/v1/searches/{search_id}", response_model=SearchRead)
def get_search(search_id: int, db: Session = Depends(get_db)):
    search = db.scalar(
        select(SavedSearch).where(SavedSearch.id == search_id).options(selectinload(SavedSearch.locations))
    )
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return search


@app.post("/api/v1/searches/{search_id}/run", response_model=SearchRunResult)
def run_search(search_id: int, db: Session = Depends(get_db)):
    search = db.scalar(
        select(SavedSearch).where(SavedSearch.id == search_id).options(selectinload(SavedSearch.locations))
    )
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return SearchPipeline(MockCollector()).run(db, search)


@app.get("/api/v1/listings", response_model=list[ListingRead])
def list_listings(db: Session = Depends(get_db)):
    return db.scalars(select(Listing).order_by(Listing.first_seen_at.desc()).limit(100)).all()
