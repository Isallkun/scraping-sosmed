@echo off
REM =============================================================================
REM Virtual Environment Setup Script (Windows)
REM =============================================================================
REM This script creates a Python virtual environment and installs dependencies
REM =============================================================================

echo ==========================================
echo Social Media Scraper - Virtual Environment Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Display Python version
echo Found Python version:
python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo Warning: Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo Virtual environment recreated
    ) else (
        echo Using existing virtual environment
    )
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate, run:
echo   deactivate
echo.
echo Next steps:
echo   1. Copy .env.example to .env and configure your settings
echo   2. Run the scraper: python scraper\main_scraper.py --help
echo   3. Or use Docker: docker-compose up -d
echo.
pause
