
@echo off
REM Sentinel AI Agent Diagnostics
REM Run as Administrator

set INSTALL_DIR=C:\Program Files\SentinelAI
set CONFIG_DIR=C:\ProgramData\SentinelAI

echo SENTINEL AI AGENT DIAGNOSTICS
echo.

if exist "%CONFIG_DIR%\config.json" (
    echo Current config:
    type "%CONFIG_DIR%\config.json"
    echo.
) else (
    echo [ERROR] Missing config: %CONFIG_DIR%\config.json
)

if exist "%INSTALL_DIR%\SentinelAgent.exe" (
    "%INSTALL_DIR%\SentinelAgent.exe" diagnose
) else (
    echo [ERROR] Missing agent exe: %INSTALL_DIR%\SentinelAgent.exe
)

echo.
sc query SentinelAIAgent
echo.
echo Last log lines:
powershell -NoProfile -ExecutionPolicy Bypass -Command "if(Test-Path 'C:\ProgramData\SentinelAI\agent.log'){Get-Content 'C:\ProgramData\SentinelAI\agent.log' -Tail 40}"
echo.
pause
