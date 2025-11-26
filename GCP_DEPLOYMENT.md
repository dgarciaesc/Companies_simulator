# GCP Deployment Guide

## Prerequisites

1. **GCP Account**: Create a free account at https://cloud.google.com/free
2. **GCP Project**: Create a new project in GCP Console
3. **GitHub Repository**: Your code should be in GitHub

## Step 1: Create GCP VM Instance (Free Tier)

1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to **Compute Engine > VM instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: `companies-simulator-vm`
   - **Region**: `us-central1` (Iowa) - eligible for free tier
   - **Zone**: `us-central1-a`
   - **Machine type**: `e2-micro` (0.25-2 vCPU, 1 GB memory) - **FREE TIER**
   - **Boot disk**: 
     - OS: Ubuntu 22.04 LTS
     - Size: 30 GB (free tier includes up to 30 GB)
   - **Firewall**: 
     - ✅ Allow HTTP traffic
     - ✅ Allow HTTPS traffic

5. Click **Create**

## Step 2: Set Up Service Account for GitHub Actions

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Configure:
   - **Name**: `github-actions-deploy`
   - **Description**: Service account for GitHub Actions deployment
4. Grant roles:
   - `Compute Instance Admin (v1)`
   - `Service Account User`
5. Click **Done**
6. Click on the created service account
7. Go to **Keys** tab → **Add Key** → **Create new key**
8. Choose **JSON** format
9. Download the JSON key file (keep it secure!)

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **New repository secret** and add:

```
Name: GCP_SA_KEY
Value: <paste entire contents of the JSON key file>

Name: GCP_PROJECT_ID
Value: your-gcp-project-id

Name: GCP_VM_NAME
Value: companies-simulator-vm

Name: GCP_VM_ZONE
Value: us-central1-a

Name: DB_PASSWORD
Value: <choose a strong password>
```

## Step 4: Initial VM Setup

1. Connect to your VM via SSH (in GCP Console, click **SSH** button)

2. Download and run the setup script:
```bash
# Download setup script
curl -O https://raw.githubusercontent.com/dgarciaesc/Companies_simulator/main/setup-gcp-vm.sh

# Make it executable
chmod +x setup-gcp-vm.sh

# Set database password
export DB_PASSWORD="your-strong-password"

# Run setup
./setup-gcp-vm.sh
```

3. Make deploy script executable:
```bash
cd ~/companies_simulator
chmod +x deploy.sh
```

## Step 5: Configure GitHub Actions

The `.github/workflows/deploy.yml` file is already set up. It will:
- Trigger on every push to `main` branch
- Copy files to VM via gcloud
- Run the deployment script
- Restart services

## Step 6: Test Deployment

1. Make a small change to your code
2. Commit and push to `main` branch:
```bash
git add .
git commit -m "Test deployment"
git push origin main
```

3. Go to **GitHub Actions** tab in your repository
4. Watch the deployment workflow execute

## Step 7: Access Your Application

1. Get your VM's external IP:
```bash
gcloud compute instances describe companies-simulator-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

2. Open in browser: `http://<EXTERNAL_IP>`

3. Login with test credentials:
   - Email: `user1@test.com`
   - Password: `password1`

## Monitoring & Debugging

### Check Service Status
```bash
# API service
sudo systemctl status companies-api

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

### View Logs
```bash
# API logs
sudo journalctl -u companies-api -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart API
sudo systemctl restart companies-api

# Restart Nginx
sudo systemctl restart nginx
```

### Manual Deployment
```bash
cd ~/companies_simulator
git pull origin main
./deploy.sh
```

## Cost Management (Free Tier Limits)

✅ **Always Free Resources:**
- 1 e2-micro VM instance per month
- 30 GB standard persistent disk
- 1 GB network egress per month (North America)

⚠️ **Monitor Usage:**
- Check [GCP Free Tier Usage](https://console.cloud.google.com/billing/freetier)
- Set up billing alerts

## Security Best Practices

1. **Enable automatic OS updates:**
```bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

2. **Use strong database password** (set in GitHub Secrets)

3. **Setup SSL/HTTPS** (recommended for production):
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate (requires domain)
sudo certbot --nginx -d yourdomain.com
```

4. **Restrict SSH access:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set: PasswordAuthentication no
# Restart: sudo systemctl restart sshd
```

## Troubleshooting

### Issue: Application not accessible
```bash
# Check if services are running
sudo systemctl status companies-api
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

### Issue: Database connection error
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -U companies_user -d companies_db -h localhost

# Check credentials in .env file
cat ~/companies_simulator/.env
```

### Issue: Out of memory
```bash
# Check memory usage
free -h

# Add swap space (if needed)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Updating the Application

Every push to `main` branch automatically deploys. For manual updates:

```bash
cd ~/companies_simulator
git pull origin main
./deploy.sh
```

## Backup Database

```bash
# Create backup
sudo -u postgres pg_dump companies_db > ~/backup_$(date +%Y%m%d).sql

# Restore backup
sudo -u postgres psql companies_db < ~/backup_20231124.sql
```

## Support

- **GitHub Issues**: https://github.com/dgarciaesc/Companies_simulator/issues
- **GCP Documentation**: https://cloud.google.com/docs
- **GitHub Actions Docs**: https://docs.github.com/en/actions
