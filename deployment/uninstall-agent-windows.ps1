param(
    [string]$TaskName = "Sentinel Endpoint Agent"
)

$ErrorActionPreference = "Stop"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($task) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Sentinel Endpoint Agent scheduled task removed."
} else {
    Write-Host "Sentinel Endpoint Agent scheduled task was not found."
}
