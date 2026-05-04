param(
    [string]$TaskName = "SKILLs-Daily-GitHub-Sync",
    [string]$RunTime = "02:00",
    [string]$SyncScript = "D:\Life\SKILLs\sync-to-github.ps1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path $SyncScript)) {
    throw "Sync script not found: $SyncScript"
}

$taskAction = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$SyncScript`""

$taskTrigger = New-ScheduledTaskTrigger -Daily -At $RunTime

$taskSettings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $taskAction `
    -Trigger $taskTrigger `
    -Settings $taskSettings `
    -Description "Daily sync D:\Life\SKILLs to GitHub Richard0901/SKILL-warehouse" `
    -Force | Out-Null

Write-Host "Task registered: $TaskName at $RunTime"
Write-Host "You can test it now with:"
Write-Host "Start-ScheduledTask -TaskName `"$TaskName`""
