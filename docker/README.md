# 🐳 Docker Configuration Files

This directory contains Dockerfile configurations for building Docker images.

## 📁 Files

### `Dockerfile.backend` (Production)
Production-ready backend Dockerfile using frozen dependencies.

**Base Image:** `python:3.11-slim`

**Features:**
- Uses `backend/requirements-frozen.txt` for reproducible builds
- Installs system dependencies (gcc, g++, mysql client)
- Optimized layer caching
- Health check on `/health` endpoint
- Runs on port 8000

**Build Command:**
```bash
docker build -f docker/Dockerfile.backend -t crm-backend .
```

---

### `Dockerfile.backend.local` (Development)
Development Dockerfile that copies from local Python virtual environment.

**Base Image:** `python:3.11-slim`

**Features:**
- Copies packages from local `backend/venv/`
- Faster builds (no pip install)
- Minimal system dependencies
- Use only for local development

**Build Command:**
```bash
docker build -f docker/Dockerfile.backend.local -t crm-backend-local .
```

**⚠️ Warning:** Requires local venv with installed packages.

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

| Scenario | Dockerfile | Command |
|----------|-----------|---------|
| Production deployment | `Dockerfile.backend` | `docker-compose build` |
| Local development (fast builds) | `Dockerfile.backend.local` | Change docker-compose.yml |
| CI/CD pipelines | `Dockerfile.backend` | Recommended |
| Testing | `Dockerfile.backend` | Use DEMO_MODE=True |

---

## 🔧 Customization

### Switch to Local Dockerfile
Edit `docker-compose.yml`:
```yaml
backend:
  build:
    dockerfile: docker/Dockerfile.backend.local  # Change this
```

### Add New Dockerfile
1. Create `docker/Dockerfile.newname`
2. Update `docker-compose.yml` to reference it
3. Build: `docker-compose build servicename`

---

## 📦 Dependencies

All Dockerfiles expect:
- `backend/` directory with Python code
- `frontend/` directory with React code
- `.env` file for environment variables
- `nginx.conf` for frontend (root directory)

See root `docker-compose.yml` for volume mounts and environment variables.
