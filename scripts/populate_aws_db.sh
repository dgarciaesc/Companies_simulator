#!/bin/bash
# Populate PostgreSQL database with sample data on AWS Ubuntu instance
# Usage: ./scripts/populate_aws_db.sh

set -e  # Exit on error

echo "=== Populating Database with Sample Data ==="

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load database credentials from environment or use defaults
DB_NAME="${DB_NAME:-companies_db}"
DB_USER="${DB_USER:-companies_user}"
DB_PASSWORD="${DB_PASSWORD:-secure_password}"
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

echo "Project Root: $PROJECT_ROOT"
echo "Database: $DB_NAME"

# Check if virtual environment exists, activate it
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "WARNING: Virtual environment not found"
    echo "Make sure Python dependencies are installed"
fi

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/src"
export DATABASE_URL="$DATABASE_URL"

echo "Running population script..."
cd "$PROJECT_ROOT"
python3 scripts/populate_db.py

echo ""
echo "=== Database populated successfully ==="
echo ""
echo "Sample data created:"
echo "  - Test companies"
echo "  - Test users (user1@test.com / password1, user2@test.com / password2)"
echo "  - Sample products with pricing data"
echo "  - Historical metrics"
