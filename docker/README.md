# 🐳 Docker Configuration Files

This directory contains all Docker-related configuration files for CRM-AI-Agent.

## 📁 Directory Structure

```
docker/
├── docker-compose.yml         # Unified Docker Compose (all profiles)
├── Dockerfile.backend         # Backend Dockerfile (prod/dev modes)
├── Dockerfile.database        # MySQL Dockerfile with UTF-8 config
├── Dockerfile.frontend        # Frontend Dockerfile (React + Nginx)
├── nginx.conf                 # Nginx configuration for frontend
├── mysql/
│   └── utf8.cnf               # MySQL UTF-8 configuration
└── README.md                  # This file
```

## 🚀 Quick Start

### Full-stack deployment (Backend + Frontend + MySQL)
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### Database only (Development)
```bash
docker-compose -f docker/docker-compose.yml --profile database up -d
```

### Microservices databases (7 MySQL instances)
```bash
docker-compose -f docker/docker-compose.yml --profile microservices up -d
```

### All services
```bash
docker-compose -f docker/docker-compose.yml --profile all up -d
```

---

## 📁 Dockerfiles

### `Dockerfile.backend` (Unified Backend)
Multi-stage Dockerfile supporting both production and development modes.

**Base Image:** `python:3.11-slim`

**Features:**
- Multi-stage build (production/development)
- Uses `backend/requirements-frozen.txt` for reproducible builds
- Includes `ai_modules/` for AI functionality
- Health check on `/health` endpoint
- Runs on port 8000

**Build Commands:**
```bash
# Production (default)
docker build -f docker/Dockerfile.backend -t crm-backend .

# Development
docker build -f docker/Dockerfile.backend --build-arg BUILD_MODE=dev -t crm-backend-dev .
```

---

### `Dockerfile.database` (MySQL with CRM Schema)
Custom MySQL image with UTF-8 support and initialization scripts.

**Base Image:** `mysql:8.0`

**Features:**
- Full UTF-8/UTF8MB4 support for Vietnamese
- Pre-loaded CRM schema from `backend/database/full_schema.sql`
- Seed data from `scripts/init_crm_database.sql`
- Custom MySQL configuration in `mysql/utf8.cnf`
- Timezone set to Vietnam (UTC+7)

**Build Command:**
```bash
docker build -f docker/Dockerfile.database -t crm-mysql .
```

**DataGrip Connection:**
- Host: `localhost`
- Port: `3307`
- Database: `crm_ai_db`
- User: `crm_user`
- Password: `crm_admin_pass`

---

### `Dockerfile.frontend` (Production)
Frontend Dockerfile for React + Vite application.

**Build Stage:**
- Uses Node.js to build production bundle
- Installs dependencies with `npm install`
- Builds optimized static files

**Production Stage:**
- Uses nginx to serve static files
- Custom nginx configuration
- Lightweight final image

**Build Command:**
```bash
docker build -f docker/Dockerfile.frontend -t crm-frontend .
```

---

## 🎯 Usage with docker-compose

The `docker-compose.yml` in the root directory references these Dockerfiles:

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
  
  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
```

**Build all services:**
```bash
docker-compose build
```

**Build specific service:**
```bash
docker-compose build backend
```

---

## 📝 Which Dockerfile to Use?

| Scenario | Dockerfile | Build Arg | Command |
|----------|-----------|-----------|---------|
| Production deployment | `Dockerfile.backend` | (default) | `docker-compose build` |
| Development mode | `Dockerfile.backend` | `BUILD_MODE=dev` | See below |
| Database setup | `Dockerfile.database` | - | Auto-init schema |
| CI/CD pipelines | `Dockerfile.backend` | - | Recommended |

---

## 🔧 Customization

### Switch to Development Build
Edit `docker-compose.yml`:
```yaml
backend:
  build:
    dockerfile: docker/Dockerfile.backend
    args:
      BUILD_MODE: dev  # Change to dev mode
```

### Add New Dockerfile
1. Create `docker/Dockerfile.newname`
2. Update `docker-compose.yml` to reference it
3. Build: `docker-compose build servicename`

---

## 📦 Dependencies

All Dockerfiles expect:
- `backend/` directory with Python code
- `ai_modules/` directory with AI modules
- `frontend/` directory with React code
- `.env` file for environment variables
- `docker/nginx.conf` for frontend
- `docker/mysql/utf8.cnf` for MySQL configuration

---

## 🔗 Profiles Explained

| Profile | Services | Use Case |
|---------|----------|----------|
| (default) | mysql, backend, frontend, adminer | Full-stack production |
| `database` | mysql, adminer | Database development only |
| `microservices` | 7 MySQL instances, adminer | Microservices architecture |
| `all` | All services | Complete environment |

---

## 📊 Port Mappings

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 80 | React app via Nginx |
| Backend | 8000 | FastAPI server |
| MySQL (mono) | 3307 | Single database mode |
| Adminer | 8080 | Database admin UI |
| mysql-identity | 3310 | Identity microservice |
| mysql-product | 3311 | Product microservice |
| mysql-order | 3312 | Order microservice |
| mysql-support | 3313 | Support microservice |
| mysql-knowledge | 3314 | Knowledge microservice |
| mysql-analytics | 3315 | Analytics microservice |
| mysql-marketing | 3316 | Marketing microservice |
| Adminer (micro) | 8081 | Microservices DB admin |

---

## 🔌 DataGrip Configuration

Để kết nối DataGrip với MySQL trong Docker:

### Single Database Mode (Port 3307)
```
Host: localhost
Port: 3307
Database: crm_ai_db
User: crm_user
Password: crm_admin_pass
```

### Microservices Mode (Ports 3310-3316)
| Database | Port | User | Password |
|----------|------|------|----------|
| crm_identity_db | 3310 | identity_user | identity_pass |
| crm_product_db | 3311 | product_user | product_pass |
| crm_order_db | 3312 | order_user | order_pass |
| crm_support_db | 3313 | support_user | support_pass |
| crm_knowledge_db | 3314 | knowledge_user | knowledge_pass |
| crm_analytics_db | 3315 | analytics_user | analytics_pass |
| crm_marketing_db | 3316 | marketing_user | marketing_pass |

**Lưu ý:** Các volume data được persist, không bị mất khi restart container.

