# Reset local PostgreSQL database (companies_db)
# This will DROP and recreate the database with the latest schema

Write-Host "=== Resetting Local Database ===" -ForegroundColor Cyan
Write-Host ""

$PostgresUser = "postgres"
$DbUser = "companies_user"
$DbPassword = "0589Allez85"
$DbName = "companies_db"

# Drop database if exists
Write-Host "Dropping database '$DbName' if it exists..." -ForegroundColor Yellow
& psql -U $PostgresUser -h localhost -c "DROP DATABASE IF EXISTS $DbName;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Database dropped" -ForegroundColor Green
} else {
    Write-Host "  [!] Could not drop database (may not exist)" -ForegroundColor Yellow
}

# Drop user if exists (must be after dropping database)
Write-Host "Dropping user '$DbUser' if it exists..." -ForegroundColor Yellow
& psql -U $PostgresUser -h localhost -c "DROP USER IF EXISTS $DbUser;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] User dropped" -ForegroundColor Green
} else {
    Write-Host "  [!] Could not drop user (may not exist or may still own objects)" -ForegroundColor Yellow
}

Write-Host ""

# Create user (or skip if already exists)
Write-Host "Creating user '$DbUser'..." -ForegroundColor Cyan
$createUserOutput = & psql -U $PostgresUser -h localhost -c "CREATE USER $DbUser WITH PASSWORD '$DbPassword';" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] User created" -ForegroundColor Green
} elseif ($createUserOutput -match "already exists|ya existe") {
    Write-Host "  [OK] User already exists (using existing user)" -ForegroundColor Yellow
} else {
    Write-Host "  [ERROR] Failed to create user: $createUserOutput" -ForegroundColor Red
    exit 1
}

# Create database
Write-Host "Creating database '$DbName'..." -ForegroundColor Cyan
& psql -U $PostgresUser -h localhost -c "CREATE DATABASE $DbName OWNER $DbUser;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Database created" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to create database" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Apply schema
Write-Host "Applying schema from sql/schema.sql..." -ForegroundColor Cyan
$env:PGPASSWORD = $DbPassword
& psql -U $DbUser -h localhost -d $DbName -f sql\schema.sql
Remove-Item Env:\PGPASSWORD

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Schema applied" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to apply schema" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Populate database
Write-Host "Populating database with test data..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-Not (Test-Path ".venv")) {
    Write-Host "  [ERROR] Virtual environment not found. Please run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Activate virtual environment and run populate script
. .venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://${DbUser}:${DbPassword}@localhost:5432/${DbName}"
python scripts\populate_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Database populated" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to populate database" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Database Reset Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Database URL: postgresql://${DbUser}:${DbPassword}@localhost:5432/${DbName}" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now start the API with: .\scripts\start_api.ps1" -ForegroundColor Cyan
