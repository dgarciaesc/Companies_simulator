Companies Simulator (Hexagonal Architecture)

Proyecto de ejemplo en Python con arquitectura hexagonal para acceder a una base de datos Postgres, con API REST y frontend React.

## Arquitectura

- **Domain**: Modelos y puertos (interfaces)
- **Adapters**: Implementación de repositorios (PostgreSQL)
- **Services**: Lógica de negocio
- **API**: REST API con Flask
- **Frontend**: Aplicación React con diseño tipo Polymarket

## Requisitos

- Python 3.10+
- PostgreSQL
- Node.js 16+ (para el frontend)

## Instalación

### Backend

```powershell
# Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Si hay problemas de permisos
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Instalar el paquete en modo editable
python -m pip install -e .
```

### Frontend

```powershell
cd frontend
npm install
```

## Configuración de Base de Datos

### Opción 1: Crear usuario y base de datos local

Usa el script automatizado:

```powershell
.\scripts\setup_local_db.ps1
```

Esto crea:
- Usuario: `test` con contraseña `test1234`
- Base de datos: `companies_test`

### Opción 2: Crear manualmente

```powershell
psql -U postgres -h localhost -c "CREATE USER test WITH PASSWORD 'test1234';"
psql -U postgres -h localhost -c "CREATE DATABASE companies_test OWNER test;"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE companies_test TO test;"
```

## Scripts Disponibles

### `scripts/setup_local_db.ps1`
Crea automáticamente el usuario y la base de datos de pruebas en PostgreSQL local.

```powershell
.\scripts\setup_local_db.ps1
```

### `scripts/start_test_db.ps1`
Inicia un contenedor Docker con PostgreSQL para pruebas (requiere Docker Desktop).

```powershell
.\scripts\start_test_db.ps1
```

### `scripts/stop_test_db.ps1`
Detiene el contenedor Docker de PostgreSQL.

```powershell
.\scripts\stop_test_db.ps1
# O para eliminarlo completamente
.\scripts\stop_test_db.ps1 -Remove
```

### `scripts/start_api.ps1`
Inicia el servidor API Flask con configuración automática.

```powershell
.\scripts\start_api.ps1
# O con parámetros personalizados
.\scripts\start_api.ps1 -Port 8000 -DatabaseUrl "postgresql://test:test1234@localhost:5432/companies_test"
```

## Uso

### 1. Iniciar el Backend (API)

```powershell
# Opción A: Usar el script (recomendado)
.\scripts\start_api.ps1

# Opción B: Manual
$env:DATABASE_URL = 'postgresql://test:test1234@localhost:5432/companies_test'
python -m companies_simulator.api.app
```

El API estará disponible en **http://localhost:8000**

### 2. Iniciar el Frontend

En otra terminal:

```powershell
cd frontend
npm start
```

El frontend se abrirá automáticamente en **http://localhost:3000**

### 3. Usar la Aplicación

1. El frontend mostrará una lista de compañías en el sidebar
2. Selecciona una compañía para ver sus productos
3. Visualiza las métricas actuales (market share y revenue)
4. Explora los gráficos históricos con el toggle Revenue/Market Share

## Variables de Entorno

- `DATABASE_URL`: Cadena de conexión PostgreSQL (ej: `postgresql://user:pass@localhost:5432/dbname`)
- `TEST_DATABASE_URL`: URL para tests (puede ser la misma que DATABASE_URL)
- `FLASK_ENV`: Entorno de Flask (`development` o `production`)
- `API_PORT`: Puerto del API (por defecto: 8000)

Ejemplo:

```powershell
$env:DATABASE_URL = 'postgresql://test:test1234@localhost:5432/companies_test'
$env:FLASK_ENV = 'development'
```

## API REST Endpoints

Base URL: `http://localhost:8000/api`

- `GET /companies` - Listar todas las compañías
- `GET /companies/:id` - Obtener una compañía específica
- `GET /companies/:id/products` - Obtener productos de una compañía
- `GET /products/:id/metrics` - Obtener métricas anuales históricas de un producto
- `GET /products/:id/metrics/:year` - Obtener métricas de un producto para un año específico
- `GET /health` - Health check del servicio

Ejemplo de uso:
```powershell
# Listar compañías
curl http://localhost:8000/api/companies

# Obtener productos de la compañía 1
curl http://localhost:8000/api/companies/1/products

# Obtener métricas históricas del producto 1
curl http://localhost:8000/api/products/1/metrics
```

## Frontend

El proyecto incluye un frontend React con diseño inspirado en Polymarket.

### Características

- **Header**: Muestra el nombre de la compañía seleccionada en la parte superior izquierda con navegación
- **Sidebar**: Selector de compañías para cambiar entre diferentes empresas
- **Lista de Productos**: Tarjetas mostrando:
  - Nombre del producto y SKU
  - Market share actual (%)
  - Revenue actual ($)
- **Gráficos Históricos**: Visualización interactiva con:
  - Líneas de tiempo para revenue y market share
  - Toggle para cambiar entre métricas
  - Múltiples productos con colores distintos
  - Datos anuales desde 2021 hasta 2023+

### Estructura del Frontend

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.js/css          # Encabezado con logo y navegación
│   │   ├── CompanySelector.js/css # Sidebar de selección de compañías
│   │   ├── ProductsList.js/css    # Tarjetas de productos con métricas
│   │   └── HistoricalChart.js/css # Gráfico de líneas con Recharts
│   ├── api.js                     # Cliente API con fallbacks mock
│   └── App.js                     # Componente principal
└── package.json
```

### Tecnologías del Frontend

- React 18
- Recharts (gráficos)
- Axios (HTTP client)
- CSS modular con diseño responsive

## Tests

El proyecto incluye tests de integración con la base de datos en `tests/test_db.py`.

### Ejecutar tests con Docker (recomendado)

1. Arranca un contenedor PostgreSQL de prueba:
```powershell
.\scripts\start_test_db.ps1
```

2. Exporta la variable de entorno y ejecuta los tests:
```powershell
$env:TEST_DATABASE_URL = 'postgresql://postgres:test_password_123@localhost:5432/companies_test'
python -m pytest -q
```

3. Para detener el contenedor:
```powershell
.\scripts\stop_test_db.ps1
```

Para eliminar el contenedor completamente:
```powershell
.\scripts\stop_test_db.ps1 -Remove
```

### Ejecutar tests con PostgreSQL local

Si ya tienes PostgreSQL instalado:

1. Crea el usuario y la base de datos de prueba (ejecuta el script una vez):
```powershell
.\scripts\setup_local_db.ps1
```

Esto creará:
- Usuario: `test` con contraseña `test1234`
- Base de datos: `companies_test`

2. Exporta la URL y ejecuta los tests:
```powershell
$env:TEST_DATABASE_URL = 'postgresql://test:test1234@localhost:5432/companies_test'
python -m pytest -q
```

**Creación manual (alternativa):**
```powershell
psql -U postgres -h localhost -c "CREATE USER test WITH PASSWORD 'test1234';"
psql -U postgres -h localhost -c "CREATE DATABASE companies_test OWNER test;"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE companies_test TO test;"
```

### Depurar tests en VS Code

Usa la configuración de depuración **"Python: Debug Pytest (module)"** desde la paleta de comandos (F5). El `launch.json` ya está configurado con `PYTHONPATH` correcto.

## Estructura del Proyecto

```
Companies_simulator/
├── src/
│   └── companies_simulator/
│       ├── domain/              # Modelos y puertos (interfaces)
│       │   ├── models.py        # Company, Product, PricingState, AnnualMetrics
│       │   └── ports.py         # RepositoryPort interface
│       ├── adapters/            # Implementaciones de infraestructura
│       │   └── postgres_repository.py
│       ├── services/            # Lógica de negocio
│       │   ├── pricing_service.py
│       │   └── company_service.py
│       └── api/                 # REST API con Flask
│           └── app.py
├── frontend/                    # Aplicación React
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   └── App.js
│   └── package.json
├── tests/                       # Tests de integración
│   ├── conftest.py
│   └── test_db.py
├── scripts/                     # Scripts de utilidad
│   ├── setup_local_db.ps1
│   ├── start_test_db.ps1
│   ├── stop_test_db.ps1
│   └── start_api.ps1
├── sql/
│   └── schema.sql              # Esquema de base de datos
├── pyproject.toml              # Configuración del paquete Python
└── README.md
```

## Flujo de Trabajo Típico

1. **Configurar entorno**:
   ```powershell
   python -m pip install -e .
   .\scripts\setup_local_db.ps1
   ```

2. **Ejecutar tests**:
   ```powershell
   $env:TEST_DATABASE_URL = 'postgresql://test:test1234@localhost:5432/companies_test'
   python -m pytest -q
   ```

3. **Iniciar backend**:
   ```powershell
   .\scripts\start_api.ps1
   ```

4. **Iniciar frontend** (en otra terminal):
   ```powershell
   cd frontend
   npm start
   ```

5. **Acceder a la aplicación**: http://localhost:3000

## Solución de Problemas

### Error: "No module named 'companies_simulator'"
Asegúrate de haber instalado el paquete: `python -m pip install -e .`

### Error de conexión a la base de datos
Verifica que PostgreSQL esté corriendo y que `DATABASE_URL` sea correcta.

### Frontend no se conecta al backend
- Verifica que el API esté corriendo en http://localhost:8000
- Revisa la consola del navegador para errores CORS
- Asegúrate de que Flask-CORS esté instalado

### Tests fallan
- Verifica que `TEST_DATABASE_URL` esté configurada
- Asegúrate de que el usuario `test` tenga permisos en la base de datos
- Ejecuta el script de configuración: `.\scripts\setup_local_db.ps1`
