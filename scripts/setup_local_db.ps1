# Setup local PostgreSQL database for testing
# Usage: .\scripts\setup_local_db.ps1

param(
    [string]$PostgresUser = "postgres",
    [string]$HostAddress = "localhost",
    [int]$Port = 5432,
    [string]$TestUser = "test",
    [string]$TestPassword = "test1234",
    [string]$DatabaseName = "companies_test"
)

Write-Host "Setting up local PostgreSQL test database..." -ForegroundColor Cyan

# Check if psql is available
try {
    psql --version | Out-Null
} catch {
    Write-Host "ERROR: psql is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Creating user '$TestUser'..." -ForegroundColor Cyan
$createUserCmd = "CREATE USER $TestUser WITH PASSWORD '$TestPassword';"
psql -U $PostgresUser -h $HostAddress -p $Port -c $createUserCmd 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "User '$TestUser' created successfully." -ForegroundColor Green
} else {
    Write-Host "User '$TestUser' may already exist or creation failed. Continuing..." -ForegroundColor Yellow
}

Write-Host "Creating database '$DatabaseName'..." -ForegroundColor Cyan
$createDbCmd = "CREATE DATABASE $DatabaseName OWNER $TestUser;"
psql -U $PostgresUser -h $HostAddress -p $Port -c $createDbCmd 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database '$DatabaseName' created successfully." -ForegroundColor Green
} else {
    Write-Host "Database '$DatabaseName' may already exist. Continuing..." -ForegroundColor Yellow
}

Write-Host "Granting privileges..." -ForegroundColor Cyan
$grantCmd = "GRANT ALL PRIVILEGES ON DATABASE $DatabaseName TO $TestUser;"
psql -U $PostgresUser -h $HostAddress -p $Port -c $grantCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Privileges granted successfully." -ForegroundColor Green
} else {
    Write-Host "WARNING: Failed to grant privileges" -ForegroundColor Yellow
}

# Test connection
Write-Host "`nTesting connection..." -ForegroundColor Cyan
$env:PGPASSWORD = $TestPassword
psql -U $TestUser -h $HostAddress -p $Port -d $DatabaseName -c "SELECT version();" | Out-Null
Remove-Item Env:\PGPASSWORD

if ($LASTEXITCODE -eq 0) {
    Write-Host "Connection test successful!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Connection test failed" -ForegroundColor Yellow
}

# Display connection string
$dbUrl = "postgresql://${TestUser}:${TestPassword}@${HostAddress}:${Port}/${DatabaseName}"
Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Database URL: $dbUrl" -ForegroundColor Cyan
Write-Host "`nTo use this database, run:" -ForegroundColor Cyan
Write-Host "`$env:TEST_DATABASE_URL = '$dbUrl'" -ForegroundColor White
Write-Host "`nOr to run tests directly:" -ForegroundColor Cyan
Write-Host "`$env:TEST_DATABASE_URL = '$dbUrl'; python -m pytest -q" -ForegroundColor White
