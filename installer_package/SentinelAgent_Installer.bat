
@echo off
REM Sentinel AI Agent Installer
REM Run as Administrator

setlocal enabledelayedexpansion

set INSTALL_DIR=C:\Program Files\SentinelAI
set CONFIG_DIR=C:\ProgramData\SentinelAI
set LOG_FILE=%CONFIG_DIR%\install.log
set SERVER_URL=%~1
if "%SERVER_URL%"=="" set SERVER_URL=http://localhost:8000

REM Create directories
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%CONFIG_DIR%" 2>nul
mkdir "%CONFIG_DIR%\logs" 2>nul

REM Copy agent executable
copy "SentinelAgent.exe" "%INSTALL_DIR%\" >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo Installation failed: Could not copy executable >>"%LOG_FILE%"
    echo [ERROR] Could not copy SentinelAgent.exe to %INSTALL_DIR%
    pause
    exit /b 1
)

REM Create default config if not exists
if not exist "%CONFIG_DIR%\config.json" (
    (
        echo {
        echo   "server_url": "%SERVER_URL%",
        echo   "organization": "Default",
        echo   "heartbeat_interval": 10,
        echo   "usb_check_interval": 5,
        echo   "process_check_interval": 30,
        echo   "max_retries": 3,
        echo   "retry_delay": 5,
        echo   "agent_id": "GENERATE_NEW",
        echo   "agent_version": "1.0.0"
        echo }
    ) > "%CONFIG_DIR%\config.json"
    echo Configuration created: %CONFIG_DIR%\config.json >>"%LOG_FILE%"
)

REM Register Windows Service
"%INSTALL_DIR%\SentinelAgent.exe" install --startup auto >>"%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo Service registration failed >>"%LOG_FILE%"
    echo [ERROR] Could not register Windows service
    pause
    exit /b 1
)

REM Start service
net start SentinelAIAgent >>"%LOG_FILE%" 2>&1

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
