# Docker Build và Deploy Script for Windows PowerShell

Write-Host "🐳 Starting Docker deployment for CRM-AI-Agent..." -ForegroundColor Cyan

# Step 1: Copy environment file
Write-Host "`n📝 Step 1: Setting up environment..." -ForegroundColor Blue
if (-not (Test-Path .env)) {
    Copy-Item .env.docker .env
    Write-Host "✅ Created .env from .env.docker" -ForegroundColor Green
} else {
    Write-Host "✅ .env already exists" -ForegroundColor Green
}

# Step 2: Stop existing containers
Write-Host "`n🛑 Step 2: Stopping existing containers..." -ForegroundColor Blue
try {
    docker-compose down 2>$null
} catch {
    Write-Host "No existing containers to stop" -ForegroundColor Yellow
}
Write-Host "✅ Stopped containers" -ForegroundColor Green

# Step 3: Build images
Write-Host "`n🔨 Step 3: Building Docker images..." -ForegroundColor Blue
docker-compose build --no-cache
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Built images successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build images" -ForegroundColor Red
    exit 1
}

# Step 4: Start services
Write-Host "`n🚀 Step 4: Starting services..." -ForegroundColor Blue
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Step 5: Wait for services to be healthy
Write-Host "`n⏳ Step 5: Waiting for services to be healthy..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Check MySQL
Write-Host -NoNewline "Checking MySQL... "
$retries = 30
for ($i = 0; $i -lt $retries; $i++) {
    try {
        docker exec crm-mysql mysqladmin ping -h localhost -u root -pcrm_admin_pass --silent 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅" -ForegroundColor Green
            break
        }
    } catch {}
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
}

# Check Backend
Write-Host -NoNewline "Checking Backend... "
for ($i = 0; $i -lt $retries; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅" -ForegroundColor Green
            break
        }
    } catch {}
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
}

# Check Frontend
Write-Host -NoNewline "Checking Frontend... "
for ($i = 0; $i -lt $retries; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅" -ForegroundColor Green
            break
        }
    } catch {}
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
}

# Step 6: Show status
Write-Host "`n📊 Step 6: Service Status" -ForegroundColor Blue
docker-compose ps

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green

Write-Host "`n📱 Access your application:" -ForegroundColor Blue
Write-Host "   Frontend:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost" -ForegroundColor Green
Write-Host "   Backend:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "   API Docs:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Green

Write-Host "`n👤 Default accounts:" -ForegroundColor Blue
Write-Host "   Admin:     " -NoNewline -ForegroundColor White
Write-Host "admin@example.com / admin123" -ForegroundColor Green
Write-Host "   Customer:  " -NoNewline -ForegroundColor White
Write-Host "user@example.com / password123" -ForegroundColor Green

Write-Host "`n📚 Useful commands:" -ForegroundColor Blue
Write-Host "   View logs:     " -NoNewline -ForegroundColor White
Write-Host "docker-compose logs -f" -ForegroundColor Green
Write-Host "   Stop:          " -NoNewline -ForegroundColor White
Write-Host "docker-compose down" -ForegroundColor Green
Write-Host "   Restart:       " -NoNewline -ForegroundColor White
Write-Host "docker-compose restart" -ForegroundColor Green
Write-Host ""
