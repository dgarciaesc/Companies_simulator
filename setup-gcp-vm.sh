#!/bin/bash
# Run this script on your GCP VM to set up the environment

set -e

echo "🚀 Setting up Companies Simulator on GCP VM..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.12
echo "🐍 Installing Python 3.12..."
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Install PostgreSQL
echo "🗄️ Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Install Node.js 18
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE USER companies_user WITH PASSWORD '${DB_PASSWORD:-changeme123}';
CREATE DATABASE companies_db OWNER companies_user;
GRANT ALL PRIVILEGES ON DATABASE companies_db TO companies_user;
\c companies_db
GRANT ALL ON SCHEMA public TO companies_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO companies_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO companies_user;
EOF

# Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "companies_simulator" ]; then
    cd companies_simulator
    git pull
else
    git clone https://github.com/dgarciaesc/Companies_simulator.git companies_simulator
    cd companies_simulator
fi

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup database schema
echo "🗄️ Creating database schema..."
sudo -u postgres psql -U companies_user -d companies_db -f sql/schema.sql

# Populate initial data
echo "📊 Populating initial data..."
export DATABASE_URL="postgresql://companies_user:${DB_PASSWORD:-changeme123}@localhost:5432/companies_db"
python scripts/populate_db.py

# Build frontend
echo "🎨 Building frontend..."
cd frontend
npm ci
npm run build
cd ..

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
Environment="DATABASE_URL=postgresql://companies_user:${DB_PASSWORD:-changeme123}@localhost:5432/companies_db"
Environment="FLASK_ENV=production"
ExecStart=/home/$USER/companies_simulator/.venv/bin/python -m flask --app src.companies_simulator.api.app run --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx configuration
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/companies-simulator > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend - serve built React app
    location / {
        root /home/${USER}/companies_simulator/frontend/build;
        try_files $uri /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /home/${USER}/companies_simulator/frontend/build/static;
    }
}
EOF

# Replace ${USER} with actual username
sudo sed -i "s/\${USER}/$USER/g" /etc/nginx/sites-available/companies-simulator

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

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get VM external IP: gcloud compute instances describe <VM_NAME> --zone=<ZONE> --format='get(networkInterfaces[0].accessConfigs[0].natIP)'"
echo "2. Access application at: http://<EXTERNAL_IP>"
echo "3. Setup GitHub Actions secrets:"
echo "   - GCP_SA_KEY: Service account JSON key"
echo "   - GCP_PROJECT_ID: Your GCP project ID"
echo "   - GCP_VM_NAME: Your VM instance name"
echo "   - GCP_VM_ZONE: VM zone (e.g., us-central1-a)"
echo ""
echo "📊 Check service status:"
echo "  sudo systemctl status companies-api"
echo "  sudo systemctl status nginx"
echo ""
echo "📝 View logs:"
echo "  sudo journalctl -u companies-api -f"
echo "  sudo tail -f /var/log/nginx/error.log"
