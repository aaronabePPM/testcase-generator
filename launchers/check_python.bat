@echo off
REM Python Installation Diagnostic Tool
REM This window will stay open so you can read the results

echo ========================================
echo Python Installation Diagnostic
echo ========================================
echo.

echo Checking for Python installations...
echo.

REM Check standard python command
echo [1] Checking 'python' command:
python --version 2>nul
if not errorlevel 1 (
    echo    ✓ Found: python
    python --version
    where python
) else (
    echo    ✗ 'python' command not found
)
echo.

REM Check python3 command
echo [2] Checking 'python3' command:
python3 --version 2>nul
if not errorlevel 1 (
    echo    ✓ Found: python3
    python3 --version
    where python3
) else (
    echo    ✗ 'python3' command not found
)
echo.

REM Check py launcher (Windows Python Launcher)
echo [3] Checking 'py' launcher:
py --version 2>nul
if not errorlevel 1 (
    echo    ✓ Found: py launcher
    py --version
    where py
    echo.
    echo    Available Python versions via 'py':
    py --list 2>nul
) else (
    echo    ✗ 'py' launcher not found
)
echo.

REM Check common installation paths
echo [4] Checking common installation paths:
echo.

if exist "%LOCALAPPDATA%\Programs\Python" (
    echo    ✓ Found Python folder in: %LOCALAPPDATA%\Programs\Python
    dir /b "%LOCALAPPDATA%\Programs\Python"
) else (
    echo    ✗ Not found in: %LOCALAPPDATA%\Programs\Python
)

if exist "C:\Program Files\Python*" (
    echo    ✓ Found Python in: C:\Program Files\
    dir /b "C:\Program Files\Python*" 2>nul
) else (
    echo    ✗ Not found in: C:\Program Files\
)

if exist "%PROGRAMFILES(X86)%\Python*" (
    echo    ✓ Found Python in: %PROGRAMFILES(X86)%\
    dir /b "%PROGRAMFILES(X86)%\Python*" 2>nul
) else (
    echo    ✗ Not found in: %PROGRAMFILES(X86)%\
)

if exist "C:\Python*" (
    echo    ✓ Found Python in: C:\
    dir /b "C:\Python*" 2>nul
) else (
    echo    ✗ Not found in: C:\
)
echo.

REM Check PATH environment variable
echo [5] Checking PATH environment variable:
echo.
echo    Current PATH contains:
echo %PATH% | findstr /I "python" >nul
if not errorlevel 1 (
    echo    ✓ PATH contains Python-related entries
    echo.
    echo %PATH% | findstr /I "python"
) else (
    echo    ✗ No Python entries found in PATH
)
echo.

REM Check Microsoft Store Python
echo [6] Checking Microsoft Store Python:
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    echo    ✓ Found Microsoft Store Python stub
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version 2>nul
    if errorlevel 1 (
        echo    ⚠ This is a stub - redirects to Microsoft Store
        echo    You may need to install Python from the Store
    )
) else (
    echo    ✗ Microsoft Store Python not found
)
echo.

echo ========================================
echo Summary
echo ========================================
echo.

REM Test which command works
set PYTHON_FOUND=0

python --version >nul 2>&1
if not errorlevel 1 (
    echo ✓ RECOMMENDATION: Use 'python' command
    set PYTHON_FOUND=1
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    echo ✓ RECOMMENDATION: Use 'python3' command
    set PYTHON_FOUND=1
)

py --version >nul 2>&1
if not errorlevel 1 (
    echo ✓ RECOMMENDATION: Use 'py' command
    set PYTHON_FOUND=1
)

if %PYTHON_FOUND%==0 (
    echo.
    echo ✗ RESULT: Python is NOT accessible from command line
    echo.
    echo Possible solutions:
    echo 1. Install Python from https://www.python.org/downloads/
    echo    - Make sure to check "Add Python to PATH" during installation
    echo.
    echo 2. If Python is installed, add it to PATH manually:
    echo    - Search for "Environment Variables" in Windows
    echo    - Edit PATH and add Python installation directory
    echo.
    echo 3. Reinstall Python and check "Add Python to PATH"
    echo.
    echo 4. Use Windows Terminal or open a NEW PowerShell window
    echo    (PATH changes require a new window to take effect)
) else (
    echo.
    echo ✓ RESULT: Python is accessible!
    echo.
    echo If start_generator.bat still doesn't work, try:
    echo 1. Close this window and open a NEW Command Prompt or PowerShell
    echo 2. Navigate to this folder
    echo 3. Run start_generator.bat again
)

echo.
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
