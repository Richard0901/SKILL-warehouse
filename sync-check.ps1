# SKILL Directory Sync Check Script
$UnifiedPath = "D:\Life\SKILLs"
$LobsterPath = "C:\Users\Administrator\AppData\Roaming\LobsterAI\SKILLs"
$OpenClawPath = "C:\Users\Administrator\.openclaw\workspace\skills"
$LogPath = "D:\Life\SKILLs\sync-check.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $LogPath -Value $logEntry -Encoding UTF8
    Write-Host $logEntry
}

function Get-SkillHashes {
    param([string]$Path)
    $hashes = @{}
    if (Test-Path $Path) {
        Get-ChildItem -Path $Path -Directory -Exclude "sync-check.ps1" | ForEach-Object {
            $hashes[$_.Name] = $true
        }
    }
    return $hashes
}

function Compare-Skills {
    param(
        [string]$Name1,
        [hashtable]$Skills1,
        [string]$Name2,
        [hashtable]$Skills2
    )
    $diff = $false
    $onlyIn1 = $Skills1.Keys | Where-Object { $_ -notin $Skills2.Keys }
    if ($onlyIn1) {
        Write-Log "[DIFF] Only in $Name1 :"
        foreach ($skill in $onlyIn1) { Write-Log "  - $skill" }
        $diff = $true
    }
    $onlyIn2 = $Skills2.Keys | Where-Object { $_ -notin $Skills1.Keys }
    if ($onlyIn2) {
        Write-Log "[DIFF] Only in $Name2 :"
        foreach ($skill in $onlyIn2) { Write-Log "  - $skill" }
        $diff = $true
    }
    return $diff
}

Write-Log "========== Sync Check Started =========="
$UnifiedSkills = Get-SkillHashes -Path $UnifiedPath
$LobsterSkills = Get-SkillHashes -Path $LobsterPath
$OpenClawSkills = Get-SkillHashes -Path $OpenClawPath

Write-Log "Unified skills count: $($UnifiedSkills.Count)"
Write-Log "LobsterAI skills count: $($LobsterSkills.Count)"
Write-Log "OpenClaw skills count: $($OpenClawSkills.Count)"

$hasDiff = $false

Write-Log "[Check] Unified vs LobsterAI"
if (Compare-Skills -Name1 "Unified" -Skills1 $UnifiedSkills -Name2 "LobsterAI" -Skills2 $LobsterSkills) { $hasDiff = $true }

Write-Log "[Check] Unified vs OpenClaw"
if (Compare-Skills -Name1 "Unified" -Skills1 $UnifiedSkills -Name2 "OpenClaw" -Skills2 $OpenClawSkills) { $hasDiff = $true }

Write-Log "[Check] LobsterAI vs OpenClaw"
if (Compare-Skills -Name1 "LobsterAI" -Skills1 $LobsterSkills -Name2 "OpenClaw" -Skills2 $OpenClawSkills) { $hasDiff = $true }

if ($hasDiff) {
    Write-Log "[WARNING] Skill directories are NOT in sync!"
    exit 1
} else {
    Write-Log "[OK] All directories are in sync"
    exit 0
}
