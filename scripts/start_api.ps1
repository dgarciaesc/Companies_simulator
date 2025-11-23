# Start API Server
# Usage: .\scripts\start_api.ps1

param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000,
    [string]$DatabaseUrl = $env:DATABASE_URL
)

# Set working directory to project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Starting Companies Simulator API..." -ForegroundColor Cyan

# Check if DATABASE_URL is set
if (-not $DatabaseUrl) {
    Write-Host "WARNING: DATABASE_URL not set. Using default test database." -ForegroundColor Yellow
    $DatabaseUrl = "postgresql://test:test1234@localhost:5432/companies_test"
}

# Set environment variables
$env:PYTHONPATH = "$ProjectRoot\src"
$env:DATABASE_URL = $DatabaseUrl
$env:FLASK_ENV = "development"
$env:API_PORT = $Port

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "Database URL: $DatabaseUrl" -ForegroundColor Gray
Write-Host "API will start on http://localhost:$Port" -ForegroundColor Green
Write-Host ""

# Start the API
python -m companies_simulator.api.app
