param(
    [Parameter(Mandatory = $true)]
    [string]$ServerUrl,

    [string]$AgentPath = (Resolve-Path "$PSScriptRoot\..\endpoint_agent").Path,

    [string]$TaskName = "Sentinel Endpoint Agent",

    [string]$PythonCommand = "py"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $AgentPath)) {
    throw "Agent path not found: $AgentPath"
}

Write-Host "Installing endpoint agent dependencies..."
Push-Location $AgentPath
& $PythonCommand -m pip install -r requirements.txt
Pop-Location

$agentCommand = @"
`$env:SENTINEL_SERVER_URL='$ServerUrl'
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
