@echo off
REM SENTINEL AI - Backend Start Script

echo.
echo ========================================
echo   SENTINEL AI - Backend
echo   Starting FastAPI Server...
echo ========================================
echo.

cd /d "%~dp0backend"

REM Start backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
