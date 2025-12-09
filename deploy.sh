#!/bin/bash
# Docker Build và Deploy Script

set -e

echo "🐳 Starting Docker deployment for CRM-AI-Agent..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Copy environment file
echo -e "${BLUE}📝 Step 1: Setting up environment...${NC}"
if [ ! -f .env ]; then
    cp .env.docker .env
    echo -e "${GREEN}✅ Created .env from .env.docker${NC}"
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi

# Step 2: Stop existing containers
echo -e "${BLUE}🛑 Step 2: Stopping existing containers...${NC}"
docker-compose down || true
echo -e "${GREEN}✅ Stopped containers${NC}"

# Step 3: Build images
echo -e "${BLUE}🔨 Step 3: Building Docker images...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Built images successfully${NC}"

# Step 4: Start services
echo -e "${BLUE}🚀 Step 4: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"

# Step 5: Wait for services to be healthy
echo -e "${BLUE}⏳ Step 5: Waiting for services to be healthy...${NC}"
sleep 10

# Check MySQL
echo -n "Checking MySQL... "
until docker exec crm-mysql mysqladmin ping -h localhost -u root -pcrm_admin_pass --silent 2>/dev/null; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✅${NC}"

# Check Backend
echo -n "Checking Backend... "
until curl -f http://localhost:8000/health 2>/dev/null; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✅${NC}"

# Check Frontend
echo -n "Checking Frontend... "
until curl -f http://localhost/ 2>/dev/null; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✅${NC}"

# Step 6: Show status
echo -e "${BLUE}📊 Step 6: Service Status${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📱 Access your application:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}👤 Default accounts:${NC}"
echo -e "   Admin:     ${GREEN}admin@example.com / admin123${NC}"
echo -e "   Customer:  ${GREEN}user@example.com / password123${NC}"
echo ""
echo -e "${BLUE}📚 Useful commands:${NC}"
echo -e "   View logs:     ${GREEN}docker-compose logs -f${NC}"
echo -e "   Stop:          ${GREEN}docker-compose down${NC}"
echo -e "   Restart:       ${GREEN}docker-compose restart${NC}"
echo ""
