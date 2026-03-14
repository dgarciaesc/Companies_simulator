Companies Simulator (Local)

Proyecto Python + Flask + React con PostgreSQL para simular compañías, productos y métricas.

## Requisitos (macOS local)

- Python 3.10+
- Node.js 16+
- PostgreSQL 16+ con `psql` disponible

## Instalación

### 1) Backend

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
```

### 2) Frontend

```bash
cd frontend
npm install
```

Si hay error SSL con npm en este equipo:

```bash
npm install --strict-ssl=false
```

## Base de datos local

1. Inicia PostgreSQL (si usas Homebrew):

```bash
brew services start postgresql@16
```

2. Crea usuario y base de datos:

```bash
if ! psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='test'" | grep -q 1; then psql -d postgres -c "CREATE ROLE test LOGIN PASSWORD 'test1234';"; fi
if ! psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='companies_test'" | grep -q 1; then createdb companies_test -O test; fi
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE companies_test TO test;"
```

3. Carga esquema y datos:

```bash
psql "postgresql://test:test1234@localhost:5432/companies_test" -f sql/schema.sql
DATABASE_URL='postgresql://test:test1234@localhost:5432/companies_test' ./.venv/bin/python scripts/populate_db.py
```

## Ejecutar localmente

### API (terminal 1)

```bash
DATABASE_URL='postgresql://test:test1234@localhost:5432/companies_test' ./.venv/bin/python -m companies_simulator.api.app
```

API: http://localhost:8000

### Frontend (terminal 2)

```bash
cd frontend
npm start
```

Frontend: http://localhost:3000

## Endpoints principales

Base URL: `http://localhost:8000/api`

- `GET /health`
- `GET /companies`
- `GET /companies/:id`
- `GET /companies/:id/products`
- `GET /products/:id/metrics`

## Tests

```bash
TEST_DATABASE_URL='postgresql://test:test1234@localhost:5432/companies_test' ./.venv/bin/python -m pytest -q
```

## Credenciales de ejemplo

- `user1@test.com` / `password1`
- `user2@test.com` / `password2`
- `admin@test.com` / `admin123`
