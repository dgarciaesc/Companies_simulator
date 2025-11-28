#!/bin/bash
# Quick fix for Nginx redirect loop issue on AWS
# Run this on the EC2 server to fix the configuration

set -e

echo "🔧 Fixing Nginx configuration..."

# Backup current config
sudo cp /etc/nginx/sites-available/companies-simulator /etc/nginx/sites-available/companies-simulator.backup

# Fix the try_files directive
sudo sed -i 's/try_files $uri \/index.html;/try_files $uri $uri\/ \/index.html;/' /etc/nginx/sites-available/companies-simulator

echo "✅ Configuration updated"

# Test configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo "✅ Nginx fixed and reloaded successfully!"
echo ""
echo "You can now access your site at:"
echo "http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'your-ec2-ip')"
