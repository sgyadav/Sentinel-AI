param(
    [Parameter(Mandatory = $true)]
    [string]$ServerUrl,

    [string]$AgentPath = (Resolve-Path "$PSScriptRoot\..\agent").Path,

    [string]$TaskName = "Sentinel Endpoint Agent",

    [string]$PythonCommand = "py"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $AgentPath)) {
    throw "Agent path not found: $AgentPath"
}

$serverUri = [Uri]$ServerUrl
if ($serverUri.Scheme -notin @("http", "https") -or -not $serverUri.IsAbsoluteUri) {
    throw "ServerUrl must be an absolute http:// or https:// backend origin. Do not include an API path."
}
if ($serverUri.AbsolutePath -ne "/" -or $serverUri.Query -or $serverUri.Fragment -or $serverUri.UserInfo) {
    throw "ServerUrl must contain only the backend origin, without credentials, path, query, or fragment."
}
if ($serverUri.Scheme -eq "http") {
    Write-Warning "The agent token will be sent without transport encryption. Use HTTPS except on an isolated trusted LAN."
}

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask -and $existingTask.State -eq "Running") {
    Stop-ScheduledTask -TaskName $TaskName
}

$secureToken = Read-Host "Enter the SENTINEL_AGENT_TOKEN configured on the backend" -AsSecureString
$tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
try {
    $agentToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
}
if ($agentToken.Length -lt 32) {
    throw "SENTINEL_AGENT_TOKEN must contain at least 32 characters."
}

$configDirectory = Join-Path $env:ProgramData "SentinelAI"
$configPath = Join-Path $configDirectory "config.json"
New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
& icacls.exe $configDirectory /inheritance:r /grant:r "*S-1-5-18:(OI)(CI)(F)" "*S-1-5-32-544:(OI)(CI)(F)" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not restrict access to the agent configuration directory."
}
if (Test-Path $configPath) {
    $agentConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
} else {
    $agentConfig = [pscustomobject]@{}
}
$backendOrigin = $serverUri.GetLeftPart([UriPartial]::Authority).TrimEnd('/')
$agentConfig | Add-Member -NotePropertyName server_url -NotePropertyValue $backendOrigin -Force
$agentConfig | Add-Member -NotePropertyName agent_token -NotePropertyValue $agentToken -Force
[IO.File]::WriteAllText(
    $configPath,
    ($agentConfig | ConvertTo-Json -Depth 10),
    [Text.UTF8Encoding]::new($false)
)
& icacls.exe $configPath /inheritance:r /grant:r "*S-1-5-18:(F)" "*S-1-5-32-544:(F)" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Could not restrict access to the agent configuration file."
}
$agentToken = $null
$secureToken = $null

Write-Host "Installing endpoint agent dependencies..."
Push-Location $AgentPath
& $PythonCommand -m pip install -r requirements.txt
Pop-Location

$agentCommand = @"
Set-Location '$AgentPath'
& $PythonCommand agent.py
"@

$encodedCommand = [Convert]::ToBase64String(
    [Text.Encoding]::Unicode.GetBytes($agentCommand)
)

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"

$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName

Write-Host "Sentinel Endpoint Agent installed and started."
Write-Host "Telemetry target: $ServerUrl"
