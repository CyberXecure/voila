# v0.7.20 controlled tester ZIP preparation, no delivery
# Hotfix 1: pass -AllowDirtyWorktree into v0.7.19b pre-ZIP smoke gate while milestone files are uncommitted.
# Creates a local controlled tester ZIP candidate only.
# Policy: ZIP preparation allowed; no installer, no OneDrive share, no GitHub release, no delivery, no distribution.
# Expected marker:
# VOILA_V0_7_20_CONTROLLED_TESTER_ZIP_PREPARATION_NO_DELIVERY_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$ReleaseRoot = "D:\dev\release-assets\voila\v0.7.20-controlled-tester-zip-preparation-no-delivery",
    [string]$PackageName = "voila-v0.7.20-controlled-tester-windows-package-candidate",
    [switch]$AllowDirtyWorktree,
    [switch]$SkipPreZipSmoke,
    [switch]$ExcludeVenv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_20_CONTROLLED_TESTER_ZIP_PREPARATION_NO_DELIVERY_CHECK=PASS"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$ReleaseRootParent = Split-Path -Parent $ReleaseRoot
$ReleaseRootLeaf = Split-Path -Leaf $ReleaseRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Write-Pass {
    param([string]$Message)
    Write-Host "PASS: $Message"
}

function Write-WarnLine {
    param([string]$Message)
    Write-Host "WARN: $Message"
}

function Fail {
    param([string]$Message)
    throw "FAIL: $Message"
}

function Assert-File {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Assert-Dir {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Get-PythonExe {
    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
        return $venvPython
    }
    return "python"
}

function Invoke-PyCompile {
    param([string[]]$RelativePaths)

    $python = Get-PythonExe
    foreach ($rel in $RelativePaths) {
        $full = Join-Path $RepoRoot $rel
        if (Test-Path -LiteralPath $full -PathType Leaf) {
            Write-Host "py_compile: $rel"
            & $python -m py_compile $full
            if ($LASTEXITCODE -ne 0) {
                Fail "py_compile failed: $rel"
            }
            Write-Pass "py_compile $rel"
        }
        else {
            Write-WarnLine "py_compile target not present, skipped: $rel"
        }
    }
}

function Stop-VoilaIfPossible {
    $stopScript = Join-Path $RepoRoot "scripts\dev\stop-voila.ps1"
    if (Test-Path -LiteralPath $stopScript -PathType Leaf) {
        Write-Step "Stopping owner-local runtime if present"
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $stopScript -Silent
        if ($LASTEXITCODE -ne 0) {
            Write-WarnLine "stop-voila.ps1 returned exit code $LASTEXITCODE; continuing"
        }
    }
}

function New-CleanDirectory {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Invoke-RobocopyChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExtraArgs
    )

    $args = @($Source, $Destination, "/E", "/R:1", "/W:1", "/NFL", "/NDL", "/NP") + $ExtraArgs
    Write-Host "robocopy $($args -join ' ')"
    & robocopy @args | Out-Host
    $code = $LASTEXITCODE

    # Robocopy codes 0-7 are success / non-fatal copy states.
    if ($code -gt 7) {
        Fail "robocopy failed with exit code $code"
    }

    Write-Pass "robocopy completed with exit code $code"
}

function Write-PackageFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $dir = Split-Path -Parent $Path
    if ($dir) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Assert-NoPathInsideZipByPattern {
    param(
        [string]$ZipPath,
        [string[]]$ForbiddenPatterns
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName
            foreach ($pattern in $ForbiddenPatterns) {
                if ($name -match $pattern) {
                    Fail "forbidden ZIP entry detected: $name matches $pattern"
                }
            }
        }
    }
    finally {
        $zip.Dispose()
    }

    Write-Pass "forbidden ZIP entry scan passed"
}

function Get-ZipEntryCount {
    param([string]$ZipPath)

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        return @($zip.Entries).Length
    }
    finally {
        $zip.Dispose()
    }
}

Write-Host "SCRIPT_VERSION=v0.7.20-controlled-tester-zip-preparation-no-delivery-hotfix1"

Write-Step "v0.7.20 policy guard"
Assert-Dir $RepoRoot "repo root"
Assert-Dir (Join-Path $RepoRoot ".git") "git metadata"

Push-Location $RepoRoot
try {
    $topLevel = (& git rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0) { Fail "not a git repo" }
    if ((Resolve-Path -LiteralPath $topLevel).Path -ne $RepoRoot) {
        Fail "repo root mismatch: expected $RepoRoot but git top-level is $topLevel"
    }

    $branch = (& git branch --show-current).Trim()
    $head = (& git rev-parse --short HEAD).Trim()
    $fullHead = (& git rev-parse HEAD).Trim()
    Write-Host "BRANCH=$branch"
    Write-Host "HEAD=$head"

    $status = @(& git status --short)
    if (@($status).Length -gt 0 -and -not $AllowDirtyWorktree) {
        $status | ForEach-Object { Write-Host $_ }
        Fail "worktree is dirty. Use -AllowDirtyWorktree only while testing the new milestone files before commit."
    }
    elseif (@($status).Length -gt 0 -and $AllowDirtyWorktree) {
        Write-WarnLine "worktree is dirty but allowed for pre-commit milestone check"
        $status | ForEach-Object { Write-Host $_ }
    }
    else {
        Write-Pass "worktree clean"
    }

    Write-Host "ZIP_PREPARATION_ALLOWED=PASS"
    Write-Host "INSTALLER_CREATED=false"
    Write-Host "ONEDRIVE_SHARE_CREATED=false"
    Write-Host "GITHUB_RELEASE_CREATED=false"
    Write-Host "DELIVERY_PERFORMED=false"
    Write-Host "DISTRIBUTION_PERFORMED=false"

    Write-Step "Required baseline checks"
    $v019bCheck = Join-Path $RepoRoot "scripts\dev\check-owner-local-route-real-smoke-before-zip-no-build-no-distribution.ps1"
    $v019bDoc = Join-Path $RepoRoot "docs\dev\v0.7.19b-owner-local-route-real-smoke-before-zip-no-build-no-distribution.md"
    Assert-File $v019bCheck "v0.7.19b check script"
    Assert-File $v019bDoc "v0.7.19b doc"

    $v019bText = Get-Content -LiteralPath $v019bCheck -Raw -Encoding UTF8
    if ($v019bText -notmatch "VOILA_V0_7_19B_OWNER_LOCAL_ROUTE_REAL_SMOKE_BEFORE_ZIP_CHECK=PASS") {
        Fail "v0.7.19b final marker missing from v0.7.19b script"
    }
    Write-Pass "v0.7.19b marker present in check script"

    Write-Step "Python syntax sanity"
    Invoke-PyCompile @(
        "services/api/web_app.py",
        "services/api/exam_prep.py",
        "services/api/study_quiz_builder.py",
        "services/api/ocr_math_report.py",
        "services/api/ocr_math_normalizer.py"
    )

    if (-not $SkipPreZipSmoke) {
        Write-Step "Pre-ZIP owner-local route smoke gate: v0.7.19b"
        $preZipGateArgs = @()
        if ($AllowDirtyWorktree) {
            $preZipGateArgs += "-AllowDirtyWorktree"
        }
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $v019bCheck @preZipGateArgs
        if ($LASTEXITCODE -ne 0) {
            Fail "v0.7.19b pre-ZIP smoke gate failed"
        }
        Write-Pass "v0.7.19b pre-ZIP smoke gate passed"
        Stop-VoilaIfPossible
    }
    else {
        Write-WarnLine "pre-ZIP smoke gate skipped by parameter"
    }

    Write-Step "Prepare controlled local release asset root"
    New-Item -ItemType Directory -Force -Path $ReleaseRootParent | Out-Null
    New-CleanDirectory -Path $ReleaseRoot

    $stagingRoot = Join-Path $ReleaseRoot $PackageName
    $zipPath = Join-Path $ReleaseRoot "$PackageName.zip"
    $shaPath = "$zipPath.sha256"
    $manifestPath = Join-Path $ReleaseRoot "ZIP-PREPARATION-MANIFEST.json"
    $summaryPath = Join-Path $ReleaseRoot "ZIP-PREPARATION-SUMMARY.txt"
    $noDeliveryPath = Join-Path $ReleaseRoot "NO-DELIVERY-NOTICE.txt"

    New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

    Write-Step "Stage package files from repo"
    $excludeDirs = @(
        (Join-Path $RepoRoot ".git"),
        (Join-Path $RepoRoot "data"),
        (Join-Path $RepoRoot ".release-cache"),
        (Join-Path $RepoRoot "node_modules"),
        (Join-Path $RepoRoot ".pytest_cache"),
        (Join-Path $RepoRoot ".mypy_cache"),
        (Join-Path $RepoRoot ".ruff_cache"),
        (Join-Path $RepoRoot ".next"),
        (Join-Path $RepoRoot "dist"),
        (Join-Path $RepoRoot "build")
    )

    if ($ExcludeVenv) {
        $excludeDirs += (Join-Path $RepoRoot ".venv")
    }

    $excludeFiles = @(
        "*.pyc",
        "*.pyo",
        "*.log",
        "*.tmp",
        ".env",
        ".env.*",
        "*.zip",
        "*.7z",
        "*.rar"
    )

    $robocopyArgs = @("/XD") + $excludeDirs + @("/XF") + $excludeFiles
    Invoke-RobocopyChecked -Source $RepoRoot -Destination $stagingRoot -ExtraArgs $robocopyArgs

    Write-Step "Add package-only tester files"
    New-Item -ItemType Directory -Force -Path (Join-Path $stagingRoot "data\input") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $stagingRoot "data\output") | Out-Null
    Write-PackageFile -Path (Join-Path $stagingRoot "data\README-EMPTY-DATA.txt") -Content @"
This tester package intentionally ships with empty local data directories.

Do not upload confidential, personal, legal, medical, financial, safety-critical, or otherwise sensitive PDFs during testing.
"@

    Write-PackageFile -Path (Join-Path $stagingRoot "START-VOILA.bat") -Content @"
@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\start-voila.ps1"
"@

    Write-PackageFile -Path (Join-Path $stagingRoot "STOP-VOILA.bat") -Content @"
@echo off
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\dev\stop-voila.ps1" -Silent
pause
"@

    Write-PackageFile -Path (Join-Path $stagingRoot "README-TESTERS-v0.7.20.txt") -Content @"
Voila controlled tester package candidate v0.7.20

This is a controlled local Windows tester ZIP candidate prepared for owner review.

Important:
- No delivery was performed by this script.
- No OneDrive share was created by this script.
- No GitHub release was created by this script.
- Do not distribute this package until a separate delivery/distribution milestone is explicitly approved.

Basic local start:
1. Extract the ZIP to a local folder.
2. Run START-VOILA.bat.
3. Open http://127.0.0.1:8787/ if it does not open automatically.
4. Use only small, non-confidential PDFs for testing.

Testing focus:
- Upload
- Generate
- Course view
- Study
- Progress
- OCR Review / corrected OCR
- OCR Math report/viewer
- Exam Prep
- Quick tools
"@

    Write-PackageFile -Path (Join-Path $stagingRoot "NO-DELIVERY-NOTICE.txt") -Content @"
NO DELIVERY / NO DISTRIBUTION NOTICE

This ZIP was prepared locally only.

delivery_performed=false
distribution_performed=false
onedrive_share_created=false
github_release_created=false
installer_created=false

Separate explicit approval is required before any tester delivery, share link, GitHub release, upload, or distribution.
"@

    Write-Step "Package content validation before ZIP"
    Assert-File (Join-Path $stagingRoot "services\api\web_app.py") "staged web_app.py"
    Assert-File (Join-Path $stagingRoot "scripts\dev\start-voila.ps1") "staged start-voila.ps1"
    Assert-File (Join-Path $stagingRoot "scripts\dev\stop-voila.ps1") "staged stop-voila.ps1"
    Assert-File (Join-Path $stagingRoot "START-VOILA.bat") "package START-VOILA.bat"
    Assert-File (Join-Path $stagingRoot "STOP-VOILA.bat") "package STOP-VOILA.bat"
    Assert-File (Join-Path $stagingRoot "README-TESTERS-v0.7.20.txt") "package tester README"
    Assert-File (Join-Path $stagingRoot "NO-DELIVERY-NOTICE.txt") "package no-delivery notice"

    if (Test-Path -LiteralPath (Join-Path $stagingRoot ".git")) {
        Fail "staged package unexpectedly contains .git"
    }
    if (Test-Path -LiteralPath (Join-Path $stagingRoot ".release-cache")) {
        Fail "staged package unexpectedly contains .release-cache"
    }

    $stagedInputFiles = @(
        Get-ChildItem -LiteralPath (Join-Path $stagingRoot "data\input") -Recurse -File -ErrorAction SilentlyContinue
    )
    $stagedOutputFiles = @(
        Get-ChildItem -LiteralPath (Join-Path $stagingRoot "data\output") -Recurse -File -ErrorAction SilentlyContinue
    )
    if (@($stagedInputFiles).Length -gt 0 -or @($stagedOutputFiles).Length -gt 0) {
        Fail "staged package contains local data input/output files"
    }
    Write-Pass "staged data/input and data/output are empty"

    $venvIncluded = Test-Path -LiteralPath (Join-Path $stagingRoot ".venv") -PathType Container
    Write-Host "venv_included=$venvIncluded"

    Write-Step "Create local ZIP candidate"
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $stagingRoot,
        $zipPath,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )

    Assert-File $zipPath "controlled tester ZIP candidate"

    $hash = Get-FileHash -LiteralPath $zipPath -Algorithm SHA256
    $shaLine = "$($hash.Hash)  $(Split-Path -Leaf $zipPath)"
    Set-Content -LiteralPath $shaPath -Value $shaLine -Encoding ASCII
    Assert-File $shaPath "ZIP SHA256 file"

    $zipItem = Get-Item -LiteralPath $zipPath
    $entryCount = Get-ZipEntryCount -ZipPath $zipPath
    Write-Host "zip_path=$zipPath"
    Write-Host "zip_sha256=$($hash.Hash)"
    Write-Host "zip_size_bytes=$($zipItem.Length)"
    Write-Host "zip_entry_count=$entryCount"

    Assert-NoPathInsideZipByPattern -ZipPath $zipPath -ForbiddenPatterns @(
        "^\.git/",
        "^\.release-cache/",
        "^data/input/.+",
        "^data/output/.+",
        "\.env($|/)",
        "\.zip$"
    )

    Write-Step "Write manifest and no-delivery summary"
    $manifest = [ordered]@{
        milestone = "v0.7.20-controlled-tester-zip-preparation-no-delivery"
        package_name = $PackageName
        repo_root = $RepoRoot
        git_branch = $branch
        git_head_short = $head
        git_head = $fullHead
        release_root = $ReleaseRoot
        staging_root = $stagingRoot
        zip_path = $zipPath
        sha256_path = $shaPath
        sha256 = $hash.Hash
        zip_size_bytes = $zipItem.Length
        zip_entry_count = $entryCount
        venv_included = [bool]$venvIncluded
        data_input_output_empty = $true
        installer_created = $false
        onedrive_share_created = $false
        github_release_created = $false
        delivery_performed = $false
        distribution_performed = $false
        policy = "controlled local ZIP preparation only; no delivery; no distribution"
        final_marker = $Marker
    }

    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Assert-File $manifestPath "ZIP preparation manifest"

    $summary = @"
Voila v0.7.20 controlled tester ZIP preparation — no delivery

package_name=$PackageName
git_branch=$branch
git_head=$head
zip_path=$zipPath
sha256=$($hash.Hash)
sha256_path=$shaPath
zip_size_bytes=$($zipItem.Length)
zip_entry_count=$entryCount
venv_included=$venvIncluded

Policy:
installer_created=false
onedrive_share_created=false
github_release_created=false
delivery_performed=false
distribution_performed=false

This milestone prepares a local ZIP candidate only.
Separate explicit approval is required before any tester delivery/share/distribution.
"@
    Set-Content -LiteralPath $summaryPath -Value $summary -Encoding UTF8
    Set-Content -LiteralPath $noDeliveryPath -Value "delivery_performed=false`ndistribution_performed=false`nonedrive_share_created=false`ngithub_release_created=false`n" -Encoding UTF8
    Assert-File $summaryPath "ZIP preparation summary"
    Assert-File $noDeliveryPath "release-root no-delivery notice"

    Write-Step "Final v0.7.20 result"
    Write-Host "controlled_tester_zip_prepared=true"
    Write-Host "zip_created=true"
    Write-Host "zip_path=$zipPath"
    Write-Host "zip_sha256=$($hash.Hash)"
    Write-Host "sha256_path=$shaPath"
    Write-Host "manifest_path=$manifestPath"
    Write-Host "summary_path=$summaryPath"
    Write-Host "installer_created=false"
    Write-Host "onedrive_share_created=false"
    Write-Host "github_release_created=false"
    Write-Host "delivery_performed=false"
    Write-Host "distribution_performed=false"
    Write-Host "NO_DELIVERY=PASS"
    Write-Host "NO_DISTRIBUTION=PASS"
    Write-Host $Marker
}
finally {
    Pop-Location
}
