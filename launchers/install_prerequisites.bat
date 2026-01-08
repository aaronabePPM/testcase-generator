@echo off
REM Prerequisites Installer for Test Case Generator
REM Checks and installs Python and Azure CLI if needed

echo ========================================
echo Prerequisites Installer
echo Test Case Generator for Azure DevOps
echo ========================================
echo.
echo This script will check and install:
echo - Python 3.12
echo - Azure CLI
echo.
pause

REM Check for administrator privileges
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Not running as Administrator
    echo Some installations may require administrator privileges.
    echo Right-click this file and select "Run as Administrator" for best results.
    echo.
    echo Press any key to continue anyway, or close this window to exit...
    pause >nul
)

echo.
echo ========================================
echo Step 1: Checking Python
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is NOT installed.
    echo Installing Python 3.12...
    echo.
    
    REM Try winget first (Windows 10/11)
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo Windows Package Manager (winget) not found.
        echo.
        echo Please install Python manually:
        start https://www.python.org/downloads/
        echo Opening download page in browser...
        echo.
        echo IMPORTANT: Check "Add Python to PATH" during installation!
        pause
        goto SKIP_PYTHON
    )
    
    winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo Automatic installation failed.
        echo Opening Python download page...
        start https://www.python.org/downloads/
        echo Please install manually and check "Add Python to PATH"
        echo.
        pause
        goto SKIP_PYTHON
    )
    
    echo.
    echo Python installed successfully!
    echo.
    
    REM Refresh PATH
    echo Refreshing environment...
    call refreshenv >nul 2>&1
    
) else (
    echo Python is already installed:
    python --version
    echo ✓ Python check passed
)

:SKIP_PYTHON
echo.
echo ========================================
echo Step 2: Checking Azure CLI
echo ========================================
echo.

az --version >nul 2>&1
if errorlevel 1 (
    echo Azure CLI is NOT installed.
    echo Installing Azure CLI...
    echo.
    
    REM Try winget first
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo Windows Package Manager (winget) not found.
        echo.
        echo Please install Azure CLI manually:
        start https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
        echo Opening installation guide in browser...
        echo.
        pause
        goto SKIP_AZURE
    )
    
    winget install Microsoft.AzureCLI --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo Automatic installation failed.
        echo Opening Azure CLI installation guide...
        start https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
        echo Please install manually
        echo.
        pause
        goto SKIP_AZURE
    )
    
    echo.
    echo Azure CLI installed successfully!
    echo.
    
) else (
    echo Azure CLI is already installed:
    az version --query "\"azure-cli\"" -o tsv
    echo ✓ Azure CLI check passed
)

:SKIP_AZURE
echo.
echo ========================================
echo Installation Complete
echo ========================================
echo.

REM Verify installations
echo Verification:
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python: NOT FOUND
    echo   Please close this window and restart, or install manually
) else (
    echo ✓ Python: 
    python --version
)

az --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Azure CLI: NOT FOUND
    echo   Please close this window and restart, or install manually
) else (
    echo ✓ Azure CLI: Installed
)

echo.
echo Next Steps:
echo 1. Close this window
echo 2. Open a NEW PowerShell or Command Prompt window
echo 3. Navigate to this folder and run: start_generator.bat
echo.
echo If you installed new software, you MUST open a new terminal window
echo for the PATH changes to take effect.
echo.
pause
