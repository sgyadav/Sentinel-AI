"""
Phase 10: WINDOWS INSTALLER BUILDER
Packages the agent into a Windows service installer
Requires: PyInstaller (pip install pyinstaller)

Usage:
    python build_installer.py
    
Output:
    SentinelAgent.exe - Standalone agent executable
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

def create_installer_script():
    """Create batch script for Windows installer"""
    installer_script = r'''
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
'''

    with open("SentinelAgent_Installer.bat", "w") as f:
        f.write(installer_script)
    print("Created: SentinelAgent_Installer.bat")


def create_uninstaller_script():
    """Create batch script for uninstaller"""
    uninstaller_script = r'''
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
'''

    with open("SentinelAgent_Uninstaller.bat", "w") as f:
        f.write(uninstaller_script)
    print("Created: SentinelAgent_Uninstaller.bat")


def create_config_template():
    """Create configuration template"""
    config = {
        "server_url": "http://YOUR_SERVER:8000",
        "organization": "YourCompany",
        "agent_id": "GENERATE_NEW",
        "agent_version": "1.0.0",
        "heartbeat_interval": 10,
        "usb_check_interval": 5,
        "process_check_interval": 30,
        "max_retries": 3,
        "retry_delay": 5,
        "enable_usb_monitoring": True,
        "enable_process_monitoring": True,
        "enable_login_monitoring": True,
        "log_level": "INFO"
    }

    with open("agent_config_template.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Created: agent_config_template.json")


def build_agent_executable():
    """Build SentinelAgent.exe with PyInstaller when available."""
    pyinstaller = shutil.which("pyinstaller")
    command = None
    if pyinstaller:
        command = [pyinstaller, "--onefile", "--name", "SentinelAgent", "agent/agent.py"]
    else:
        try:
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            command = [sys.executable, "-m", "PyInstaller", "--onefile", "--name", "SentinelAgent", "agent/agent.py"]
        except Exception:
            command = None

    if not command:
        print("[WARN] PyInstaller not found. Install it and rerun to build SentinelAgent.exe.")
        return None

    subprocess.run(command, check=True)
    exe_path = Path("dist") / "SentinelAgent.exe"
    if exe_path.exists():
        print(f"Created: {exe_path}")
        return exe_path
    print("[WARN] PyInstaller completed but dist/SentinelAgent.exe was not found.")
    return None


def create_iexpress_config(pkg_dir):
    """Create an IExpress config that can package SentinelAgentSetup.exe on Windows."""
    sed_path = Path("SentinelAgentSetup.sed")
    package_files = [
        "SentinelAgent.exe",
        "SentinelAgent_Installer.bat",
        "SentinelAgent_Uninstaller.bat",
        "config.json",
        "INSTALLATION_GUIDE.txt",
    ]
    source_lines = "\n".join([f"%FILE{i}%=" for i, _ in enumerate(package_files)])
    string_lines = "\n".join([f"FILE{i}={name}" for i, name in enumerate(package_files)])
    sed = f"""[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[SourceFiles]
SourceFiles0={str(pkg_dir.resolve())}
[SourceFiles0]
{source_lines}
[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=Sentinel AI Agent setup completed.
TargetName={str((pkg_dir / "SentinelAgentSetup.exe").resolve())}
FriendlyName=Sentinel AI Agent Setup
AppLaunched=SentinelAgent_Installer.bat
PostInstallCmd=<None>
AdminQuietInstCmd=SentinelAgent_Installer.bat
UserQuietInstCmd=SentinelAgent_Installer.bat
{string_lines}
"""
    sed_path.write_text(sed, encoding="utf-8")
    print("Created: SentinelAgentSetup.sed")
    return sed_path


def create_readme():
    """Create installation README"""
    readme = """
# SENTINEL AI AGENT - INSTALLATION GUIDE

## System Requirements
- Windows 10 or later
- Python 3.8+ (if running from source)
- Administrator privileges for installation

## Installation Methods

### Method 1: Using Installer (Recommended)
1. Run `SentinelAgent_Installer.bat` as Administrator
2. Follow the prompts
3. Agent will be installed as Windows Service
4. Service starts automatically with Windows

### Method 2: Manual Installation
1. Create directory: `C:\\Program Files\\SentinelAI`
2. Copy `SentinelAgent.exe` to that directory
3. Create config at: `C:\\ProgramData\\SentinelAI\\config.json`
4. Register service:
   ```
   sc create SentinelAIAgent binPath= "C:\\Program Files\\SentinelAI\\SentinelAgent.exe"
   net start SentinelAIAgent
   ```

## Configuration

Edit `C:\\ProgramData\\SentinelAI\\config.json`:

```json
{
  "server_url": "http://your-server:8000",
  "organization": "Your Company",
  "heartbeat_interval": 10,
  "usb_check_interval": 5,
  "process_check_interval": 30
}
```

## Service Management

Start agent:
```
net start SentinelAIAgent
```

Stop agent:
```
net stop SentinelAIAgent
```

Check status:
```
sc query SentinelAIAgent
```

## Logs

Agent logs are written to:
```
C:\\ProgramData\\SentinelAI\\agent.log
```

View logs:
```
Get-Content "C:\\ProgramData\\SentinelAI\\agent.log" -Tail 50
```

## Troubleshooting

**Agent won't start:**
- Check Windows Event Viewer for service errors
- Verify config.json is valid JSON
- Check server URL is accessible
- Review agent.log for errors

**High CPU usage:**
- Increase heartbeat_interval in config
- Increase process_check_interval
- Check for runaway processes

**Network issues:**
- Verify server is running and accessible
- Check firewall rules allow outbound connection
- Test with: `ping your-server`

## Uninstallation

Run `SentinelAgent_Uninstaller.bat` as Administrator

This will:
- Stop the service
- Remove the service registration  
- Delete installation directory
- Preserve configuration files

## Support

For issues:
1. Check agent logs: `C:\\ProgramData\\SentinelAI\\agent.log`
2. Verify network connectivity
3. Ensure backend is running: `curl http://your-server:8000/health`
"""

    with open("INSTALLATION_GUIDE.txt", "w") as f:
        f.write(readme)
    print("Created: INSTALLATION_GUIDE.txt")


def main():
    """Build installer package"""
    print("=" * 60)
    print("SENTINEL AI AGENT - INSTALLER BUILDER")
    print("=" * 60)
    print()

    # Check if agent.py exists
    if not Path("agent/agent.py").exists():
        print("[ERROR] agent/agent.py not found!")
        print("Please run this from the project root directory")
        return False

    print("[1/6] Creating installer script...")
    create_installer_script()

    print("[2/6] Creating uninstaller script...")
    create_uninstaller_script()

    print("[3/6] Creating configuration template...")
    create_config_template()

    print("[4/6] Creating installation guide...")
    create_readme()

    print("[5/6] Building agent executable when tooling is available...")
    exe_path = build_agent_executable()

    print("[6/6] Creating package structure...")
    # Create installer package directory
    pkg_dir = Path("installer_package")
    pkg_dir.mkdir(exist_ok=True)

    # Copy files
    shutil.copy("SentinelAgent_Installer.bat", pkg_dir)
    shutil.copy("SentinelAgent_Uninstaller.bat", pkg_dir)
    shutil.copy("agent_config_template.json", pkg_dir / "config.json")
    shutil.copy("INSTALLATION_GUIDE.txt", pkg_dir)
    if exe_path and exe_path.exists():
        shutil.copy(exe_path, pkg_dir / "SentinelAgent.exe")
    elif Path("SentinelAgent.exe").exists():
        shutil.copy("SentinelAgent.exe", pkg_dir / "SentinelAgent.exe")
    else:
        print("[WARN] SentinelAgent.exe is not in the package yet.")

    sed_path = create_iexpress_config(pkg_dir)
    iexpress = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "iexpress.exe"
    if iexpress.exists() and (pkg_dir / "SentinelAgent.exe").exists():
        try:
            subprocess.run([str(iexpress), "/N", str(sed_path)], check=True)
            print(f"Created: {pkg_dir / 'SentinelAgentSetup.exe'}")
        except Exception as exc:
            print(f"[WARN] IExpress setup EXE generation failed: {exc}")
    else:
        print("[WARN] SentinelAgentSetup.exe not generated. Ensure SentinelAgent.exe exists, then run: iexpress /N SentinelAgentSetup.sed")

    print()
    print("=" * 60)
    print("INSTALLER PACKAGE CREATED")
    print("=" * 60)
    print()
    print("Location: ./installer_package/")
    print()
    print("Files:")
    print("  - SentinelAgent.exe (compiled from agent.py, if PyInstaller is installed)")
    print("  - SentinelAgentSetup.exe (generated by IExpress when available)")
    print("  - SentinelAgent_Installer.bat")
    print("  - SentinelAgent_Uninstaller.bat")
    print("  - config.json (configuration template)")
    print("  - INSTALLATION_GUIDE.txt")
    print()
    print("To build executable:")
    print("  pip install pyinstaller")
    print("  pyinstaller --onefile --icon=icon.ico agent/agent.py")
    print()
    print("Then rerun this builder to generate installer_package/SentinelAgentSetup.exe")
    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
