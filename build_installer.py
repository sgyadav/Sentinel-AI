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
import re
import sys
import shutil
import json
import subprocess
import socket
from pathlib import Path
from urllib.parse import urlparse


def looks_like_local_server(url):
    return bool(re.match(
        r"^(localhost|127\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.|\[?::1\]?)",
        url,
        re.IGNORECASE
    ))


def normalize_server_url(value):
    url = "".join(str(value or "").strip().split()).replace("\\", "/")
    if not url:
        raise ValueError("server_url is empty")

    if "://" not in url:
        single_slash_scheme = re.match(r"^(https?):/+(.*)$", url, re.IGNORECASE)
        if single_slash_scheme:
            url = f"{single_slash_scheme.group(1).lower()}://{single_slash_scheme.group(2).lstrip('/')}"
        else:
            scheme = "http" if looks_like_local_server(url) else "https"
            url = f"{scheme}://{url}"

    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("server_url must start with http:// or https://")

    if not parsed.netloc and parsed.path:
        repaired = f"{parsed.scheme.lower()}://{parsed.path.lstrip('/')}"
        parsed = urlparse(repaired)
        url = repaired

    if not parsed.netloc:
        raise ValueError("server_url must include a hostname")

    return url.rstrip("/")


def detect_server_url():
    """Return the production backend URL."""
    override = os.getenv("SENTINEL_SERVER_URL")
    if override:
        return normalize_server_url(override)

    return normalize_server_url("https://sentinel-ai-fz5u.onrender.com")


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


def create_configurator_script():
    """Create a PowerShell helper that safely merges installer config with existing agent identity."""
    configurator = r'''
param(
    [string]$ServerUrl = ""
)

$ErrorActionPreference = "Stop"
$ConfigDir = "C:\ProgramData\SentinelAI"
$TargetConfig = Join-Path $ConfigDir "config.json"
$SourceConfig = Join-Path $PSScriptRoot "config.json"

function Test-LocalServerUrl {
    param([string]$Value)
    return $Value -match "^(localhost|127\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.|\[?::1\]?)"
}

function Normalize-ServerUrl {
    param([string]$Url)

    $value = [string]$Url
    $value = ($value.Trim() -replace "\s+", "")
    $value = $value -replace "\\", "/"

    if (-not $value) {
        throw "server_url is empty"
    }

    if ($value -notmatch "://") {
        if ($value -match "^(https?):/+(.*)$") {
            $scheme = $Matches[1].ToLowerInvariant()
            $hostAndPath = $Matches[2].TrimStart("/")
            $value = "${scheme}://${hostAndPath}"
        } else {
            $scheme = if (Test-LocalServerUrl $value) { "http" } else { "https" }
            $value = "${scheme}://${value}"
        }
    }

    if ($value -match "^(https?):///+(.+)$") {
        $scheme = $Matches[1].ToLowerInvariant()
        $hostAndPath = $Matches[2].TrimStart("/")
        $value = "${scheme}://${hostAndPath}"
    }

    $uri = $null
    if (-not [System.Uri]::TryCreate($value, [System.UriKind]::Absolute, [ref]$uri)) {
        throw "server_url is not a valid absolute URL: $value"
    }
    if ($uri.Scheme -notin @("http", "https") -or -not $uri.Host) {
        throw "server_url must start with http:// or https:// and include a hostname: $value"
    }

    return $value.TrimEnd([char[]]"/")
}

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ConfigDir "logs") | Out-Null

$newConfig = [ordered]@{
    server_url = "https://sentinel-ai-fz5u.onrender.com"
    organization = "Default"
    agent_id = "GENERATE_NEW"
    agent_version = "1.0.0"
    heartbeat_interval = 10
    usb_check_interval = 5
    process_check_interval = 30
    max_retries = 3
    retry_delay = 5
    enable_usb_monitoring = $true
    enable_process_monitoring = $true
    enable_login_monitoring = $true
    log_level = "INFO"
}

if (Test-Path $SourceConfig) {
    $source = Get-Content $SourceConfig -Raw | ConvertFrom-Json
    foreach ($property in $source.PSObject.Properties) {
        $newConfig[$property.Name] = $property.Value
    }
}

if (Test-Path $TargetConfig) {
    try {
        $existing = Get-Content $TargetConfig -Raw | ConvertFrom-Json
        if ($existing.agent_id -and $existing.agent_id -ne "GENERATE_NEW") {
            $newConfig["agent_id"] = $existing.agent_id
        }
    } catch {
        Copy-Item $TargetConfig "$TargetConfig.broken" -Force
    }
}

if ($ServerUrl -and $ServerUrl.Trim().Length -gt 0) {
    $newConfig["server_url"] = $ServerUrl
}

$newConfig["server_url"] = Normalize-ServerUrl $newConfig["server_url"]

[pscustomobject]$newConfig | ConvertTo-Json -Depth 5 | Set-Content -Path $TargetConfig -Encoding UTF8
Write-Host "Config ready: $TargetConfig"
Write-Host "Backend URL: $($newConfig["server_url"])"
Write-Host "Agent ID: $($newConfig["agent_id"])"
'''

    with open("ConfigureSentinelAgent.ps1", "w") as f:
        f.write(configurator)
    print("Created: ConfigureSentinelAgent.ps1")


def create_diagnostics_script():
    """Create a support script for employee-PC registration checks."""
    diagnostics = r'''
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
'''

    with open("SentinelAgent_Diagnostics.bat", "w") as f:
        f.write(diagnostics)
    print("Created: SentinelAgent_Diagnostics.bat")


def create_config_template():
    """Create configuration template"""
    server_url = detect_server_url()
    config = {
        "server_url": server_url,
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
    print(f"Default backend URL: {server_url}")


def build_agent_executable():
    """Build SentinelAgent.exe with PyInstaller when available."""
    command = None
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        command = [sys.executable, "-m", "PyInstaller"]
    except Exception:
        pyinstaller = shutil.which("pyinstaller")
        if pyinstaller:
            command = [pyinstaller]

    if not command:
        print("[WARN] PyInstaller not found. Install it and rerun to build SentinelAgent.exe.")
        return None

    hidden_imports = [
        "pythoncom",
        "pywintypes",
        "servicemanager",
        "win32api",
        "win32con",
        "win32event",
        "win32evtlog",
        "win32pipe",
        "win32service",
        "win32serviceutil",
        "win32timezone",
        "win32trace",
        "winerror",
        "ntsecuritycon",
    ]

    options = [
        "--clean",
        "--onefile",
        "--name",
        "SentinelAgent",
        "--collect-submodules",
        "win32com",
    ]
    for module in hidden_imports:
        options.extend(["--hidden-import", module])

    pywin32_dirs = [
        Path(sys.prefix) / "Lib" / "site-packages" / "pywin32_system32",
        Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages" / "pywin32_system32",
    ]
    seen_dlls = set()
    for dll_dir in pywin32_dirs:
        if not dll_dir.exists():
            continue
        for dll_path in dll_dir.glob("*.dll"):
            resolved = dll_path.resolve()
            if resolved in seen_dlls:
                continue
            seen_dlls.add(resolved)
            options.extend(["--add-binary", f"{resolved};."])

    command = command + options + ["agent/agent.py"]
    print("[INFO] Building SentinelAgent.exe with explicit pywin32 packaging support")
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
        "ConfigureSentinelAgent.ps1",
        "SentinelAgent_Diagnostics.bat",
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
ShowInstallProgramWindow=1
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
AppLaunched=cmd.exe /c SentinelAgent_Installer.bat
PostInstallCmd=<None>
AdminQuietInstCmd=cmd.exe /c SentinelAgent_Installer.bat
UserQuietInstCmd=cmd.exe /c SentinelAgent_Installer.bat
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
- Administrator privileges for installation

## Installation Methods

### Method 1: Using Installer (Recommended)
1. Confirm `config.json` points to the admin backend, for example `https://sentinel-ai-fz5u.onrender.com`
2. Run `SentinelAgentSetup.exe` as Administrator
3. Agent will be installed as Windows Service
4. Service starts automatically with Windows

### Method 2: Batch Installer With URL Override
Run as Administrator:
```
SentinelAgent_Installer.bat http://ADMIN-PC-IP:8000
```

### Method 3: Manual Installation
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
  "server_url": "https://sentinel-ai-fz5u.onrender.com",
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

## Registration Check

Run diagnostics as Administrator:
```
SentinelAgent_Diagnostics.bat
```

Or from the installed folder:
```
"C:\\Program Files\\SentinelAI\\SentinelAgent.exe" diagnose
```

Register immediately without waiting for the service loop:
```
"C:\\Program Files\\SentinelAI\\SentinelAgent.exe" register
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

    print("[1/8] Creating installer script...")
    create_installer_script()

    print("[2/8] Creating uninstaller script...")
    create_uninstaller_script()

    print("[3/8] Creating configurator script...")
    create_configurator_script()

    print("[4/8] Creating diagnostics script...")
    create_diagnostics_script()

    print("[5/8] Creating configuration template...")
    create_config_template()

    print("[6/8] Creating installation guide...")
    create_readme()

    print("[7/8] Building agent executable when tooling is available...")
    exe_path = build_agent_executable()

    print("[8/8] Creating package structure...")
    # Create installer package directory
    pkg_dir = Path("installer_package")
    pkg_dir.mkdir(exist_ok=True)

    # Copy files
    shutil.copy("SentinelAgent_Installer.bat", pkg_dir)
    shutil.copy("SentinelAgent_Uninstaller.bat", pkg_dir)
    shutil.copy("ConfigureSentinelAgent.ps1", pkg_dir)
    shutil.copy("SentinelAgent_Diagnostics.bat", pkg_dir)
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
    print("  - ConfigureSentinelAgent.ps1")
    print("  - SentinelAgent_Diagnostics.bat")
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
