param(
    [string]$RootDir = "D:\Life\SKILLs",
    [string]$OutputFile = "D:\Life\SKILLs\README.md"
)

$ErrorActionPreference = "Stop"

$fallbackDescriptions = @{
    "edge-tts"         = "Text-to-speech generation with Edge TTS voices."
    "feishu-doc"       = "Feishu/Lark document operations (create, read, update, search)."
    "feishu-drive"     = "Feishu/Lark Drive file and folder management."
    "feishu-perm"      = "Feishu/Lark permission and sharing management."
    "feishu-wiki"      = "Feishu/Lark wiki space and node operations."
    "Humanizer-zh-main" = "Chinese text humanization and style polishing workflows."
}

function Get-SkillDescription {
    param([string]$RawText)

    $desc = $null
    if ($RawText -match '(?ms)^---\s*(.*?)\s*---') {
        $frontMatter = $Matches[1]
        if ($frontMatter -match '(?mi)^description\s*:\s*(.+)$') {
            $desc = $Matches[1].Trim().Trim('"', "'")
        }
    }

    if (-not $desc) {
        $lines = $RawText -split "`r?`n"
        foreach ($line in $lines) {
            $t = $line.Trim()
            if (-not $t) { continue }
            if ($t -eq "---") { continue }
            if ($t -match '^#') { continue }
            if ($t -match '^name\s*:') { continue }
            if ($t -match '^description\s*:') { continue }
            if ($t -match '^```') { continue }
            if ($t -match '^\*\*') { continue }
            $desc = $t
            break
        }
    }

    if (-not $desc) { $desc = "(description not provided)" }
    return $desc
}

function Test-InvalidDescription {
    param([string]$Text)

    $t = $Text.Trim()
    if (-not $t) { return $true }
    if ($t -notmatch '\w') { return $true }
    return $false
}

function Normalize-Text {
    param(
        [string]$Text,
        [int]$MaxLen = 110
    )

    $t = ($Text -replace '\s+', ' ').Trim()
    if ($t.Length -gt $MaxLen) {
        return $t.Substring(0, $MaxLen - 3) + "..."
    }
    return $t
}

function Escape-Markdown {
    param([string]$Text)
    return ($Text -replace '\|', '\\|')
}

$rootFull = (Resolve-Path -Path $RootDir).Path.TrimEnd('\')
$skillFiles = rg --files -g "**/SKILL.md" $RootDir
$items = @()

foreach ($file in $skillFiles) {
    $path = if ([System.IO.Path]::IsPathRooted($file)) {
        $file
    } else {
        Join-Path $RootDir $file
    }

    if ($path.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        $relative = $path.Substring($rootFull.Length).TrimStart('\', '/')
    } else {
        $relative = $path
    }
    $relative = $relative.Replace("\", "/")
    $raw = Get-Content -Raw -Path $path -Encoding UTF8

    $parent = Split-Path -Path $relative -Parent
    $skillName = Split-Path -Path $parent -Leaf
    if (-not $skillName) {
        $skillName = Split-Path -Path $relative -LeafBase
    }

    $desc = Get-SkillDescription -RawText $raw
    if (Test-InvalidDescription -Text $desc) {
        if ($fallbackDescriptions.ContainsKey($skillName)) {
            $desc = $fallbackDescriptions[$skillName]
        } else {
            $desc = "Utility skill for $skillName."
        }
    }
    $desc = Normalize-Text -Text $desc

    $items += [pscustomobject]@{
        skill       = $skillName
        path        = $relative
        description = $desc
    }
}

$items = $items | Sort-Object skill, path
$generatedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# SKILL Catalog")
$lines.Add("")
$lines.Add("This catalog lists all skills under D:\Life\SKILLs. The same content is synced to your GitHub cloud repository.")
$lines.Add("")
$lines.Add("- Total skills: $($items.Count)")
$lines.Add("- Generated at: $generatedAt")
$lines.Add("- Description source: each skill SKILL.md description field (fallback: first meaningful line)")
$lines.Add("")
$lines.Add("## Skills Index")
$lines.Add("")
$lines.Add("| Skill | Purpose | Path |")
$lines.Add("| --- | --- | --- |")

foreach ($item in $items) {
    $skill = Escape-Markdown -Text $item.skill
    $desc = Escape-Markdown -Text $item.description
    $path = Escape-Markdown -Text $item.path
    $lines.Add("| $skill | $desc | $path |")
}

$lines -join "`r`n" | Set-Content -Path $OutputFile -Encoding UTF8
Write-Host "README generated: $OutputFile"
Write-Host "Rows: $($items.Count)"
