.PHONY: dev lint format typecheck test migrate revision downgrade docker-build docker-up docker-down clean

dev:
	uv run uvicorn src.presentation.main:app --reload

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(message)"

downgrade:
	uv run alembic downgrade "$(rev)"

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
