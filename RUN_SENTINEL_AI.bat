@echo off
REM SENTINEL AI - Complete Startup Script
REM This script starts both backend and frontend

echo.
echo ============================================
echo   SENTINEL AI - CYBER DEFENSE SYSTEM
echo   Starting Services...
echo ============================================
echo.

REM Get directory
set "PROJECT_DIR=%cd%"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)

echo [OK] Python and Node.js found
echo.

REM Start Backend
echo [1/2] Starting Backend API on port 8000...
cd /d "%PROJECT_DIR%\backend"
start "SENTINEL Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start Frontend
echo [2/2] Starting Frontend on port 5173...
cd /d "%PROJECT_DIR%\frontend"
start "SENTINEL Frontend" cmd /k npm run dev

echo.
echo ============================================
echo   SERVICES STARTING...
echo ============================================
echo.
echo Waiting for services to be ready...
timeout /t 8 /nobreak

echo.
echo Opening browser...
start http://localhost:5173

echo.
echo ============================================
echo   READY!
echo ============================================
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Login with:
echo   Username: admin
echo   Password: Admin1234
echo.
echo Close the backend and frontend windows to stop.
echo.

pause
