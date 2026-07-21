
@echo off
REM Sentinel AI Agent Installer
REM Run as Administrator

setlocal enabledelayedexpansion

set INSTALL_DIR=C:\Program Files\SentinelAI
set CONFIG_DIR=C:\ProgramData\SentinelAI
set LOG_FILE=%CONFIG_DIR%\install.log
set SERVER_URL=%~1
set PACKAGE_DIR=%~dp0

REM Create directories
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%CONFIG_DIR%" 2>nul
mkdir "%CONFIG_DIR%\logs" 2>nul

REM Stop existing service before replacing files.
net stop SentinelAIAgent >>"%LOG_FILE%" 2>&1

REM Copy agent executable
copy "%PACKAGE_DIR%SentinelAgent.exe" "%INSTALL_DIR%\" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo Installation failed: Could not copy executable >>"%LOG_FILE%"
    echo [ERROR] Could not copy SentinelAgent.exe to %INSTALL_DIR%
    pause
    exit /b 1
)

REM Refresh config every install, but preserve the assigned AGT-xxxxx ID.
powershell -NoProfile -ExecutionPolicy Bypass -File "%PACKAGE_DIR%ConfigureSentinelAgent.ps1" -ServerUrl "%SERVER_URL%" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo Configuration failed >>"%LOG_FILE%"
    echo [ERROR] Could not create or update %CONFIG_DIR%\config.json
    pause
    exit /b 1
)

REM Register immediately so the admin can see the endpoint before the service loop starts.
"%INSTALL_DIR%\SentinelAgent.exe" register >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo Agent registration failed >>"%LOG_FILE%"
    echo [WARN] Could not register endpoint with backend right now.
    echo [WARN] Continuing installation. The agent service will retry after Windows starts.
)

REM Register or update Windows Service
"%INSTALL_DIR%\SentinelAgent.exe" update --startup auto >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    "%INSTALL_DIR%\SentinelAgent.exe" install --startup auto >>"%LOG_FILE%" 2>&1
)

if errorlevel 1 (
    echo Service registration failed >>"%LOG_FILE%"
    echo [ERROR] Could not register Windows service
    pause
    exit /b 1
)

REM Start service
net start SentinelAIAgent >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo Service start failed >>"%LOG_FILE%"
    echo [ERROR] SentinelAIAgent service did not start.
    echo Run diagnostics: "%INSTALL_DIR%\SentinelAgent.exe" diagnose
    echo Log file: %LOG_FILE%
    pause
    exit /b 1
)

echo. >>"%LOG_FILE%"
echo Installation completed successfully at %date% %time% >>"%LOG_FILE%"
echo.
echo [SUCCESS] Sentinel AI Agent installed successfully!
echo Installation directory: %INSTALL_DIR%
echo Configuration directory: %CONFIG_DIR%
echo.
echo To start the agent: net start SentinelAIAgent
echo To stop the agent: net stop SentinelAIAgent
echo.
echo Agent logs: %CONFIG_DIR%\agent.log
echo.
pause
