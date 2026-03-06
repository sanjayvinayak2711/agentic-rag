@echo off
title Agentic RAG - Single File Startup
echo.
echo ========================================
echo    Starting Agentic RAG - SINGLE FILE
echo ========================================
echo.
echo [1/4] Checking OS and launching...
if exist "C:\Windows\System32\cmd.exe" (
    echo [2/4] Windows detected - Using batch file...
    call :run_batch
) else (
    echo [2/4] Linux/Mac detected - Using shell script...
    call :run_shell
)
goto :end

:run_batch
echo [3/4] Launching single file...
python app/main.py
goto :end

:run_shell
echo [3/4] Launching single file...
python3 app/main.py
goto :end

:end
echo.
echo ========================================
echo    READY INSTANTLY!
echo    Frontend: http://localhost:8000
echo    Backend: Running in single process
echo ========================================
pause
