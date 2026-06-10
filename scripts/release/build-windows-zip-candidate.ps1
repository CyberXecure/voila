<#
.SYNOPSIS
Builds or dry-runs a Voila Windows ZIP package candidate.

.DESCRIPTION
This release helper prepares a package staging folder, copies runtime/source files,
copies package legal files, validates staging, and optionally creates a ZIP candidate,
SHA256 file, and extracted verification folder.

It does not publish a GitHub release, create an installer, sign binaries, implement
payment/licensing, or provide legal approval.

.EXAMPLE
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource .\.release-cache\runtime-source `
  -OutputRoot .\.release-cache\voila-v0.3.28-windows-package-candidate `
  -Version "v0.3.28" `
  -ReleaseType PublicBeta `
  -DryRun

.EXAMPLE
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource .\.release-cache\runtime-source `
  -OutputRoot .\.release-cache\voila-v0.3.28-windows-package-candidate `
  -Version "v0.3.28" `
  -ReleaseType PublicBeta `
  -Force
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [Parameter(Mandatory = $true)]
  [string] $RuntimeSource,

  [Parameter(Mandatory = $true)]
  [string] $OutputRoot,

  [Parameter(Mandatory = $true)]
  [ValidatePattern("^v[0-9]+\.[0-9]+\.[0-9]+")]
  [string] $Version,

  [Parameter(Mandatory = $true)]
  [ValidateSet("PublicBeta", "TesterDemo", "Supporter", "Pro", "Internal")]
  [string] $ReleaseType,

  [string] $ZipName,

  [switch] $DryRun,

  [switch] $Force,

  [switch] $SkipExtractValidation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RequiredDirectory {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  $resolved = Resolve-Path -Path $Path -ErrorAction SilentlyContinue
  if (-not $resolved) {
    throw "$Label does not exist: $Path"
  }

  if (-not (Test-Path -Path $resolved.Path -PathType Container)) {
    throw "$Label is not a directory: $Path"
  }

  return $resolved.Path
}

function Assert-SafeDirectory {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  $repoRoot = (Resolve-Path ".").Path.TrimEnd("\")
  $normalized = $Path.TrimEnd("\")

  $unsafe = @(
    $repoRoot,
    (Join-Path $repoRoot "docs").TrimEnd("\"),
    (Join-Path $repoRoot "scripts").TrimEnd("\")
  )

  foreach ($unsafePath in $unsafe) {
    if ($normalized -eq $unsafePath) {
      throw "$Label must not be repository root, docs/, or scripts/: $Path"
    }
  }
}

function Copy-DirectoryContents {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Source,

    [Parameter(Mandatory = $true)]
    [string] $Destination
  )

  New-Item -ItemType Directory -Force -Path $Destination | Out-Null

  Get-ChildItem -Path $Source -Force | ForEach-Object {
    $target = Join-Path $Destination $_.Name
    Copy-Item -Path $_.FullName -Destination $target -Recurse -Force
  }
}

function Assert-RequiredPackageFile {
  param(
    [Parameter(Mandatory = $true)]
    [string] $PackageRoot,

    [Parameter(Mandatory = $true)]
    [string] $RelativePath
  )

  $path = Join-Path $PackageRoot $RelativePath
  if (-not (Test-Path -Path $path -PathType Leaf)) {
    throw "Missing required package file: $RelativePath"
  }
}

function Write-BuildSummary {
  param(
    [Parameter(Mandatory = $true)]
    [string] $SummaryPath,

    [Parameter(Mandatory = $true)]
    [string] $Content
  )

  Set-Content -Encoding UTF8 -Path $SummaryPath -Value $Content
}

function Get-DefaultZipName {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Version,

    [Parameter(Mandatory = $true)]
    [string] $ReleaseType
  )

  $releaseSlug = switch ($ReleaseType) {
    "PublicBeta" { "public-beta" }
    "TesterDemo" { "tester-demo" }
    "Supporter" { "supporter" }
    "Pro" { "pro" }
    "Internal" { "internal" }
  }

  return "voila-$Version-$releaseSlug-windows-package-candidate.zip"
}

Write-Host "=== VOILA WINDOWS ZIP CANDIDATE BUILD ==="
Write-Host "RuntimeSource: $RuntimeSource"
Write-Host "OutputRoot: $OutputRoot"
Write-Host "Version: $Version"
Write-Host "ReleaseType: $ReleaseType"
Write-Host "DryRun: $($DryRun.IsPresent)"
Write-Host "Force: $($Force.IsPresent)"
Write-Host ""

$resolvedRuntimeSource = Resolve-RequiredDirectory -Path $RuntimeSource -Label "RuntimeSource"
Assert-SafeDirectory -Path $resolvedRuntimeSource -Label "RuntimeSource"

if (-not $ZipName) {
  $ZipName = Get-DefaultZipName -Version $Version -ReleaseType $ReleaseType
}

if (-not $ZipName.EndsWith(".zip", [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "ZipName must end with .zip"
}

$outputRootFull = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputRoot)
Assert-SafeDirectory -Path $outputRootFull -Label "OutputRoot"

$stagingRoot = Join-Path $outputRootFull "staging"
$packageRoot = Join-Path $stagingRoot "voila"
$outRoot = Join-Path $outputRootFull "out"
$extractRoot = Join-Path $outputRootFull "extract-smoke"
$zipPath = Join-Path $outRoot $ZipName
$shaPath = "$zipPath.sha256"
$summaryPath = Join-Path $outRoot "BUILD-SUMMARY.txt"

if ((Test-Path $outputRootFull) -and (-not $Force)) {
  throw "OutputRoot already exists. Use -Force to recreate it: $outputRootFull"
}

if ($PSCmdlet.ShouldProcess($outputRootFull, "Prepare output root")) {
  Remove-Item $outputRootFull -Recurse -Force -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null
  New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
}

Write-Host "=== COPY RUNTIME SOURCE TO STAGING ==="
Copy-DirectoryContents -Source $resolvedRuntimeSource -Destination $packageRoot

Write-Host ""
Write-Host "=== ENSURE REQUIRED PACKAGE DOCS / LAUNCHERS ==="

$requiredTopLevel = @(
  "README-WINDOWS.txt",
  "RELEASE-NOTES.txt",
  "START-VOILA.bat",
  "STOP-VOILA.bat"
)

foreach ($relative in $requiredTopLevel) {
  Assert-RequiredPackageFile -PackageRoot $packageRoot -RelativePath $relative
}

Write-Host "Required top-level package files exist."

Write-Host ""
Write-Host "=== COPY PACKAGE LEGAL FILES ==="
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot $packageRoot `
  -ReleaseType $ReleaseType `
  -Force

Write-Host ""
Write-Host "=== VALIDATE PACKAGE STAGING STRICT ==="
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot $packageRoot `
  -ReleaseType $ReleaseType `
  -Strict

if ($DryRun) {
  Write-Host ""
  Write-Host "=== DRY RUN: ZIP / SHA256 / EXTRACT SKIPPED ==="

  $summary = @"
Voila Windows ZIP Candidate Build Summary

Result: DRY-RUN PASS
Version: $Version
ReleaseType: $ReleaseType
RuntimeSource: $resolvedRuntimeSource
OutputRoot: $outputRootFull
PackageRoot: $packageRoot
ZipName: $ZipName
ZipPath: not created - DryRun
Sha256Path: not created - DryRun
ExtractValidation: skipped - DryRun
CreatedAt: $(Get-Date -Format o)
"@

  Write-BuildSummary -SummaryPath $summaryPath -Content $summary
  Write-Host $summary
  return
}

Write-Host ""
Write-Host "=== CREATE ZIP CANDIDATE ==="

if ($PSCmdlet.ShouldProcess($zipPath, "Create ZIP candidate")) {
  Compress-Archive `
    -Path $packageRoot `
    -DestinationPath $zipPath `
    -Force
}

if (-not (Test-Path $zipPath -PathType Leaf)) {
  throw "ZIP candidate was not created: $zipPath"
}

Write-Host "ZIP created:"
Get-Item $zipPath | Select-Object FullName, Length

Write-Host ""
Write-Host "=== GENERATE SHA256 ==="

$hash = Get-FileHash -Path $zipPath -Algorithm SHA256
$shaContent = @"
SHA256: $($hash.Hash)
File: $ZipName
GeneratedAt: $(Get-Date -Format o)
"@

Set-Content -Encoding UTF8 -Path $shaPath -Value $shaContent

Write-Host $shaContent

if (-not $SkipExtractValidation) {
  Write-Host ""
  Write-Host "=== EXTRACT ZIP FOR VALIDATION ==="

  Remove-Item $extractRoot -Recurse -Force -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $extractRoot | Out-Null

  Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force

  $extractedPackageRoot = Join-Path $extractRoot "voila"

  if (-not (Test-Path $extractedPackageRoot -PathType Container)) {
    throw "Extracted ZIP does not contain expected root folder: voila/"
  }

  $requiredExtracted = @(
    "README-WINDOWS.txt",
    "RELEASE-NOTES.txt",
    "START-VOILA.bat",
    "STOP-VOILA.bat",
    "legal\EULA.txt",
    "legal\LICENSE.txt",
    "legal\BETA-TERMS.md",
    "legal\THIRD-PARTY-NOTICES.md"
  )

  foreach ($relative in $requiredExtracted) {
    Assert-RequiredPackageFile -PackageRoot $extractedPackageRoot -RelativePath $relative
  }

  Write-Host "Extract validation passed."
} else {
  Write-Host ""
  Write-Host "Extract validation skipped by -SkipExtractValidation."
}

$summary = @"
Voila Windows ZIP Candidate Build Summary

Result: PASS
Version: $Version
ReleaseType: $ReleaseType
RuntimeSource: $resolvedRuntimeSource
OutputRoot: $outputRootFull
PackageRoot: $packageRoot
ZipName: $ZipName
ZipPath: $zipPath
Sha256Path: $shaPath
ExtractValidation: $(if ($SkipExtractValidation) { "skipped" } else { "PASS" })
CreatedAt: $(Get-Date -Format o)
"@

Write-BuildSummary -SummaryPath $summaryPath -Content $summary

Write-Host ""
Write-Host $summary
