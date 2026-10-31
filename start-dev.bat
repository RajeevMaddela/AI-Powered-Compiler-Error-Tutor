@echo off
echo =======================================================
echo Starting AI Powered Compiler Error Tutor Development
echo =======================================================

echo Checking Docker Engine...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Starting Backend API Server (Port 8000)...
start "Compiler Error Tutor - Backend" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Frontend Dev Server (Port 5173)...
start "Compiler Error Tutor - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo =======================================================
echo Services launched!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/api/docs
echo =======================================================
