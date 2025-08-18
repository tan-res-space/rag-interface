# Local PostgreSQL Setup & Integration Guide (RAG Interface)

This page explains how to set up a local PostgreSQL 15 database in a Podman container, test connectivity, and integrate it with the Python + FastAPI RAG interface project (Hexagonal Architecture). It includes exact commands, environment variables, schema creation, and verification steps.

---

## 0) At a glance

- DB engine: PostgreSQL 15 (container)
- Container runtime: Podman (compatible with Docker CLI flags)
- App ORM/driver: SQLAlchemy 2.x (async) + asyncpg
- Connection URI format: `postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`

---

## 1) PostgreSQL Container Setup (Podman)

### 1.1 Create persistent storage

- Recommended: named Podman volume

```bash
podman volume create pgdata_rag
```

- Alternative: host folder (so you can inspect files)

```bash
mkdir -p "$HOME/pgdata/rag-interface"
```

### 1.2 Run PostgreSQL 15

Use either a named volume OR a host folder. Replace env values if needed.

- Using a named volume:

```bash
podman run -d \
  --name rag-postgres \
  -e POSTGRES_DB=error_reporting \
  -e POSTGRES_USER=ers_user \
  -e POSTGRES_PASSWORD=ers_password \
  -p 5432:5432 \
  -v pgdata_rag:/var/lib/postgresql/data \
  docker.io/library/postgres:15
```

- Using a host folder:

```bash
podman run -d \
  --name rag-postgres \
  -e POSTGRES_DB=error_reporting \
  -e POSTGRES_USER=ers_user \
  -e POSTGRES_PASSWORD=ers_password \
  -p 5432:5432 \
  -v "$HOME/pgdata/rag-interface:/var/lib/postgresql/data" \
  --replace \
  docker.io/library/postgres:15
```

Notes:
- `-p 5432:5432` exposes PostgreSQL on `localhost:5432`.
- If 5432 is taken, use another host port (e.g., `-p 55432:5432`) and update `DB_PORT` accordingly.

### 1.3 Optional: user-defined network (container ↔ container)

```bash
podman network create rag-net
podman run -d --name rag-postgres --network rag-net ... docker.io/library/postgres:15
```
- In this case, app containers on `rag-net` can use host `rag-postgres` and port `5432` without publishing to localhost.

---

## 2) Database Connection Testing

### 2.1 Check container status

```bash
podman ps --filter "name=rag-postgres"
podman logs -f rag-postgres   # Ctrl+C to stop
```

Expected log snippet: `database system is ready to accept connections`

### 2.2 Test with psql

- Inside the container:

```bash
podman exec -it rag-postgres psql -U ers_user -d error_reporting -c "SELECT version();"
podman exec -it rag-postgres pg_isready -U ers_user -d error_reporting
```

- Using local psql (if installed):

```bash
psql "host=localhost port=5432 dbname=error_reporting user=ers_user password=ers_password" -c "SELECT 1;"
```

### 2.3 Troubleshooting

- Port conflict: use a different host port `-p 55432:5432` and set `DB_PORT=55432`.
- Auth failed: verify `POSTGRES_USER`/`POSTGRES_PASSWORD` and your connection string.
- Connection refused: ensure container is running and port is mapped; check firewall.
- DB/role missing: ensure `POSTGRES_DB` is set (or create manually), and your `DB_DATABASE` matches.
- Python SSL/driver issues: ensure `asyncpg` and `SQLAlchemy` 2.x are installed and URI uses `postgresql+asyncpg`.

---

## 3) Wire PostgreSQL into the RAG Interface

The app reads DB configuration from environment variables; the adapter constructs the SQLAlchemy async URI like:

```
postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}
```

### 3.1 Install Python deps (from your venv)

```bash
pip install "SQLAlchemy>=2.0" asyncpg fastapi uvicorn
```

### 3.2 Create/update `.env` in repo root

```bash
echo "DB_TYPE=postgresql" > .env
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=5432" >> .env
echo "DB_DATABASE=error_reporting" >> .env
echo "DB_USERNAME=ers_user" >> .env
echo "DB_PASSWORD=ers_password" >> .env
echo "EVENT_BUS_TYPE=in_memory" >> .env
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
# Optional pool tuning
echo "DB_POOL_SIZE=10" >> .env
echo "DB_MAX_OVERFLOW=20" >> .env
echo "DB_POOL_TIMEOUT=30" >> .env
# Optional single DSN override
# echo "DB_CONNECTION_STRING=postgresql+asyncpg://ers_user:ers_password@localhost:5432/error_reporting" >> .env
```

### 3.3 Initialize schema (create tables)

The PostgreSQL adapter includes helpers for creating tables from the SQLAlchemy models.

```bash
python -c "
import asyncio
from src.error_reporting_service.infrastructure.config.settings import settings
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory

async def main():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    await adapter.create_tables()
    print('✅ Tables created')

asyncio.run(main())
"
```

Expected: `✅ Tables created`

### 3.4 Test connectivity via the adapter

```bash
python -c "import asyncio; \
from src.error_reporting_service.infrastructure.config.settings import settings; \
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory; \
async def test(): \
    adapter = await DatabaseAdapterFactory.create(settings.database); \
    print('DB Health:', await adapter.health_check()); \
asyncio.run(test())"
```

Expected: `DB Health: True`

---

## 4) Verification (Acceptance Criteria)

### 4.1 SQL-level checks

```bash
podman exec -it rag-postgres psql -U ers_user -d error_reporting -c "SELECT current_database(), current_user;"
```

Expected: `error_reporting` and `ers_user`.

### 4.2 App sees correct settings

```bash
python -c "from src.error_reporting_service.infrastructure.config.settings import settings; \
print('Type:', settings.database.type); \
print('Host:', settings.database.host); \
print('DB:', settings.database.database)"
```

### 4.3 Basic CRUD through the adapter

```bash
python - <<'PY'
import asyncio, uuid
from datetime import datetime, timedelta
from src.error_reporting_service.infrastructure.config.settings import settings
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.domain.entities.error_report import ErrorReport, SeverityLevel, ErrorStatus

async def main():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    await adapter.create_tables()

    # Create
    er_id = uuid.uuid4()
    report = ErrorReport(
        error_id=er_id,
        job_id=uuid.uuid4(),
        speaker_id=uuid.uuid4(),
        reported_by=uuid.uuid4(),
        original_text="Ths is a smple sentence.",
        corrected_text="This is a simple sentence.",
        error_categories=["spelling"],
        severity_level=SeverityLevel.LOW,
        start_position=0,
        end_position=5,
        error_timestamp=datetime.utcnow() - timedelta(minutes=1),
        reported_at=datetime.utcnow(),
        context_notes="Typo correction",
        status=ErrorStatus.PENDING,
        metadata={"source":"local-test"}
    )
    created = await adapter.save_error_report(report)
    print("Created:", created.error_id)

    # Read
    fetched = await adapter.find_error_by_id(er_id)
    print("Fetched exists:", fetched is not None)

    # Update
    updated = await adapter.update_error_report(er_id, {"status": "processed"})
    print("Updated status:", updated.status)

    # Delete
    deleted = await adapter.delete_error_report(er_id)
    print("Deleted:", deleted)

asyncio.run(main())
PY
```

Expected output (values vary):
- `Created: <UUID>`
- `Fetched exists: True`
- `Updated status: ErrorStatus.PROCESSED`
- `Deleted: True`

If you see `relation "error_reports" does not exist`, re-run the schema creation step (3.3).

### 4.4 Optional: app startup

If your FastAPI app entrypoint (e.g., `main.py`) uses the adapters, start it:

```bash
uvicorn main:app --reload
```

Or run the broader validation available in this repo:

```bash
python validate_setup.py
```

Look for lines:
- `Database adapter created: PostgreSQLAdapter`
- `Database health check passed`

---

## 5) Architecture & Flows (Mermaid)

### 5.1 Local dev topology

```mermaid
graph TD
  Dev[Developer Machine]
  subgraph Podman
    PG[(PostgreSQL 15)]
  end
  App[FastAPI + SQLAlchemy (async) + asyncpg]

  Dev -->|podman run/psql| PG
  App -->|postgresql+asyncpg| PG
```

### 5.2 Setup flow

```mermaid
flowchart TD
  A[Create Volume or Host Folder] --> B[Run Postgres 15 Container]
  B --> C[Check Container Status]
  C --> D[Test Connection with psql]
  D --> E[Create .env with DB Settings]
  E --> F[Install Python Deps]
  F --> G[Initialize Schema (create_tables)]
  G --> H[Run Adapter Health Check]
  H --> I[CRUD Smoke Test]
```

### 5.3 Adapter CRUD sequence

```mermaid
sequenceDiagram
  participant Client
  participant FastAPI as FastAPI Layer
  participant Adapter as PostgreSQL Adapter
  participant DB as PostgreSQL 15

  Client->>FastAPI: POST /errors (payload)
  FastAPI->>Adapter: save_error_report(entity)
  Adapter->>DB: INSERT error_reports ...
  DB-->>Adapter: row inserted
  Adapter-->>FastAPI: created entity
  FastAPI-->>Client: 201 Created
```

---

## 6) Maintenance & Cleanup

- Stop container: `podman stop rag-postgres`
- Start again: `podman start rag-postgres`
- View logs: `podman logs -f rag-postgres`
- Remove container: `podman rm -f rag-postgres`
- Remove named volume (danger—deletes data): `podman volume rm pgdata_rag`

---

## 7) Environment variables (reference)

- `DB_TYPE=postgresql`
- `DB_HOST=localhost`
- `DB_PORT=5432`
- `DB_DATABASE=error_reporting`
- `DB_USERNAME=ers_user`
- `DB_PASSWORD=ers_password`
- Optional override: `DB_CONNECTION_STRING=postgresql+asyncpg://ers_user:ers_password@localhost:5432/error_reporting`
- Optional tuning: `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`

Connection URI (async): `postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`

