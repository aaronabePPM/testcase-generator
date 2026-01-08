@echo off
REM Quick Launcher for Streamlit Web App

echo ========================================
echo Test Case Generator - Web Version
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Checking Streamlit installation...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    pip install -r requirements-streamlit.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Streamlit app...
echo.
echo The app will open in your default browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run app\streamlit_app.py

pause
