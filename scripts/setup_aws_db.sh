#!/bin/bash
# Setup and reinitialize PostgreSQL database on AWS Ubuntu instance
# Usage: ./scripts/setup_aws_db.sh

set -e  # Exit on error

echo "=== Setting up PostgreSQL Database on AWS ==="

# Load database credentials from environment or use defaults
DB_NAME="${DB_NAME:-companies_db}"
DB_USER="${DB_USER:-companies_user}"
DB_PASSWORD="${DB_PASSWORD:-secure_password}"

echo "Database: $DB_NAME"
echo "User: $DB_USER"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "ERROR: PostgreSQL is not installed"
    exit 1
fi

# Check if PostgreSQL service is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
fi

echo "Dropping existing database if exists..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" || true

echo "Dropping existing user if exists..."
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" || true

echo "Creating database user..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

echo "Creating database..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "Running schema creation..."
PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -f sql/schema.sql

echo ""
echo "=== Database setup completed successfully ==="
echo "Database URL: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
