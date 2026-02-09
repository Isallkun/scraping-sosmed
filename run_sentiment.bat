@echo off
REM Sentiment Analysis - Quick Run Script
REM Usage: run_sentiment.bat [input_file] [output_file]

setlocal

set INPUT=%1
set OUTPUT=%2

if "%INPUT%"=="" (
    echo Error: Please provide input file path
    echo Usage: run_sentiment.bat input.json output.json
    pause
    exit /b 1
)

if "%OUTPUT%"=="" set OUTPUT=%INPUT:~0,-5%_sentiment.json

echo ========================================
echo Sentiment Analysis
echo ========================================
echo Input: %INPUT%
echo Output: %OUTPUT%
echo Model: VADER
echo ========================================
echo.

REM Run sentiment analysis
python -m sentiment.main_analyzer --input "%INPUT%" --output "%OUTPUT%" --model vader

echo.
echo ========================================
echo Analysis completed!
echo Results saved to: %OUTPUT%
echo ========================================
pause
