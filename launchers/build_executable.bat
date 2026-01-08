@echo off
REM Build standalone executable for Test Case Generator
REM This creates a single .exe file that includes Python and all dependencies

echo ========================================
echo Building Test Case Generator EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is required to build the executable
    echo Please install Python first, then run this script again
    echo.
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
echo.
pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Building executable...
echo This may take a few minutes...
echo.

REM Build the executable with options:
REM --onefile: Create a single executable file
REM --windowed: No console window (GUI only)
REM --name: Name of the executable
REM --icon: Icon file (optional, we'll skip for now)
REM --add-data: Include additional files if needed

pyinstaller --onefile --windowed --name "TestCaseGenerator" --clean app\testcase_generator.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The executable has been created in the 'dist' folder:
echo   dist\TestCaseGenerator.exe
echo.
echo File size: 
dir dist\TestCaseGenerator.exe | find "TestCaseGenerator.exe"
echo.
echo You can now:
echo 1. Copy TestCaseGenerator.exe to any location
echo 2. Double-click to run (no Python required!)
echo 3. Share with QA team members
echo.
echo NOTE: The executable still requires Azure CLI to be installed
echo       for exporting work items from Azure DevOps.
echo.
pause
