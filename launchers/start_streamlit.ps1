# Quick Launcher for Streamlit Web App

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Case Generator - Web Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check Streamlit
Write-Host "Checking Streamlit installation..." -ForegroundColor Yellow
python -c "import streamlit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Streamlit not found. Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements-streamlit.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host ""
Write-Host "The app will open in your default browser at:" -ForegroundColor Cyan
Write-Host "http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

streamlit run app\streamlit_app.py
