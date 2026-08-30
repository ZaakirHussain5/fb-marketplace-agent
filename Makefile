.PHONY: up down restart logs ps smoke clean config

up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build -d

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

smoke:
	sh scripts/smoke.sh

config:
	docker compose config

clean:
	docker compose down -v --remove-orphans
