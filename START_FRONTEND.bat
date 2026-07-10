@echo off
REM SENTINEL AI - Frontend Start Script

echo.
echo ========================================
echo   SENTINEL AI - Frontend
echo   Starting Vite Dev Server...
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Start npm dev using cmd instead of PowerShell
cmd /c "npm run dev"

pause
