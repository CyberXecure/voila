param(
    [string]$ProjectRoot = "",
    [string]$ReleaseRoot = "D:\dev\releases",
    [string]$VersionTag = "",
    [string]$ZipPath = "",
    [string]$WorkRoot = "",
    [switch]$SkipIfMissing,
    [switch]$KeepTemp
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

$StandaloneSmokeScript = Join-Path $ProjectRoot "scripts\release\smoke-language-pack-standalone-package.ps1"

if (-not (Test-Path $StandaloneSmokeScript)) {
    throw "Standalone smoke script missing: $StandaloneSmokeScript"
}

function Find-LatestVoilaZip {
    param([string]$Root)

    if (-not (Test-Path $Root)) {
        return $null
    }

    $zips = Get-ChildItem -Path $Root -Filter "*.zip" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "voila" } |
        Sort-Object LastWriteTime -Descending

    if ($zips.Count -eq 0) {
        return $null
    }

    return $zips[0].FullName
}

Write-Host "=== Voila language-pack build output smoke ==="
Write-Host "ProjectRoot:   $ProjectRoot"
Write-Host "ReleaseRoot:   $ReleaseRoot"
Write-Host "VersionTag:    $VersionTag"
Write-Host "ZipPath input: $ZipPath"
Write-Host "SkipIfMissing: $SkipIfMissing"
Write-Host ""

if (-not $ZipPath -and $VersionTag) {
    $ZipPath = Join-Path $ReleaseRoot "$VersionTag.zip"
}

if (-not $ZipPath) {
    if ($SkipIfMissing) {
        Write-Host "No explicit ZIP provided. Skipping build output smoke because -SkipIfMissing was provided."
        exit 0
    }

    $ZipPath = Find-LatestVoilaZip -Root $ReleaseRoot
}

if (-not $ZipPath) {
    throw "No Voila ZIP found. Provide -ZipPath, -VersionTag, or create a ZIP in ReleaseRoot: $ReleaseRoot"
}

if (-not (Test-Path $ZipPath)) {
    if ($SkipIfMissing) {
        Write-Host "ZIP not found: $ZipPath"
        Write-Host "Skipping build output smoke because -SkipIfMissing was provided."
        exit 0
    }

    throw "ZIP not found: $ZipPath"
}

Write-Host "Selected ZIP: $ZipPath"

$argsList = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $StandaloneSmokeScript,
    "-ProjectRoot", $ProjectRoot,
    "-ZipPath", $ZipPath
)

if ($WorkRoot) {
    $argsList += @("-WorkRoot", $WorkRoot)
}

if ($KeepTemp) {
    $argsList += "-KeepTemp"
}

& powershell @argsList

if ($LASTEXITCODE -ne 0) {
    throw "Build output language-pack smoke failed."
}

Write-Host ""
Write-Host "Build output language-pack smoke passed."
exit 0
