# Start PostgreSQL test database in Docker
# Usage: .\scripts\start_test_db.ps1

param(
    [string]$ContainerName = "companies_test_db",
    [string]$PostgresPassword = "test_password_123",
    [string]$DatabaseName = "companies_test",
    [int]$Port = 5432
)

Write-Host "Starting PostgreSQL test database in Docker..." -ForegroundColor Cyan

# Check if Docker is available
try {
    docker --version | Out-Null
} catch {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if container already exists
$existingContainer = docker ps -a --filter "name=^${ContainerName}$" --format "{{.Names}}"
Write-Host "Checking for existing container..." -ForegroundColor Cyan

if ($existingContainer -eq $ContainerName) {
    Write-Host "Container '$ContainerName' already exists." -ForegroundColor Yellow
    
    # Check if it's running
    $running = docker ps --filter "name=^${ContainerName}$" --format "{{.Names}}"
    if ($running -eq $ContainerName) {
        Write-Host "Container is already running." -ForegroundColor Green
    } else {
        Write-Host "Starting existing container..." -ForegroundColor Yellow
        docker start $ContainerName
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to start container" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "Creating new PostgreSQL container..." -ForegroundColor Cyan
    docker run --name $ContainerName `
        -e POSTGRES_USER=postgres `
        -e POSTGRES_PASSWORD=$PostgresPassword `
        -e POSTGRES_DB=$DatabaseName `
        -p ${Port}:5432 `
        -d postgres:15
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create container" -ForegroundColor Red
        exit 1
    }
}

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Cyan
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and -not $ready) {
    $attempt++
    Start-Sleep -Seconds 1
    
    # Check if PostgreSQL is accepting connections
    $result = docker exec $ContainerName pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        Write-Host "PostgreSQL is ready!" -ForegroundColor Green
    } else {
        Write-Host "." -NoNewline
    }
}

if (-not $ready) {
    Write-Host "`nERROR: PostgreSQL did not become ready in time" -ForegroundColor Red
    Write-Host "Check logs with: docker logs $ContainerName" -ForegroundColor Yellow
    exit 1
}

# Export environment variable
$dbUrl = "postgresql://postgres:${PostgresPassword}@localhost:${Port}/${DatabaseName}"
Write-Host "`nDatabase URL: $dbUrl" -ForegroundColor Green
Write-Host "`nTo use this database, run:" -ForegroundColor Cyan
Write-Host "`$env:TEST_DATABASE_URL = '$dbUrl'" -ForegroundColor White
Write-Host "`nOr to run tests directly:" -ForegroundColor Cyan
Write-Host "`$env:TEST_DATABASE_URL = '$dbUrl'; python -m pytest -q" -ForegroundColor White

Write-Host "`nTo stop the database:" -ForegroundColor Cyan
Write-Host ".\scripts\stop_test_db.ps1" -ForegroundColor White
