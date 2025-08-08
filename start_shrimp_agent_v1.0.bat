@echo off
echo.
echo ========================================
echo Shrimp Agent v1.0 Launcher
echo ========================================
echo Version: Shrimp_Agent1.0
echo Description: Intelligent Multimodal RAG System
echo Author: Shrimp Agent Team
echo Time: %date% %time%
echo ========================================
echo.

echo [1/4] Stopping existing Python processes...
taskkill /f /im python.exe >nul 2>&1
echo Process cleanup completed

echo [2/4] Waiting 3 seconds before starting services...
timeout /t 3 /nobreak >nul

echo [3/4] Starting backend API server...
start "Shrimp Agent API Server" cmd /k "echo Starting API Server (Port:5000) && python api_server_v2.py"
if %errorlevel% neq 0 (
    echo Error: API server startup failed
    pause
    exit /b 1
)
echo API server starting...

echo Waiting for API server initialization...
timeout /t 5 /nobreak >nul

echo [4/4] Starting frontend server...
start "Shrimp Agent Frontend" cmd /k "echo Starting Frontend Server (Port:8080) && python frontend/server.py"
if %errorlevel% neq 0 (
    echo Error: Frontend server startup failed
    pause
    exit /b 1
)
echo Frontend server starting...

echo Waiting for frontend server initialization...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Shrimp Agent v1.0 Started Successfully!
echo ========================================
echo Backend API: http://localhost:5000
echo Frontend:   http://localhost:8080
echo ========================================
echo Tips:
echo   - First run may need to download model files
echo   - Make sure .env file has correct API keys
echo   - Check terminal windows for error messages
echo ========================================
echo.

echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8080

echo.
echo System Status Monitor:
echo   - Press any key to exit launcher
echo   - Services will continue running in background
echo   - Close terminal windows to stop services
echo.
pause

echo.
echo Thank you for using Shrimp Agent v1.0!
echo Project: https://github.com/shrimp-agent
echo.