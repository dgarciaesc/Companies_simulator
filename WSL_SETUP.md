# WSL Setup Guide for Companies Simulator

## Prerequisites
1. Install WSL2 with Ubuntu:
   ```powershell
   wsl --install
   ```
   Or if already installed:
   ```powershell
   wsl --install -d Ubuntu
   ```

2. Open WSL terminal (search "Ubuntu" in Windows Start menu)

## Setup Steps

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
sudo service postgresql start

# Set postgres user password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Create database user and database
sudo -u postgres psql << EOF
CREATE USER companies_user WITH PASSWORD 'changeme123';
CREATE DATABASE companies_db OWNER companies_user;
GRANT ALL PRIVILEGES ON DATABASE companies_db TO companies_user;
\q
EOF
```

### 3. Install Python 3.12
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip -y
```

### 4. Install Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
node --version  # Should show v18.x
npm --version
```

### 5. Clone/Access Your Project
If your project is in Windows:
```bash
cd /mnt/c/Users/DAGAR33/projects/Companies_simulator
```

Or clone fresh:
```bash
cd ~
git clone https://github.com/dgarciaesc/Companies_simulator.git
cd Companies_simulator
```

### 6. Setup Python Environment
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 7. Setup Database
```bash
# Apply schema
export PGPASSWORD='changeme123'
psql -U companies_user -h localhost -d companies_db -f sql/schema.sql

# Populate with test data
export DATABASE_URL='postgresql://companies_user:changeme123@localhost:5432/companies_db'
python scripts/populate_db.py
```

### 8. Setup Frontend
```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Terminal 1 - Start API
```bash
cd /mnt/c/Users/DAGAR33/projects/Companies_simulator  # or your path
source .venv/bin/activate
export DATABASE_URL='postgresql://companies_user:changeme123@localhost:5432/companies_db'
python -m companies_simulator.api.app
```

### Terminal 2 - Start Frontend
```bash
cd /mnt/c/Users/DAGAR33/projects/Companies_simulator/frontend  # or your path
npm start
```

## Auto-start PostgreSQL
PostgreSQL doesn't auto-start in WSL. Add to `~/.bashrc`:
```bash
# Auto-start PostgreSQL
if ! pgrep -x postgres > /dev/null; then
    sudo service postgresql start
fi
```

## Useful Commands

### Check PostgreSQL Status
```bash
sudo service postgresql status
```

### Start PostgreSQL
```bash
sudo service postgresql start
```

### Stop PostgreSQL
```bash
sudo service postgresql stop
```

### Access Database
```bash
export PGPASSWORD='changeme123'
psql -U companies_user -h localhost -d companies_db
```

### Reset Database
```bash
export PGPASSWORD='changeme123'
psql -U companies_user -h localhost -d companies_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U companies_user -h localhost -d companies_db -f sql/schema.sql
export DATABASE_URL='postgresql://companies_user:changeme123@localhost:5432/companies_db'
python scripts/populate_db.py
```

## Advantages of WSL
- Native Linux environment (matches AWS deployment)
- Better performance for PostgreSQL
- Simpler shell scripts (bash instead of PowerShell)
- No path encoding issues
- Same commands as production server

## Accessing from Windows
- WSL files: `\\wsl$\Ubuntu\home\<username>\Companies_simulator`
- Windows files in WSL: `/mnt/c/Users/DAGAR33/...`
- VS Code: Install "Remote - WSL" extension, open folder in WSL

## Port Access
WSL2 shares network with Windows, so:
- API on `http://localhost:8000` works from both WSL and Windows
- Frontend on `http://localhost:3000` works from both WSL and Windows
