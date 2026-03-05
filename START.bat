@echo off
title Agentic RAG - Single Click Start
echo.
echo ========================================
echo    Starting Agentic RAG Project
echo ========================================
echo.
echo [1/4] Checking requirements...
python -c "import os; print('✅ OK' if os.path.exists('app/main.py') and os.path.exists('ui/index.html') else '❌ Missing files')"
echo.
echo [2/4] Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo [3/4] Starting backend server...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo [4/4] Opening frontend...
timeout /t 3 >nul
start http://localhost:8000
echo.
echo ========================================
echo    Agentic RAG is now running!
echo    Frontend: http://localhost:8000
echo    Press Ctrl+C to stop
echo ========================================
pause
