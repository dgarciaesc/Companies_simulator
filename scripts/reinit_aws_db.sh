#!/bin/bash
# Complete database reinitialization and population for AWS Ubuntu instance
# This script drops the database, recreates it, and populates it with sample data
# Usage: ./scripts/reinit_aws_db.sh

set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  AWS Database Reinitialization"
echo "========================================"
echo ""

# Check if DB_PASSWORD is set
if [ -z "$DB_PASSWORD" ]; then
    echo "ERROR: DB_PASSWORD environment variable is not set"
    echo "Please set it before running this script:"
    echo "  export DB_PASSWORD='your_password'"
    exit 1
fi

# Export database configuration
export DB_NAME="${DB_NAME:-companies_db}"
export DB_USER="${DB_USER:-companies_user}"

echo "Configuration:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Step 1: Setup database
echo "Step 1: Setting up database..."
bash "$SCRIPT_DIR/setup_aws_db.sh"
echo ""

# Step 2: Populate database
echo "Step 2: Populating database..."
bash "$SCRIPT_DIR/populate_aws_db.sh"
echo ""

echo "========================================"
echo "  Database reinitialization complete!"
echo "========================================"
echo ""
echo "You can now:"
echo "  1. Test the API:"
echo "     curl http://localhost:8000/api/health"
echo ""
echo "  2. Restart the API service:"
echo "     sudo systemctl restart companies-api"
echo ""
echo "  3. Login with test user:"
echo "     Email: user1@test.com"
echo "     Password: password1"
