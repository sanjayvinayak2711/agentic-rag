@echo off
title Agentic RAG
cd /d "%~dp0"

echo ========================================
echo        Starting Agentic RAG
echo ========================================
echo.

echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Launching application...
python -m app.main

echo.
echo ========================================
echo    Frontend: http://localhost:8000
echo ========================================

pause