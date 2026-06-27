.PHONY: dev up down build logs

dev:
	npm run dev

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f
