# SKILL Directory Sync Check Script
# Checks synchronization between Unified, LobsterAI, and all OpenClaw skill directories

$UnifiedPath = "D:\Life\SKILLs"
$LobsterPath = "C:\Users\Administrator\AppData\Roaming\LobsterAI\SKILLs"

# OpenClaw has multiple skill directories
$OpenClawPaths = @(
    "C:\Users\Administrator\.openclaw\workspace\skills",
    "C:\Users\Administrator\clawd\skills",
    "C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\skills",
    "C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\extensions\feishu\skills"
)

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
        Get-ChildItem -Path $Path -Directory -Exclude "sync-check.ps1","*.bat" | ForEach-Object {
            $hashes[$_.Name] = $true
        }
    }
    return $hashes
}

function Get-AllOpenClawSkills {
    $allSkills = @{}
    foreach ($path in $OpenClawPaths) {
        if (Test-Path $path) {
            $skills = Get-SkillHashes -Path $path
            foreach ($key in $skills.Keys) {
                $allSkills[$key] = $true
            }
        }
    }
    return $allSkills
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
        Write-Log "[DIFF] Only in $Name1 ($($onlyIn1.Count) skills):"
        foreach ($skill in $onlyIn1) { Write-Log "  - $skill" }
        $diff = $true
    }
    $onlyIn2 = $Skills2.Keys | Where-Object { $_ -notin $Skills1.Keys }
    if ($onlyIn2) {
        Write-Log "[DIFF] Only in $Name2 ($($onlyIn2.Count) skills):"
        foreach ($skill in $onlyIn2) { Write-Log "  - $skill" }
        $diff = $true
    }
    return $diff
}

Write-Log "========== Sync Check Started =========="

$UnifiedSkills = Get-SkillHashes -Path $UnifiedPath
$LobsterSkills = Get-SkillHashes -Path $LobsterPath
$OpenClawSkills = Get-AllOpenClawSkills

Write-Log "Unified skills count: $($UnifiedSkills.Count)"
Write-Log "LobsterAI skills count: $($LobsterSkills.Count)"
Write-Log "OpenClaw total skills (all dirs): $($OpenClawSkills.Count)"

# Check individual OpenClaw directories
foreach ($path in $OpenClawPaths) {
    if (Test-Path $path) {
        $skills = Get-SkillHashes -Path $path
        Write-Log "  - $path : $($skills.Count) skills"
    } else {
        Write-Log "  - $path : NOT FOUND"
    }
}

$hasDiff = $false

Write-Log "`n[Check] Unified vs LobsterAI"
if (Compare-Skills -Name1 "Unified" -Skills1 $UnifiedSkills -Name2 "LobsterAI" -Skills2 $LobsterSkills) { $hasDiff = $true }

Write-Log "`n[Check] Unified vs OpenClaw (all dirs combined)"
if (Compare-Skills -Name1 "Unified" -Skills1 $UnifiedSkills -Name2 "OpenClaw" -Skills2 $OpenClawSkills) { $hasDiff = $true }

Write-Log "`n[Check] LobsterAI vs OpenClaw"
if (Compare-Skills -Name1 "LobsterAI" -Skills1 $LobsterSkills -Name2 "OpenClaw" -Skills2 $OpenClawSkills) { $hasDiff = $true }

if ($hasDiff) {
    Write-Log "`n[WARNING] Skill directories are NOT in sync!"
    Write-Log "[INFO] This is expected if some skills are platform-specific."
    exit 1
} else {
    Write-Log "`n[OK] All directories are in sync"
    exit 0
}
