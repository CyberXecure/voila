param(
    [string]$ProjectRoot = "",
    [string]$ReadinessRoot = "",
    [switch]$IncludeSamples,
    [switch]$KeepTemp
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

if (-not $ReadinessRoot) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $ReadinessRoot = Join-Path ([System.IO.Path]::GetTempPath()) "voila-language-pack-packaging-readiness-$stamp"
}

$AppRoot = Join-Path $ReadinessRoot "app"
$InspectScript = Join-Path $ProjectRoot "scripts\release\inspect-language-pack-packaging.ps1"

function Copy-RelativeDirectory {
    param(
        [string]$RelativePath,
        [bool]$Required
    )

    $source = Join-Path $ProjectRoot $RelativePath
    $destination = Join-Path $AppRoot $RelativePath

    if (-not (Test-Path $source)) {
        if ($Required) {
            throw "Required source directory missing: $source"
        }
        return
    }

    New-Item -ItemType Directory -Force -Path $destination | Out-Null

    $sourceItems = Join-Path $source "*"
    Copy-Item -Path $sourceItems -Destination $destination -Recurse -Force
}

Write-Host "=== Voila language pack packaging readiness dry-run ==="
Write-Host "ProjectRoot:   $ProjectRoot"
Write-Host "ReadinessRoot: $ReadinessRoot"
Write-Host "AppRoot:       $AppRoot"
Write-Host "IncludeSamples: $IncludeSamples"
Write-Host ""

if (-not (Test-Path $InspectScript)) {
    throw "Inspect script missing: $InspectScript"
}

Remove-Item $ReadinessRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $AppRoot | Out-Null

Write-Host "=== COPY REQUIRED LANGUAGE PACK DATA ==="
Copy-RelativeDirectory -RelativePath "language-packs\core" -Required $true
Copy-RelativeDirectory -RelativePath "language-packs\schema" -Required $true

if ($IncludeSamples) {
    Write-Host "=== COPY OPTIONAL SAMPLES ==="
    Copy-RelativeDirectory -RelativePath "language-packs\samples" -Required $false
}

Write-Host ""
Write-Host "=== INSPECT DRY-RUN PACKAGED APP ROOT ==="
& powershell -ExecutionPolicy Bypass -File $InspectScript -ProjectRoot $ProjectRoot -PackagedAppRoot $AppRoot

if ($LASTEXITCODE -ne 0) {
    throw "Language pack packaging inspection failed for dry-run app root."
}

if (-not $KeepTemp) {
    Write-Host ""
    Write-Host "=== CLEANUP DRY-RUN FOLDER ==="
    Remove-Item $ReadinessRoot -Recurse -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host ""
    Write-Host "Keeping dry-run folder: $ReadinessRoot"
}

Write-Host ""
Write-Host "Language pack packaging readiness dry-run passed."
exit 0
