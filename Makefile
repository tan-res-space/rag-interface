.PHONY: db-up db-down db-restart db-logs db-init db-health db-crud-test db-net

# Configuration (override via env: e.g., DB_PORT=55432 make db-up)
PG_IMAGE ?= docker.io/library/postgres:15
PG_NAME ?= rag-postgres
PG_VOLUME ?= pgdata_rag
PG_NETWORK ?= rag-net
DB_NAME ?= error_reporting
DB_USER ?= ers_user
DB_PASSWORD ?= ers_password
DB_HOST ?= localhost
DB_PORT ?= 5432

# Bring up PostgreSQL with Podman and a named volume for persistence
 db-up:
	@echo "[db-up] Creating volume (if missing): $(PG_VOLUME)"
	-@podman volume create $(PG_VOLUME) >/dev/null 2>&1 || true
	@echo "[db-up] Starting PostgreSQL container: $(PG_NAME) on port $(DB_PORT)"
	-@podman rm -f $(PG_NAME) >/dev/null 2>&1 || true
	podman run -d \
		--name $(PG_NAME) \
		-e POSTGRES_DB=$(DB_NAME) \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-p $(DB_PORT):5432 \
		-v $(PG_VOLUME):/var/lib/postgresql/data \
		$(PG_IMAGE)
	@echo "[db-up] Waiting for Postgres to accept connections..."
	@sleep 3
	@podman logs --tail=50 $(PG_NAME) || true

# Stop and remove the PostgreSQL container (data persists in volume)
 db-down:
	@echo "[db-down] Stopping container: $(PG_NAME)"
	-@podman stop $(PG_NAME) >/dev/null 2>&1 || true
	@echo "[db-down] Removing container: $(PG_NAME)"
	-@podman rm $(PG_NAME) >/dev/null 2>&1 || true

# Restart database container
 db-restart: db-down db-up

# Tail logs
 db-logs:
	podman logs -f $(PG_NAME)
# Create a user-defined Podman network for container-to-container connectivity
 db-net:
	@echo "[db-net] Creating network: $(PG_NETWORK)"
	-@podman network create $(PG_NETWORK) >/dev/null 2>&1 || true
	@echo "[db-net] Done. Launch Postgres with: \n  podman run -d --name $(PG_NAME) --network $(PG_NETWORK) ... $(PG_IMAGE)"



# Initialize schema (create tables) via app adapter
 db-init:
	@echo "[db-init] Creating tables in $(DB_NAME)"
	python -c "import asyncio; \
from src.error_reporting_service.infrastructure.config.settings import settings; \
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory; \
async def main(): \
    adapter = await DatabaseAdapterFactory.create(settings.database); \
    await adapter.create_tables(); \
    print('✅ Tables created'); \
asyncio.run(main())"

# App-level DB health check via adapter
 db-health:
	python -c "import asyncio; \
from src.error_reporting_service.infrastructure.config.settings import settings; \
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory; \
async def test(): \
    adapter = await DatabaseAdapterFactory.create(settings.database); \
    print('DB Health:', await adapter.health_check()); \
asyncio.run(test())"

# CRUD smoke test through the adapter
db-crud-test:
	python - <<'PY'
import asyncio, uuid
from datetime import datetime, timedelta
from src.error_reporting_service.infrastructure.config.settings import settings
from src.error_reporting_service.infrastructure.adapters.database.factory import DatabaseAdapterFactory
from src.error_reporting_service.domain.entities.error_report import ErrorReport, SeverityLevel, ErrorStatus

async def main():
    adapter = await DatabaseAdapterFactory.create(settings.database)
    await adapter.create_tables()

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
        metadata={"source":"make-crud-test"}
    )
    created = await adapter.save_error_report(report)
    print("Created:", created.error_id)

    fetched = await adapter.find_error_by_id(er_id)
    print("Fetched exists:", fetched is not None)

    updated = await adapter.update_error_report(er_id, {"status": "processed"})
    print("Updated status:", updated.status)

    deleted = await adapter.delete_error_report(er_id)
    print("Deleted:", deleted)

asyncio.run(main())
PY

