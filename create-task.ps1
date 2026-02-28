# Create Scheduled Task for SKILL Sync Check
$now = Get-Date
$trigger = New-ScheduledTaskTrigger -Once $now -RepetitionInterval (New-TimeSpan -Hours 1)
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-ExecutionPolicy Bypass -File D:\Life\SKILLs\sync-check.ps1'
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet

Register-ScheduledTask -TaskName 'SKILL_Sync_Check' -Trigger $trigger -Action $action -Principal $principal -Settings $settings -Force

Write-Host "Scheduled task created successfully!"
Get-ScheduledTask -TaskName 'SKILL_Sync_Check'
