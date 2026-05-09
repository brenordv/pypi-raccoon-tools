# Raccoon Tools DB
A managed PostgreSQL connection pool (via `psycopg 3`) with opt-in FastAPI and OpenTelemetry integrations.

[![vet OSS Components](https://github.com/brenordv/pypi-raccoon-tools/actions/workflows/raccoontools-db-vet.yml/badge.svg)](https://github.com/brenordv/pypi-raccoon-tools/actions/workflows/raccoontools-db-vet.yml)

# Installation

**Base install:**
```bash
uv add raccoontools-db
```

**With OpenTelemetry instrumentation:**
```bash
uv add raccoontools-db[otel]
```

**With FastAPI OTEL instrumentation:**
```bash
uv add raccoontools-db[fastapi]
```

**All extras:**
```bash
uv add raccoontools-db[all]
```

# Functionalities

## Connection Pool (`raccoontools_db.pool`)

Provides a module-level singleton connection pool with a simple create/get/close lifecycle.

### `PoolConfig`
Configuration dataclass for the connection pool.

**Fields:**
- `conn_info` *(str)*: PostgreSQL connection string.
- `min_size` *(int)*: Minimum connections in pool (default: 2).
- `max_size` *(int)*: Maximum connections in pool (default: 10).
- `use_otel` *(bool)*: Enable OpenTelemetry tracing (default: False).
- `otel_service_name` *(str)*: Service name for OTEL (required when `use_otel=True`).
- `otel_exporter_endpoint` *(str)*: OTLP exporter endpoint (required when `use_otel=True`).
- `otel_use_http` *(bool)*: Use HTTP protocol for OTLP (default: True).

### `create_pool(config: PoolConfig) -> None`
Creates and opens the global connection pool. Raises `RuntimeError` if a pool already exists.

### `get_pool() -> ConnectionPool`
Returns the active pool. Raises `RuntimeError` if the pool has not been created.

### `close_pool() -> None`
Closes the pool and resets state. Safe to call if already closed or never created.

### Example: Plain usage (no FastAPI, no OTEL)
```python
from raccoontools_db.pool import PoolConfig, create_pool, get_pool, close_pool

config = PoolConfig(conn_info="postgresql://user:pass@localhost:5432/mydb")
create_pool(config)

pool = get_pool()
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print(cur.fetchone())

close_pool()
```

### Example: With OpenTelemetry
```python
from raccoontools_db.pool import PoolConfig, create_pool, get_pool, close_pool

config = PoolConfig(
    conn_info="postgresql://user:pass@localhost:5432/mydb",
    use_otel=True,
    otel_service_name="my-service",
    otel_exporter_endpoint="http://localhost:4318",
)
create_pool(config)

pool = get_pool()
# Use pool as normal — logging is handled via OTEL tracing
```

## FastAPI Integration (`raccoontools_db.fastapi`)

### `create_lifespan(config: PoolConfig)`
An async context manager that ties the pool lifecycle to FastAPI's startup/shutdown.

### Example: With FastAPI
```python
from fastapi import FastAPI
from raccoontools_db.fastapi import create_lifespan
from raccoontools_db.pool import PoolConfig, get_pool

config = PoolConfig(conn_info="postgresql://user:pass@localhost:5432/mydb")
app = FastAPI(lifespan=create_lifespan(config))

@app.get("/health")
def health():
    pool = get_pool()
    with pool.connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}
```

### Example: With FastAPI + OpenTelemetry
```python
from fastapi import FastAPI
from raccoontools_db.fastapi import create_lifespan
from raccoontools_db.pool import PoolConfig, get_pool

config = PoolConfig(
    conn_info="postgresql://user:pass@localhost:5432/mydb",
    use_otel=True,
    otel_service_name="my-service",
    otel_exporter_endpoint="http://localhost:4318",
)
app = FastAPI(lifespan=create_lifespan(config))
```

# Changelog
- [Check the changelog here.](CHANGELOG.md)
