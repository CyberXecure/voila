param(
    [string]$ProjectRoot = "",
    [string]$PackagedAppRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

function Test-RelativeFile {
    param(
        [string]$Root,
        [string]$RelativePath,
        [bool]$Required
    )

    $fullPath = Join-Path $Root $RelativePath
    $exists = Test-Path $fullPath
    $length = 0

    if ($exists) {
        $length = (Get-Item $fullPath).Length
    }

    [pscustomobject]@{
        Required = $Required
        Exists = $exists
        Length = $length
        RelativePath = $RelativePath
        FullPath = $fullPath
    }
}

$requiredLanguagePackFiles = @(
    "language-packs\core\ro.language-pack.json",
    "language-packs\core\en.language-pack.json",
    "language-packs\schema\language-pack.schema.json"
)

$optionalLanguagePackFiles = @(
    "language-packs\samples\ro.language-pack.sample.json",
    "language-packs\samples\en.language-pack.sample.json",
    "language-packs\runtime\minimal_language_runtime.py"
)

Write-Host "=== Voila language pack packaging inspection ==="
Write-Host "ProjectRoot:     $ProjectRoot"
if ($PackagedAppRoot) {
    Write-Host "PackagedAppRoot: $PackagedAppRoot"
}
else {
    Write-Host "PackagedAppRoot: (not provided)"
}
Write-Host ""

Write-Host "=== SOURCE REQUIRED FILES ==="
$sourceRequired = foreach ($relative in $requiredLanguagePackFiles) {
    Test-RelativeFile -Root $ProjectRoot -RelativePath $relative -Required $true
}
$sourceRequired | Format-Table Required, Exists, Length, RelativePath -AutoSize

Write-Host ""
Write-Host "=== SOURCE OPTIONAL FILES ==="
$sourceOptional = foreach ($relative in $optionalLanguagePackFiles) {
    Test-RelativeFile -Root $ProjectRoot -RelativePath $relative -Required $false
}
$sourceOptional | Format-Table Required, Exists, Length, RelativePath -AutoSize

$errors = @()

foreach ($item in $sourceRequired) {
    if (-not $item.Exists) {
        $errors += "Missing required source file: $($item.RelativePath)"
    }
    elseif ($item.Length -le 0) {
        $errors += "Required source file is empty: $($item.RelativePath)"
    }
}

if ($PackagedAppRoot) {
    Write-Host ""
    Write-Host "=== PACKAGED REQUIRED FILES ==="
    $packagedRequired = foreach ($relative in $requiredLanguagePackFiles) {
        Test-RelativeFile -Root $PackagedAppRoot -RelativePath $relative -Required $true
    }
    $packagedRequired | Format-Table Required, Exists, Length, RelativePath -AutoSize

    foreach ($item in $packagedRequired) {
        if (-not $item.Exists) {
            $errors += "Missing required packaged file: $($item.RelativePath)"
        }
        elseif ($item.Length -le 0) {
            $errors += "Required packaged file is empty: $($item.RelativePath)"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Language pack packaging inspection failed."
    foreach ($errorItem in $errors) {
        Write-Host "- $errorItem"
    }
    exit 1
}

Write-Host ""
Write-Host "Language pack packaging inspection passed."
exit 0
