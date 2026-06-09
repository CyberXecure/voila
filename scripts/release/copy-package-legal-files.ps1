[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [Parameter(Mandatory = $true)]
  [string] $PackageRoot,

  [Parameter(Mandatory = $true)]
  [ValidateSet("PublicBeta", "TesterDemo", "Supporter", "Pro", "Internal")]
  [string] $ReleaseType,

  [switch] $Force,

  [switch] $ValidateOnly,

  [string] $EulaSource = ".\docs\legal\VOILA-BETA-EULA-DRAFT.md",
  [string] $LicenseSource = ".\LICENSE.txt",
  [string] $BetaTermsSource = ".\BETA-TERMS.md",
  [string] $ThirdPartyNoticesSource = ".\docs\legal\THIRD-PARTY-NOTICES.md"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RequiredFile {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  $resolved = Resolve-Path -Path $Path -ErrorAction SilentlyContinue
  if (-not $resolved) {
    throw "Missing required source file for $Label`: $Path"
  }

  if (-not (Test-Path -Path $resolved.Path -PathType Leaf)) {
    throw "Required source path is not a file for $Label`: $Path"
  }

  return $resolved.Path
}

function Resolve-RequiredDirectory {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  $resolved = Resolve-Path -Path $Path -ErrorAction SilentlyContinue
  if (-not $resolved) {
    throw "Missing required directory for $Label`: $Path"
  }

  if (-not (Test-Path -Path $resolved.Path -PathType Container)) {
    throw "Required path is not a directory for $Label`: $Path"
  }

  return $resolved.Path
}

function Assert-SafePackageRoot {
  param(
    [Parameter(Mandatory = $true)]
    [string] $ResolvedPackageRoot
  )

  $repoRoot = (Resolve-Path ".").Path.TrimEnd("\")
  $packageRoot = $ResolvedPackageRoot.TrimEnd("\")

  if ($packageRoot -eq $repoRoot) {
    throw "PackageRoot must not be the repository root: $ResolvedPackageRoot"
  }
}

function Copy-RequiredLegalFile {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Source,

    [Parameter(Mandatory = $true)]
    [string] $Destination,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  if ((Test-Path -Path $Destination -PathType Leaf) -and (-not $Force)) {
    throw "Destination already exists for $Label. Use -Force to overwrite: $Destination"
  }

  if ($PSCmdlet.ShouldProcess($Destination, "Copy $Label")) {
    Copy-Item -Path $Source -Destination $Destination -Force:$Force
  }
}

function Assert-RequiredOutput {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  if (-not (Test-Path -Path $Path -PathType Leaf)) {
    throw "Missing required output for $Label`: $Path"
  }
}

Write-Host "=== VOILA PACKAGE LEGAL FILE COPY ==="
Write-Host "Release type: $ReleaseType"

$packageRootResolved = Resolve-RequiredDirectory -Path $PackageRoot -Label "PackageRoot"
Assert-SafePackageRoot -ResolvedPackageRoot $packageRootResolved

$eula = Resolve-RequiredFile -Path $EulaSource -Label "EULA"
$license = Resolve-RequiredFile -Path $LicenseSource -Label "LICENSE"
$betaTerms = Resolve-RequiredFile -Path $BetaTermsSource -Label "BETA-TERMS"
$thirdParty = Resolve-RequiredFile -Path $ThirdPartyNoticesSource -Label "THIRD-PARTY-NOTICES"

$legalOut = Join-Path $packageRootResolved "legal"

Write-Host ""
Write-Host "Package root: $packageRootResolved"
Write-Host "Legal output: $legalOut"

if (-not $ValidateOnly) {
  if ($PSCmdlet.ShouldProcess($legalOut, "Create legal output folder")) {
    New-Item -ItemType Directory -Force -Path $legalOut | Out-Null
  }

  Copy-RequiredLegalFile -Source $eula -Destination (Join-Path $legalOut "EULA.txt") -Label "EULA"
  Copy-RequiredLegalFile -Source $license -Destination (Join-Path $legalOut "LICENSE.txt") -Label "LICENSE"
  Copy-RequiredLegalFile -Source $betaTerms -Destination (Join-Path $legalOut "BETA-TERMS.md") -Label "BETA-TERMS"
  Copy-RequiredLegalFile -Source $thirdParty -Destination (Join-Path $legalOut "THIRD-PARTY-NOTICES.md") -Label "THIRD-PARTY-NOTICES"
} else {
  Write-Host ""
  Write-Host "ValidateOnly mode: copy operations skipped."
}

Write-Host ""
Write-Host "=== VALIDATE OUTPUT ==="

Assert-RequiredOutput -Path (Join-Path $legalOut "EULA.txt") -Label "EULA"
Assert-RequiredOutput -Path (Join-Path $legalOut "LICENSE.txt") -Label "LICENSE"
Assert-RequiredOutput -Path (Join-Path $legalOut "BETA-TERMS.md") -Label "BETA-TERMS"
Assert-RequiredOutput -Path (Join-Path $legalOut "THIRD-PARTY-NOTICES.md") -Label "THIRD-PARTY-NOTICES"

Write-Host ""
Write-Host "Legal file copy validation passed."
