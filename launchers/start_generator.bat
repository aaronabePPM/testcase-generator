@echo off
REM Quick Start Launcher for Test Case Generator
REM Double-click this file to launch the application

echo ========================================
echo Test Case Generator for Azure DevOps
echo ========================================
echo.

REM Set default Python command
set PYTHON_CMD=

REM Check for Python - try multiple common commands
echo Searching for Python installation...

REM Try standard 'python' command
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto PYTHON_CHECK_DONE
)

REM Try 'python3' command
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto PYTHON_CHECK_DONE
)

REM Try Windows Python launcher
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto PYTHON_CHECK_DONE
)

:PYTHON_CHECK_DONE

if "%PYTHON_CMD%"=="" (
    echo ERROR: Python is not found or not accessible from command line
    echo.
    echo TIP: Run 'check_python.bat' to diagnose Python installation issues
    echo.
    echo Would you like to:
    echo.
    echo [1] Run diagnostic tool to check Python installation
    echo [2] Install Python automatically using winget
    echo [3] Open Python download page in browser
    echo [4] Exit
    echo.2
    set /p choice="Enter your choice (1, 2, 3, or 4): "
    
    if "%choice%"=="1" (
        echo.
        echo Running Python diagnostic tool...
        echo.
        call check_python.bat
        echo.
        echo After reviewing the diagnostic results, try running this script again.
        echo.
        pause
        exit /b 0
    )
    
    if "%choice%"=="1" (
        echo.
        echo Installing Python using Windows Package Manager...
        echo This may take a few minutes...
        echo.
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        if errorlevel 1 (
            echo.
            echo Automatic installation failed. Trying alternative method...
            goto MANUAL_INSTALL
        )
        echo.
        echo Python installed successfully!
        echo.
        echo Attempting to launch the application...
        echo.
        
        REM Try to find Python in common install locations
        set PYTHON_CMD=python
        
        REM Check if python is now available
        python --version >nul 2>&1
        if not errorlevel 1 goto PYTHON_FOUND
        
        REM Try common Python 3.12 locations
        if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
            set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
            goto PYTHON_FOUND
        )
        
        if exist "C:\Program Files\Python312\python.exe" (
            set PYTHON_CMD=C:\Program Files\Python312\python.exe
            goto PYTHON_FOUND
        )
        
        if exist "%PROGRAMFILES(X86)%\Python312\python.exe" (
            set PYTHON_CMD=%PROGRAMFILES(X86)%\Python312\python.exe
            goto PYTHON_FOUND
        )
        
        REM Python installed but not in PATH yet
        echo.
        echo Python was installed, but requires a new terminal window to work.
        echo Please CLOSE this window and double-click start_generator.bat again.
        echo.
        pause
        exit /b 0
    )
    
    if "%choice%"=="3" (
        :MANUAL_INSTALL
        echo.
        echo Opening Python download page in your browser...
        start https://www.python.org/downloads/
        echo.
        echo Please download and install Python 3.8 or higher.
        echo IMPORTANT: Check "Add Python to PATH" during installation!
        echo.
        echo After installation, CLOSE THIS WINDOW and open a NEW terminal,
        echo then run the application again.
        echo.
        pause
        exit /b 0
    )
    
    if "%choice%"=="4" (
        echo.
        echo Exiting...
        exit /b 1
    )
    
    echo.
    echo Invalid choice. Exiting...
    pause
    exit /b 1
)

:PYTHON_FOUND
echo Python found: 
%PYTHON_CMD% --version
echo.
echo Starting Test Case Generator...
echo.

REM Launch the application
%PYTHON_CMD% app\testcase_generator.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application
    echo.
    pause
)
