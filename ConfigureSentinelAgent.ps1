
param(
    [string]$ServerUrl = ""
)

$ErrorActionPreference = "Stop"
$ConfigDir = "C:\ProgramData\SentinelAI"
$TargetConfig = Join-Path $ConfigDir "config.json"
$SourceConfig = Join-Path $PSScriptRoot "config.json"

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ConfigDir "logs") | Out-Null

$newConfig = [ordered]@{
    server_url = "http://localhost:8000"
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
    $newConfig["server_url"] = $ServerUrl.Trim().TrimEnd("/")
}

if (-not $newConfig["server_url"]) {
    throw "server_url is empty"
}

[pscustomobject]$newConfig | ConvertTo-Json -Depth 5 | Set-Content -Path $TargetConfig -Encoding UTF8
Write-Host "Config ready: $TargetConfig"
Write-Host "Backend URL: $($newConfig["server_url"])"
Write-Host "Agent ID: $($newConfig["agent_id"])"
