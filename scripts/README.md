# 🚀 Deployment Scripts

This directory contains deployment and testing scripts for the CRM-AI-Agent project.

## 📁 Files

### `deploy.ps1` (Windows PowerShell)
Full deployment script for Windows environments.

**Usage:**
```powershell
.\scripts\deploy.ps1
```

**What it does:**
1. Sets up environment (.env from .env.docker)
2. Stops existing containers
3. Builds Docker images (no cache)
4. Starts services (MySQL, Backend, Frontend)
5. Waits for health checks
6. Displays service URLs

---

### `deploy.sh` (Linux/Mac Bash)
Full deployment script for Linux/Mac environments.

**Usage:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**What it does:**
Same as `deploy.ps1` but for Unix-based systems.

---

### `test-docker.ps1` (Windows PowerShell)
Quick verification script to test Docker setup.

**Usage:**
```powershell
.\scripts\test-docker.ps1
```

**What it checks:**
1. Docker installation and version
2. Docker Compose availability
3. .env file existence
4. Migration files presence
5. Docker daemon status
6. Required images availability

---

## 🎯 Quick Start

### First Time Setup (Windows)
```powershell
# 1. Test Docker setup
.\scripts\test-docker.ps1

# 2. Deploy application
.\scripts\deploy.ps1
```

### First Time Setup (Linux/Mac)
```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Deploy application
./scripts/deploy.sh
```

---

## 📝 Notes



## Move main project to `D:\Code\Project_BigData`

This repo currently lives under:

- `D:\Bai Luan\Nam 2025 - 2026\HocKyII\CDIO_3\Project\CRM-AI-Agent`

To relocate the **main project** to:

- `D:\Code\Project_BigData`

Use:

```powershell
cd "D:\Bai Luan\Nam 2025 - 2026\HocKyII\CDIO_3\Project\CRM-AI-Agent"

# Dry-run first
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\move-main-to-bigdata.ps1 -WhatIf -DetachClone

# Real run (copy/mirror). Add -RemoveSource if you want it to delete the old folder after copy.
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\move-main-to-bigdata.ps1 -DetachClone
```

Notes:

- The script **will not create** `D:\Code\Project_BigData`. Ensure it exists first.
- `-DetachClone` will detach the clone folder from being a git worktree (so it won't break when the main repo moves).
---

## 🔧 Manual Commands

If you prefer manual control:

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build --no-cache backend
docker-compose up -d backend
```
