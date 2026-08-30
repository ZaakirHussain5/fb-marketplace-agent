import logging
import time

from app.db import Base, SessionLocal, engine
from app.services.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("orchestrator-worker")

POLL_SECONDS = 10


def tick() -> None:
    orchestrator = AgentOrchestrator()
    with SessionLocal() as db:
        agents = orchestrator.due_agents(db)
        for agent in agents:
            logger.info("Running agent id=%s name=%s", agent.id, agent.name)
            run = orchestrator.run_agent(db, agent, trigger="scheduled")
            logger.info(
                "Finished run id=%s status=%s collected=%s matched=%s notified=%s",
                run.id,
                run.status,
                run.collected,
                run.matched,
                run.notified,
            )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Agent orchestrator worker started; poll interval=%ss", POLL_SECONDS)
    while True:
        try:
            tick()
        except Exception:
            logger.exception("Worker tick failed")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
