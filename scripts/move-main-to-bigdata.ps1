[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    # Path to the current (main) project folder to move.
    [Parameter()]
    [string] $SourcePath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,

    # Target folder where the main project should live.
    # IMPORTANT: This script will NOT create this folder.
    [Parameter()]
    [string] $DestinationPath = 'D:\Code\Project_BigData',

    # Optional: path to the clone folder that was created as a git worktree.
    # If provided with -DetachClone, this script will detach it from the main repo
    # (so it will no longer depend on SourcePath's .git).
    [Parameter()]
    [string] $ClonePath = 'D:\Bai Luan\Nam 2025 - 2026\HocKyII\CDIO_3\Project\CRM-AI-Agent-CDIO3',

    # Detach the clone from the main repo BEFORE moving, to avoid broken worktree links.
    [Parameter()]
    [switch] $DetachClone,

    # After successful copy, attempt to delete SourcePath (best-effort).
    # Note: deletion may fail if files are locked/open.
    [Parameter()]
    [switch] $RemoveSource
)

$ErrorActionPreference = 'Stop'

function Write-Step([string] $Message) {
    Write-Host "\n=== $Message ===" -ForegroundColor Cyan
}

function Assert-PathExists([string] $Path, [string] $Label) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label does not exist: $Path"
    }
}

function Get-IsGitWorktree([string] $RepoPath) {
    $gitFile = Join-Path $RepoPath '.git'
    if (-not (Test-Path -LiteralPath $gitFile)) { return $false }

    # In a worktree, .git is typically a FILE containing a gitdir pointer.
    $item = Get-Item -LiteralPath $gitFile
    if ($item.PSIsContainer) { return $false }

    try {
        $content = Get-Content -LiteralPath $gitFile -ErrorAction Stop | Select-Object -First 1
    } catch {
        return $false
    }

    return ($content -match '^gitdir:')
}

function Detach-Clone([string] $ClonePath) {
    Assert-PathExists -Path $ClonePath -Label 'ClonePath'

    if (-not (Get-IsGitWorktree -RepoPath $ClonePath)) {
        Write-Host "Clone is not a git worktree (or already detached): $ClonePath" -ForegroundColor Yellow
        return
    }

    Write-Step "Detaching clone from main repo (worktree -> standalone)"
    Write-Host "ClonePath: $ClonePath" -ForegroundColor Gray

    $gitFile = Join-Path $ClonePath '.git'
    if ($PSCmdlet.ShouldProcess($gitFile, 'Remove worktree .git pointer file')) {
        if (-not $WhatIfPreference) {
            Remove-Item -LiteralPath $gitFile -Force
        } else {
            Write-Host "[WhatIf] Would remove: $gitFile" -ForegroundColor DarkYellow
        }
    }

    if ($PSCmdlet.ShouldProcess($ClonePath, 'Initialize new standalone git repository')) {
        if (-not $WhatIfPreference) {
            Push-Location $ClonePath
            try {
                git init | Out-String | Write-Host
                git add -A
                # Commit can fail if git user.name/email not set; that's OK.
                git commit -m "chore: detach clone repo" | Out-String | Write-Host
            } finally {
                Pop-Location
            }
        } else {
            Write-Host "[WhatIf] Would run: git init; git add -A; git commit ... in $ClonePath" -ForegroundColor DarkYellow
        }
    }

    Write-Host "Detached clone successfully (no longer depends on main repo's .git)." -ForegroundColor Green
}

Write-Step 'Pre-flight checks'
Assert-PathExists -Path $SourcePath -Label 'SourcePath'
Assert-PathExists -Path $DestinationPath -Label 'DestinationPath'

if ((Resolve-Path -LiteralPath $SourcePath).Path.TrimEnd('\\') -ieq (Resolve-Path -LiteralPath $DestinationPath).Path.TrimEnd('\\')) {
    throw 'SourcePath and DestinationPath are the same. Aborting.'
}

# Safety: Ensure Source looks like the CRM-AI-Agent repo
$expected = @('backend', 'frontend', 'docker-compose.yml')
foreach ($e in $expected) {
    $p = Join-Path $SourcePath $e
    if (-not (Test-Path -LiteralPath $p)) {
        throw "SourcePath doesn't look like the expected project root (missing $e): $SourcePath"
    }
}

# Optional: detach clone first so worktree pointer won't break after move
if ($DetachClone) {
    Detach-Clone -ClonePath $ClonePath
}

Write-Step 'Copy (mirror) source -> destination'
Write-Host "SourcePath:      $SourcePath" -ForegroundColor Gray
Write-Host "DestinationPath: $DestinationPath" -ForegroundColor Gray

# Use robocopy for robust copy/mirror behavior.
# /MIR mirrors directories (including deletions in destination).
# /R:1 /W:1 keep retries short.
$robocopyArgs = @(
    $SourcePath,
    $DestinationPath,
    '/MIR',
    '/R:1',
    '/W:1',
    '/COPY:DAT',
    '/DCOPY:DAT'
)

$robocopyPreview = 'robocopy ' + ('"' + $SourcePath + '"') + ' ' + ('"' + $DestinationPath + '"') + ' ' + (($robocopyArgs | Select-Object -Skip 2) -join ' ')

if ($WhatIfPreference) {
    Write-Host "[WhatIf] Would run: $robocopyPreview" -ForegroundColor DarkYellow
} else {
    Write-Host "Running: $robocopyPreview" -ForegroundColor Gray
    & robocopy @robocopyArgs | Out-Host

    # Robocopy uses exit codes with bit flags; 0-7 are typically success.
    $exitCode = $LASTEXITCODE
    if ($exitCode -ge 8) {
        throw "Robocopy failed with exit code $exitCode"
    }
}

Write-Step 'Post-copy sanity checks'
$destBackend = Join-Path $DestinationPath 'backend'
$destFrontend = Join-Path $DestinationPath 'frontend'
$destCompose = Join-Path $DestinationPath 'docker-compose.yml'

foreach ($p in @($destBackend, $destFrontend, $destCompose)) {
    if (-not (Test-Path -LiteralPath $p)) {
        throw "Destination is missing expected path after copy: $p"
    }
}

Write-Host 'Destination looks OK.' -ForegroundColor Green

if ($RemoveSource) {
    Write-Step 'Removing source folder (best-effort)'
    Write-Host "SourcePath: $SourcePath" -ForegroundColor Gray
    if ($PSCmdlet.ShouldProcess($SourcePath, 'Delete source folder')) {
        if (-not $WhatIfPreference) {
            # Avoid deleting while current working dir is inside SourcePath
            Set-Location $env:TEMP
            try {
                Remove-Item -LiteralPath $SourcePath -Recurse -Force
                Write-Host 'Removed source folder.' -ForegroundColor Green
            } catch {
                Write-Host "WARNING: Failed to remove source folder (likely locked). You can delete it manually later. Error: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[WhatIf] Would delete: $SourcePath" -ForegroundColor DarkYellow
        }
    }
}

Write-Step 'Next steps'
Write-Host "- Open the moved main project at: $DestinationPath" -ForegroundColor Gray
Write-Host "- If you detached the clone, it is now standalone at: $ClonePath" -ForegroundColor Gray
Write-Host "- After you create new private remotes, set them with: git remote remove origin; git remote add origin <url>" -ForegroundColor Gray
