#!/bin/bash
set -e

echo "🚀 Starting deployment on AWS EC2..."

# Navigate to project directory
cd ~/companies_simulator

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt

# Install/update frontend dependencies and build
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
npm run build
cd ..

# Set up environment variables
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://companies_user:${DB_PASSWORD}@localhost:5432/companies_db
FLASK_ENV=production
EOF
fi

# Setup/migrate database schema
echo "🗄️ Setting up database schema..."
export DATABASE_URL="postgresql://companies_user:${DB_PASSWORD}@localhost:5432/companies_db"
export PGPASSWORD="${DB_PASSWORD}"
psql -U companies_user -d companies_db -h localhost -f sql/schema.sql 2>/dev/null || true
unset PGPASSWORD

# Populate database if empty
source .venv/bin/activate
python scripts/populate_db.py 2>/dev/null || echo "Database already populated"

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart companies-api
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "📊 Service status:"
sudo systemctl status companies-api --no-pager
