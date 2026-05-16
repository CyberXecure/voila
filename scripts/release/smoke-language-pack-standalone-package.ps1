param(
    [string]$ProjectRoot = "",
    [string]$ZipPath = "",
    [string]$PackagedAppRoot = "",
    [string]$WorkRoot = "",
    [switch]$IncludeSamples,
    [switch]$KeepTemp
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

$InspectScript = Join-Path $ProjectRoot "scripts\release\inspect-language-pack-packaging.ps1"

if (-not (Test-Path $InspectScript)) {
    throw "Inspect script missing: $InspectScript"
}

function Copy-RelativeDirectory {
    param(
        [string]$SourceRoot,
        [string]$DestinationRoot,
        [string]$RelativePath,
        [bool]$Required
    )

    $source = Join-Path $SourceRoot $RelativePath
    $destination = Join-Path $DestinationRoot $RelativePath

    if (-not (Test-Path $source)) {
        if ($Required) {
            throw "Required source directory missing: $source"
        }
        return
    }

    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Copy-Item -Path (Join-Path $source "*") -Destination $destination -Recurse -Force
}

function Resolve-AppRootFromPath {
    param([string]$Root)

    if (Test-Path (Join-Path $Root "language-packs")) {
        return $Root
    }

    $nestedApp = Join-Path $Root "app"
    if (Test-Path (Join-Path $nestedApp "language-packs")) {
        return $nestedApp
    }

    return $Root
}

function Invoke-LanguagePackInspection {
    param([string]$AppRoot)

    Write-Host ""
    Write-Host "=== INSPECT STANDALONE LANGUAGE PACKS ==="
    Write-Host "AppRoot: $AppRoot"

    & powershell -ExecutionPolicy Bypass -File $InspectScript -ProjectRoot $ProjectRoot -PackagedAppRoot $AppRoot

    if ($LASTEXITCODE -ne 0) {
        throw "Standalone language-pack inspection failed."
    }
}

Write-Host "=== Voila standalone language-pack smoke ==="
Write-Host "ProjectRoot:     $ProjectRoot"
Write-Host "ZipPath:         $ZipPath"
Write-Host "PackagedAppRoot: $PackagedAppRoot"
Write-Host "IncludeSamples:  $IncludeSamples"

$tempRoot = ""

try {
    if ($ZipPath) {
        if (-not (Test-Path $ZipPath)) {
            throw "ZIP missing: $ZipPath"
        }

        if (-not $WorkRoot) {
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $WorkRoot = Join-Path ([System.IO.Path]::GetTempPath()) "voila-language-pack-standalone-zip-smoke-$stamp"
        }

        $tempRoot = $WorkRoot
        Remove-Item $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null

        Write-Host ""
        Write-Host "=== EXTRACT ZIP ==="
        Write-Host "WorkRoot: $WorkRoot"
        Expand-Archive -Path $ZipPath -DestinationPath $WorkRoot -Force

        $appRoot = Resolve-AppRootFromPath -Root $WorkRoot
        Invoke-LanguagePackInspection -AppRoot $appRoot
    }
    elseif ($PackagedAppRoot) {
        if (-not (Test-Path $PackagedAppRoot)) {
            throw "Packaged app root missing: $PackagedAppRoot"
        }

        $appRoot = Resolve-AppRootFromPath -Root $PackagedAppRoot
        Invoke-LanguagePackInspection -AppRoot $appRoot
    }
    else {
        if (-not $WorkRoot) {
            $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $WorkRoot = Join-Path ([System.IO.Path]::GetTempPath()) "voila-language-pack-standalone-source-smoke-$stamp"
        }

        $tempRoot = $WorkRoot
        $appRoot = Join-Path $WorkRoot "app"

        Remove-Item $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force -Path $appRoot | Out-Null

        Write-Host ""
        Write-Host "=== CREATE SOURCE DRY-RUN APP ROOT ==="
        Write-Host "AppRoot: $appRoot"

        Copy-RelativeDirectory -SourceRoot $ProjectRoot -DestinationRoot $appRoot -RelativePath "language-packs\core" -Required $true
        Copy-RelativeDirectory -SourceRoot $ProjectRoot -DestinationRoot $appRoot -RelativePath "language-packs\schema" -Required $true

        if ($IncludeSamples) {
            Copy-RelativeDirectory -SourceRoot $ProjectRoot -DestinationRoot $appRoot -RelativePath "language-packs\samples" -Required $false
        }

        Invoke-LanguagePackInspection -AppRoot $appRoot
    }
}
finally {
    if ($tempRoot -and -not $KeepTemp) {
        Write-Host ""
        Write-Host "=== CLEANUP TEMP FOLDER ==="
        Remove-Item $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    elseif ($tempRoot) {
        Write-Host ""
        Write-Host "Keeping temp folder: $tempRoot"
    }
}

Write-Host ""
Write-Host "Standalone language-pack smoke passed."
exit 0
