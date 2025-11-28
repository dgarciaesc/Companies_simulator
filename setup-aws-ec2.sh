#!/bin/bash
# Run this script on your AWS EC2 instance to set up the environment

set -e

echo "🚀 Setting up Companies Simulator on AWS EC2..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.12
echo "🐍 Installing Python 3.12..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Install PostgreSQL
echo "🗄️ Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib libpq-dev

# Install Node.js 18
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Install Git (if not already installed)
sudo apt-get install -y git

# Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
DB_PASSWORD=${DB_PASSWORD:-changeme123}

sudo -u postgres psql << EOF
-- Drop existing database and user if they exist
DROP DATABASE IF EXISTS companies_db;
DROP USER IF EXISTS companies_user;

-- Create user and database
CREATE USER companies_user WITH PASSWORD '${DB_PASSWORD}';
CREATE DATABASE companies_db OWNER companies_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE companies_db TO companies_user;

-- Connect to database and grant schema permissions
\c companies_db
GRANT ALL ON SCHEMA public TO companies_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO companies_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO companies_user;
EOF

# Clone or update repository
echo "📥 Setting up repository..."
cd ~
if [ -d "companies_simulator" ]; then
    echo "Repository exists, updating..."
    cd companies_simulator
    git pull origin main || true
else
    echo "Cloning repository..."
    git clone https://github.com/dgarciaesc/Companies_simulator.git companies_simulator
    cd companies_simulator
fi

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt

# Create .env file
echo "⚙️ Creating .env file..."
cat > .env << EOF
DATABASE_URL=postgresql://companies_user:${DB_PASSWORD}@localhost:5432/companies_db
FLASK_ENV=production
EOF

# Setup database schema
echo "🗄️ Creating database schema..."
export PGPASSWORD="${DB_PASSWORD}"
psql -U companies_user -d companies_db -h localhost -f sql/schema.sql
unset PGPASSWORD

# Populate initial data
echo "📊 Populating initial data..."
export DATABASE_URL="postgresql://companies_user:${DB_PASSWORD}@localhost:5432/companies_db"
source .venv/bin/activate
python scripts/populate_db.py

# Build frontend
echo "🎨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Make deployment script executable
chmod +x deploy-aws.sh

# Setup systemd service for API
echo "⚙️ Setting up API service..."
sudo tee /etc/systemd/system/companies-api.service > /dev/null << EOF
[Unit]
Description=Companies Simulator API
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/companies_simulator
Environment="DATABASE_URL=postgresql://companies_user:${DB_PASSWORD}@localhost:5432/companies_db"
Environment="FLASK_ENV=production"
Environment="PYTHONPATH=/home/$USER/companies_simulator/src"
ExecStart=/home/$USER/companies_simulator/.venv/bin/python -m flask --app src.companies_simulator.api.app run --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx configuration
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/companies-simulator > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Frontend - serve built React app
    location / {
        root /home/$USER/companies_simulator/frontend/build;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # Static files
    location /static {
        alias /home/$USER/companies_simulator/frontend/build/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Images
    location /images {
        alias /home/$USER/companies_simulator/frontend/build/images;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/companies-simulator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable companies-api
sudo systemctl start companies-api
sudo systemctl enable nginx

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Service Status:"
sudo systemctl status companies-api --no-pager | head -10
echo ""
echo "🌐 Access your application:"
echo "   Public IP: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📝 Next steps for GitHub Actions:"
echo "1. Add these secrets to your GitHub repository:"
echo "   - AWS_ACCESS_KEY_ID: Your AWS access key"
echo "   - AWS_SECRET_ACCESS_KEY: Your AWS secret key"
echo "   - AWS_REGION: Your AWS region (e.g., us-east-1)"
echo "   - EC2_HOST: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "   - EC2_USER: ubuntu"
echo "   - EC2_SSH_KEY: Your EC2 private key content"
echo "   - DB_PASSWORD: ${DB_PASSWORD}"
echo ""
echo "📊 Useful commands:"
echo "   Check API status:    sudo systemctl status companies-api"
echo "   Check Nginx status:  sudo systemctl status nginx"
echo "   View API logs:       sudo journalctl -u companies-api -f"
echo "   View Nginx logs:     sudo tail -f /var/log/nginx/error.log"
echo "   Restart API:         sudo systemctl restart companies-api"
echo "   Manual deploy:       cd ~/companies_simulator && ./deploy-aws.sh"
