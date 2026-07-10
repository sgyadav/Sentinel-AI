@echo off
REM SENTINEL AI - Complete Startup Script
REM This starts both Backend and Frontend automatically

echo.
echo ============================================================
echo   SENTINEL AI - REAL-TIME CYBER DEFENSE SYSTEM
echo   Complete Startup Script
echo ============================================================
echo.

set "PROJECT_DIR=%~dp0"

echo [STEP 1] Starting Backend API on port 8000...
start "SENTINEL AI - Backend" cmd /k "cd /d "%PROJECT_DIR%backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [STEP 2] Waiting for backend to start (5 seconds)...
timeout /t 5 /nobreak

echo [STEP 3] Starting Frontend on port 5173...
start "SENTINEL AI - Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm run dev"

echo [STEP 4] Waiting for frontend to start (8 seconds)...
timeout /t 8 /nobreak

echo.
echo ============================================================
echo   SERVICES STARTING!
echo ============================================================
echo.
echo Please wait for the browser to open...
echo.
echo If browser doesn't open automatically, visit:
echo   http://localhost:5173
echo.
echo Login with:
echo   Username: admin
echo   Password: Admin1234
echo.
echo ============================================================
echo.

REM Wait a bit and open browser
timeout /t 3 /nobreak
start http://localhost:5173

echo.
echo Browser opened at: http://localhost:5173
echo.
echo To stop: Close both command windows (Backend and Frontend)
echo.

pause
