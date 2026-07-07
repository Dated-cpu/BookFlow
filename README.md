# BookFlow AI

Scheduling & Appointment Management SaaS.

## Stack

- Python 3.13, FastAPI, SQLAlchemy 2 (async), PostgreSQL
- Clean Architecture, Repository Pattern, Dependency Injection
- Ruff, uv, Docker

## Quickstart

```bash
make docker-up
make migrate
make dev
```

## Development

| Command | Purpose |
|---|---|
| `make lint` | Run Ruff linter |
| `make format` | Format code |
| `make typecheck` | Run mypy |
| `make test` | Run tests |
| `make migration message="desc"` | Auto-generate Alembic migration |

## Architecture

```
src/
├── domain/          # Entities, repository interfaces, value objects
├── application/     # Use cases, ports, DTOs
├── infrastructure/  # Database, auth, config, DI wiring
└── presentation/    # FastAPI app, routers, schemas
```

Domain layer has zero framework dependencies. All dependencies point inward.
