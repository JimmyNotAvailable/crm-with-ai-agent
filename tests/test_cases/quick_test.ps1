# Quick Test Runner for CRM-AI-Agent
# Chạy nhanh các test cases

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRM-AI-Agent Quick Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "D:\Bai Luan\Nam 2025 - 2026\HocKyII\CDIO_3\Project\CRM-AI-Agent"
$python = "$projectRoot\.venv\Scripts\python.exe"
$testDir = "$projectRoot\tests\test_cases"

# Check if venv exists
if (-Not (Test-Path $python)) {
    Write-Host "ERROR: Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Python: $python" -ForegroundColor Green
Write-Host "Test Directory: $testDir" -ForegroundColor Green
Write-Host ""

# Menu
Write-Host "Select test to run:" -ForegroundColor Yellow
Write-Host "1. Test Case 1: Database Connectivity" -ForegroundColor White
Write-Host "2. Test Case 2: AI Integration" -ForegroundColor White
Write-Host "3. Test Case 3: Backend Endpoints" -ForegroundColor White
Write-Host "4. Run All Tests" -ForegroundColor White
Write-Host "5. View Test Report" -ForegroundColor White
Write-Host "0. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (0-5)"

switch ($choice) {
    "1" {
        Write-Host "`nRunning Test Case 1: Database Connectivity..." -ForegroundColor Cyan
        & $python "$testDir\test_case_1_database.py"
    }
    "2" {
        Write-Host "`nRunning Test Case 2: AI Integration..." -ForegroundColor Cyan
        & $python "$testDir\test_case_2_ai_integration.py"
    }
    "3" {
        Write-Host "`nRunning Test Case 3: Backend Endpoints..." -ForegroundColor Cyan
        Write-Host "NOTE: Backend must be running on http://localhost:8000" -ForegroundColor Yellow
        $confirm = Read-Host "Is backend running? (y/n)"
        if ($confirm -eq "y") {
            & $python "$testDir\test_case_3_backend_endpoints.py"
        } else {
            Write-Host "Start backend first: python -m backend.main" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host "`nRunning All Tests..." -ForegroundColor Cyan
        & $python "$testDir\run_all_tests.py"
    }
    "5" {
        $reportFile = "$testDir\TEST_REPORT.md"
        if (Test-Path $reportFile) {
            Write-Host "`nOpening test report..." -ForegroundColor Cyan
            code $reportFile
        } else {
            Write-Host "Test report not found. Run tests first." -ForegroundColor Yellow
        }
    }
    "0" {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test completed. Check results in:" -ForegroundColor Cyan
Write-Host "$testDir\results\" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
