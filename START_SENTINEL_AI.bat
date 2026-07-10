@echo off
REM SENTINEL AI - Quick Start for Windows

echo.
echo ============================================
echo   SENTINEL AI - CYBER DEFENSE SYSTEM
echo   Quick Start Script for Windows
echo ============================================
echo.

REM Get the project directory
set PROJECT_DIR=%cd%

echo Checking prerequisites...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    exit /b 1
)
echo [OK] Docker found

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not found
    exit /b 1
)
echo [OK] Docker Compose found
echo.

echo ============================================
echo   Starting SENTINEL AI Services...
echo ============================================
echo.

REM Navigate to project directory
cd /d "%PROJECT_DIR%"

REM Pull latest images
echo [1/3] Pulling images...
docker-compose pull

REM Build images if needed
echo [2/3] Building images...
docker-compose build

REM Start services
echo [3/3] Starting services...
docker-compose up -d

REM Wait for services to start
echo.
echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak

REM Check status
echo.
echo ============================================
echo   Checking Service Status...
echo ============================================
echo.

docker-compose ps

echo.
echo ============================================
echo   SENTINEL AI IS RUNNING!
echo ============================================
echo.
echo ACCESS URLS:
echo   - Frontend:  http://localhost:5173
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo LOGIN CREDENTIALS:
echo   - Username:  admin
echo   - Password:  Admin1234
echo.
echo USEFUL COMMANDS:
echo   - View logs:     docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Rebuild:       docker-compose up -d --build
echo.
echo ============================================
echo.

REM Open browser
echo Opening frontend in browser...
timeout /t 3 /nobreak
start http://localhost:5173

pause
