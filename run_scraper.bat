@echo off
REM Social Media Scraper - Quick Run Script
REM Usage: run_scraper.bat [platform] [target_url] [limit]

setlocal

REM Default values from .env
set PLATFORM=%1
set TARGET=%2
set LIMIT=%3

if "%PLATFORM%"=="" set PLATFORM=instagram
if "%TARGET%"=="" set TARGET=https://www.instagram.com/rusdi_sutejo/
if "%LIMIT%"=="" set LIMIT=10

echo ========================================
echo Social Media Scraper
echo ========================================
echo Platform: %PLATFORM%
echo Target: %TARGET%
echo Limit: %LIMIT%
echo ========================================
echo.

REM Run the scraper
python -m scraper.main_scraper --platform %PLATFORM% --target "%TARGET%" --limit %LIMIT% --no-headless

echo.
echo ========================================
echo Scraping completed!
echo Check the output directory for results.
echo ========================================
pause
