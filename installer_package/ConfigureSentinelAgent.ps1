
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
