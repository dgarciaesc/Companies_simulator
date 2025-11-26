#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to project directory
cd ~/companies_simulator

# Pull latest changes
git pull origin main

# Install/update dependencies
echo "📦 Installing Python dependencies..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install/update frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm ci
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

# Setup/migrate database
echo "🗄️ Setting up database..."
source .venv/bin/activate
python scripts/populate_db.py

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart companies-api
sudo systemctl restart nginx

echo "✅ Deployment complete!"
