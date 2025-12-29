# Test Docker Setup and Database
# Quick verification script

Write-Host "🔍 Testing Docker Setup for CRM-AI-Agent..." -ForegroundColor Cyan

# Step 1: Check if Docker is running
Write-Host "`n📌 Step 1: Checking Docker..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not running!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and start it." -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if docker-compose is available
Write-Host "`n📌 Step 2: Checking Docker Compose..." -ForegroundColor Blue
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available!" -ForegroundColor Red
    exit 1
}

# Step 3: Check if .env file exists
Write-Host "`n📌 Step 3: Checking environment file..." -ForegroundColor Blue
if (Test-Path .env) {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found, creating from template..." -ForegroundColor Yellow
    Copy-Item .env.docker .env
    Write-Host "✅ Created .env from .env.docker" -ForegroundColor Green
}

# Step 4: Check migration files
Write-Host "`n📌 Step 4: Checking migration files..." -ForegroundColor Blue
$migrationFiles = @(
    "backend\migrations\01_create_schema.sql",
    "backend\migrations\02_insert_sample_data.sql"
)

$allMigrationsExist = $true
foreach ($file in $migrationFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
        $allMigrationsExist = $false
    }
}

if (-not $allMigrationsExist) {
    Write-Host "❌ Some migration files are missing!" -ForegroundColor Red
    exit 1
}

# Step 5: Check if ports are available
Write-Host "`n📌 Step 5: Checking port availability..." -ForegroundColor Blue
$ports = @(80, 8000, 3306)
$portsInUse = @()

foreach ($port in $ports) {
    $connection = netstat -ano | Select-String ":$port " | Select-String "LISTENING"
    if ($connection) {
        $portsInUse += $port
        Write-Host "  ⚠️  Port $port is in use" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Port $port is available" -ForegroundColor Green
    }
}

if ($portsInUse.Count -gt 0) {
    Write-Host "`n⚠️  Warning: Some ports are already in use: $($portsInUse -join ', ')" -ForegroundColor Yellow
    Write-Host "Docker Compose will try to stop existing containers..." -ForegroundColor Yellow
}

# Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ Pre-flight check completed!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green

Write-Host "`n📋 Next steps:" -ForegroundColor Blue
Write-Host "   1. Run deploy script: deploy.ps1" -ForegroundColor Green
Write-Host "   2. Or manually: docker-compose up -d" -ForegroundColor Green
Write-Host ""

# Ask if user wants to proceed with deployment
$response = Read-Host "Do you want to proceed with deployment now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`nStarting deployment..." -ForegroundColor Cyan
    & ".\deploy.ps1"
} else {
    Write-Host "`nDeployment cancelled. Run deploy.ps1 when ready." -ForegroundColor Yellow
}
