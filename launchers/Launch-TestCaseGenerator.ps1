# Test Case Generator Launcher (PowerShell)
# Automatically finds Python and launches the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Case Generator for Azure DevOps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Search for Python installations
$pythonPaths = @(
    "C:\Users\Aaron\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\Aaron\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\Aaron\AppData\Local\Programs\Python\Python310\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $pythonExe = $path
        break
    }
}

if ($pythonExe) {
    Write-Host "✓ Found Python: $pythonExe" -ForegroundColor Green
    Write-Host ""
    
    # Get Python version
    $version = & $pythonExe --version 2>&1
    Write-Host "Version: $version" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Launching Test Case Generator..." -ForegroundColor Yellow
    Write-Host ""
    
    # Launch the application
    & $pythonExe "$PSScriptRoot\app\testcase_generator.py"
    
} else {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python needs to be installed. Would you like to install it now?" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[Y] Yes - Install Python using winget" -ForegroundColor White
    Write-Host "[N] No - Exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Your choice (Y/N)"
    
    if ($choice -eq "Y" -or $choice -eq "y") {
        Write-Host ""
        Write-Host "Installing Python 3.12..." -ForegroundColor Yellow
        Write-Host "This may take a few minutes..." -ForegroundColor Yellow
        Write-Host ""
        
        winget install Python.Python.3.12
        
        Write-Host ""
        Write-Host "Installation complete!" -ForegroundColor Green
        Write-Host "Please CLOSE this window and run the launcher again." -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}
