@echo off
REM Quick start script for ContextBridge on Windows

echo.
echo 🚀 ContextBridge - Day 1 Setup
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

REM Create virtual environment
echo 📦 Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt >nul 2>&1
echo ✅ Dependencies installed
echo.

REM Create data directory
if not exist "data" mkdir data
echo ✅ Data directory created
echo.

echo 🎯 Ready to run ContextBridge!
echo.
echo To start the server:
echo   python main.py
echo.
echo Then visit:
echo   http://localhost:8000/docs
echo.
echo To index the example content:
echo   curl -X POST "http://localhost:8000/api/v1/index/file" ^
echo     -H "Content-Type: application/x-www-form-urlencoded" ^
echo     -d "file_path=%cd%\example_content.md"
echo.
pause
