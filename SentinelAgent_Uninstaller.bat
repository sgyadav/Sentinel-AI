
@echo off
REM Sentinel AI Agent Uninstaller
REM Run as Administrator

setlocal enabledelayedexpansion

set INSTALL_DIR=C:\Program Files\SentinelAI
set CONFIG_DIR=C:\ProgramData\SentinelAI

echo Uninstalling Sentinel AI Agent...
echo.

REM Stop service
echo Stopping service...
net stop SentinelAIAgent >nul 2>&1

REM Delete service
echo Removing service...
sc delete SentinelAIAgent >nul 2>&1

REM Delete installation directory
if exist "%INSTALL_DIR%" (
    echo Removing files...
    rmdir /s /q "%INSTALL_DIR%"
)

echo.
echo Uninstallation completed.
echo Configuration files preserved at: %CONFIG_DIR%
echo.
pause
