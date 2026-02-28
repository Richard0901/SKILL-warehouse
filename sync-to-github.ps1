param(
    [string]$SourceDir = "D:\Life\SKILLs",
    [string]$RepoDir = "D:\Life\private\SKILL-warehouse",
    [string]$RepoUrl = "https://github.com/Richard0901/SKILL-warehouse.git",
    [string]$Branch = "main",
    [string]$LogPath = "D:\Life\private\skill-github-sync.log",
    [string]$GitUserName = "Richard0901",
    [string]$GitUserEmail = "richard0901@users.noreply.github.com"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp][$Level] $Message"
    Write-Host $line
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
}

function Invoke-Git {
    param(
        [string]$WorkingDir,
        [string[]]$GitArgs
    )

    $prevErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git -C $WorkingDir @GitArgs 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prevErrorAction
    }

    if ($exitCode -ne 0) {
        $details = ($output -join [Environment]::NewLine)
        throw "git $($GitArgs -join ' ') failed with exit code $exitCode`n$details"
    }
}

try {
    $sourcePath = (Resolve-Path -Path $SourceDir).Path
    $repoPath = [System.IO.Path]::GetFullPath($RepoDir)
    $logDir = Split-Path -Path $LogPath -Parent

    if (-not (Test-Path -Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    if ($repoPath.StartsWith($sourcePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "RepoDir cannot be inside SourceDir. Please use a separate folder."
    }

    Write-Log "Sync started. source=$sourcePath repo=$repoPath branch=$Branch"

    & git --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "git is not available in PATH."
    }

    if (-not (Test-Path -Path $repoPath)) {
        $repoParent = Split-Path -Path $repoPath -Parent
        if (-not (Test-Path -Path $repoParent)) {
            New-Item -ItemType Directory -Path $repoParent -Force | Out-Null
        }
        Write-Log "Local repo not found. Cloning $RepoUrl ..."
        & git clone --branch $Branch $RepoUrl $repoPath
        if ($LASTEXITCODE -ne 0) {
            throw "git clone failed with exit code $LASTEXITCODE"
        }
    }

    if (-not (Test-Path -Path (Join-Path $repoPath ".git"))) {
        throw "$repoPath exists but is not a git repository."
    }

    $currentUserName = (& git -C $repoPath config --get user.name)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($currentUserName -join "").Trim())) {
        Write-Log "Setting repository git user.name to $GitUserName"
        Invoke-Git -WorkingDir $repoPath -GitArgs @("config", "user.name", $GitUserName)
    }

    $currentUserEmail = (& git -C $repoPath config --get user.email)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($currentUserEmail -join "").Trim())) {
        Write-Log "Setting repository git user.email to $GitUserEmail"
        Invoke-Git -WorkingDir $repoPath -GitArgs @("config", "user.email", $GitUserEmail)
    }

    Invoke-Git -WorkingDir $repoPath -GitArgs @("config", "core.autocrlf", "false")
    Invoke-Git -WorkingDir $repoPath -GitArgs @("config", "core.safecrlf", "false")

    Write-Log "Preparing local mirror branch ..."
    & cmd /c "git -C `"$repoPath`" rebase --abort >nul 2>nul"
    & cmd /c "git -C `"$repoPath`" merge --abort >nul 2>nul"
    Invoke-Git -WorkingDir $repoPath -GitArgs @("reset", "--hard")
    Invoke-Git -WorkingDir $repoPath -GitArgs @("clean", "-fd")
    Invoke-Git -WorkingDir $repoPath -GitArgs @("fetch", "origin", $Branch)
    Invoke-Git -WorkingDir $repoPath -GitArgs @("checkout", "-B", $Branch, "origin/$Branch")

    Write-Log "Mirroring files from source to repo ..."
    $robocopyArgs = @(
        $sourcePath,
        $repoPath,
        "/MIR",
        "/R:2",
        "/W:3",
        "/XJ",
        "/NFL",
        "/NDL",
        "/NP",
        "/XD", ".git",
        "/XF", "sync-check.log", "sync-github.log", "skill-github-sync.log"
    )
    & robocopy @robocopyArgs | Out-Null
    $robocopyExit = $LASTEXITCODE
    if ($robocopyExit -ge 8) {
        throw "robocopy failed with exit code $robocopyExit"
    }

    Invoke-Git -WorkingDir $repoPath -GitArgs @("add", "-A")
    $status = & git -C $repoPath status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed with exit code $LASTEXITCODE"
    }

    if ([string]::IsNullOrWhiteSpace(($status -join ""))) {
        Write-Log "No file changes detected. Nothing to commit."
        exit 0
    }

    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Invoke-Git -WorkingDir $repoPath -GitArgs @("commit", "-m", "chore(sync): skills update $stamp")
    Invoke-Git -WorkingDir $repoPath -GitArgs @("push", "origin", $Branch)

    Write-Log "Sync completed and pushed successfully."
    exit 0
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}
