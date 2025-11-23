# Stop and remove PostgreSQL test database container
# Usage: .\scripts\stop_test_db.ps1

param(
    [string]$ContainerName = "companies_test_db",
    [switch]$Remove
)

Write-Host "Stopping PostgreSQL test database..." -ForegroundColor Cyan

# Check if container exists
$existingContainer = docker ps -a --filter "name=^${ContainerName}$" --format "{{.Names}}"

if ($existingContainer -ne $ContainerName) {
    Write-Host "Container '$ContainerName' does not exist." -ForegroundColor Yellow
    exit 0
}

# Stop container
Write-Host "Stopping container '$ContainerName'..." -ForegroundColor Cyan
docker stop $ContainerName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Container stopped successfully." -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to stop container" -ForegroundColor Red
    exit 1
}

# Remove container if requested
if ($Remove) {
    Write-Host "Removing container '$ContainerName'..." -ForegroundColor Cyan
    docker rm $ContainerName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Container removed successfully." -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to remove container" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Container stopped but not removed. Use -Remove to delete it." -ForegroundColor Yellow
    Write-Host "To remove: .\scripts\stop_test_db.ps1 -Remove" -ForegroundColor White
}
