#!/bin/bash
# Add swap space to EC2 instance to prevent out-of-memory during builds

echo "🔧 Adding swap space..."

# Check if swap already exists
if [ -f /swapfile ]; then
    echo "Swap file already exists"
    sudo swapon --show
    exit 0
fi

# Create 2GB swap file
echo "Creating 2GB swap file..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
echo "✅ Swap space added:"
sudo swapon --show
free -h
