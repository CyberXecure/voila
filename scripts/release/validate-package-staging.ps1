<#
.SYNOPSIS
Validates a Voila Windows package staging folder before ZIP/installer creation.

.DESCRIPTION
This script validates package staging readiness for Voila controlled releases.
It checks package root safety, legal files, README, release notes, launchers,
and exclusion patterns.

It is intended for release/package validation only.

It does not:
- copy files
- modify package contents
- build a ZIP
- create an installer
- create or upload a release
- change runtime/backend/frontend behavior
- provide legal approval

.EXAMPLE
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta

.EXAMPLE
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -Strict

.EXAMPLE
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -ValidateLegalOnly
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string] $PackageRoot,

  [Parameter(Mandatory = $true)]
  [ValidateSet("PublicBeta", "TesterDemo", "Supporter", "Pro", "Internal")]
  [string] $ReleaseType,

  [switch] $Strict,

  [switch] $ValidateLegalOnly,

  [switch] $SkipLauncherCheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Results = New-Object System.Collections.Generic.List[object]

function Add-Check {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Name,

    [Parameter(Mandatory = $true)]
    [ValidateSet("PASS", "WARN", "FAIL")]
    [string] $Status,

    [string] $Message = ""
  )

  $script:Results.Add([pscustomobject]@{
    Name = $Name
    Status = $Status
    Message = $Message
  }) | Out-Null
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
    Add-Check -Name $Label -Status "FAIL" -Message "Directory does not exist: $Path"
    return $null
  }

  if (-not (Test-Path -Path $resolved.Path -PathType Container)) {
    Add-Check -Name $Label -Status "FAIL" -Message "Path is not a directory: $Path"
    return $null
  }

  Add-Check -Name $Label -Status "PASS" -Message $resolved.Path
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
    Add-Check -Name "Safe package root" -Status "FAIL" -Message "PackageRoot must not be repository root."
    return
  }

  $repoDocs = (Join-Path $repoRoot "docs").TrimEnd("\")
  $repoScripts = (Join-Path $repoRoot "scripts").TrimEnd("\")

  if ($packageRoot -eq $repoDocs) {
    Add-Check -Name "Safe package root" -Status "FAIL" -Message "PackageRoot must not be docs/."
    return
  }

  if ($packageRoot -eq $repoScripts) {
    Add-Check -Name "Safe package root" -Status "FAIL" -Message "PackageRoot must not be scripts/."
    return
  }

  Add-Check -Name "Safe package root" -Status "PASS" -Message $ResolvedPackageRoot
}

function Test-RequiredFile {
  param(
    [Parameter(Mandatory = $true)]
    [string] $BasePath,

    [Parameter(Mandatory = $true)]
    [string] $RelativePath,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  $path = Join-Path $BasePath $RelativePath

  if (-not (Test-Path -Path $path -PathType Leaf)) {
    Add-Check -Name $Label -Status "FAIL" -Message "Missing required file: $RelativePath"
    return $null
  }

  $item = Get-Item $path
  if ($item.Length -le 0) {
    Add-Check -Name $Label -Status "FAIL" -Message "File is empty: $RelativePath"
    return $item.FullName
  }

  Add-Check -Name $Label -Status "PASS" -Message "$RelativePath ($($item.Length) bytes)"
  return $item.FullName
}

function Test-OptionalFile {
  param(
    [Parameter(Mandatory = $true)]
    [string] $BasePath,

    [Parameter(Mandatory = $true)]
    [string[]] $RelativePaths,

    [Parameter(Mandatory = $true)]
    [string] $Label,

    [string] $MissingStatus = "WARN"
  )

  foreach ($relative in $RelativePaths) {
    $path = Join-Path $BasePath $relative
    if (Test-Path -Path $path -PathType Leaf) {
      $item = Get-Item $path
      Add-Check -Name $Label -Status "PASS" -Message "$relative ($($item.Length) bytes)"
      return $item.FullName
    }
  }

  Add-Check -Name $Label -Status $MissingStatus -Message ("None found: " + ($RelativePaths -join ", "))
  return $null
}

function Test-FileContainsAny {
  param(
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string[]] $Patterns,

    [Parameter(Mandatory = $true)]
    [string] $Label,

    [string] $MissingStatus = "WARN"
  )

  if (-not $Path) {
    Add-Check -Name $Label -Status $MissingStatus -Message "File not available for content check."
    return
  }

  $content = Get-Content -Path $Path -Raw -ErrorAction Stop
  foreach ($pattern in $Patterns) {
    if ($content -match [regex]::Escape($pattern)) {
      Add-Check -Name $Label -Status "PASS" -Message "Found: $pattern"
      return
    }
  }

  Add-Check -Name $Label -Status $MissingStatus -Message ("Missing expected content indicator. Expected one of: " + ($Patterns -join ", "))
}

function Test-ForbiddenPackageContent {
  param(
    [Parameter(Mandatory = $true)]
    [string] $BasePath
  )

  $forbiddenFilePatterns = @(
    ".env",
    "*.key",
    "*.pfx"
  )

  $forbiddenDirectoryNames = @(
    "secrets",
    "private"
  )

  foreach ($pattern in $forbiddenFilePatterns) {
    $matches = Get-ChildItem -Path $BasePath -Recurse -Force -File -Filter $pattern -ErrorAction SilentlyContinue
    if ($matches) {
      Add-Check -Name "Forbidden files" -Status "FAIL" -Message ("Found forbidden file pattern {0}: {1}" -f $pattern, (($matches | Select-Object -First 5 -ExpandProperty FullName) -join "; "))
      return
    }
  }

  foreach ($name in $forbiddenDirectoryNames) {
    $matches = Get-ChildItem -Path $BasePath -Recurse -Force -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq $name }
    if ($matches) {
      Add-Check -Name "Forbidden directories" -Status "FAIL" -Message ("Found forbidden directory {0}: {1}" -f $name, (($matches | Select-Object -First 5 -ExpandProperty FullName) -join "; "))
      return
    }
  }

  $commercialDocs = Get-ChildItem -Path $BasePath -Recurse -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match "\\docs\\commercial$" }

  if ($commercialDocs) {
    Add-Check -Name "Forbidden commercial docs" -Status "FAIL" -Message ("Found docs/commercial in package: " + (($commercialDocs | Select-Object -First 5 -ExpandProperty FullName) -join "; "))
    return
  }

  Add-Check -Name "Forbidden content scan" -Status "PASS" -Message "No forbidden files or folders found."
}

function Test-AdvisoryPlanningDocs {
  param(
    [Parameter(Mandatory = $true)]
    [string] $BasePath
  )

  $patterns = @("*PLAN.md", "*CHECKLIST.md", "*OUTLINE.md")
  $matches = @()

  foreach ($pattern in $patterns) {
    $matches += Get-ChildItem -Path $BasePath -Recurse -Force -File -Filter $pattern -ErrorAction SilentlyContinue
  }

  if ($matches.Count -gt 0) {
    Add-Check -Name "Planning docs advisory" -Status "WARN" -Message ("Planning/checklist/outline docs found: " + (($matches | Select-Object -First 5 -ExpandProperty FullName) -join "; "))
  } else {
    Add-Check -Name "Planning docs advisory" -Status "PASS" -Message "No planning/checklist/outline docs found."
  }
}

Write-Host "=== VOILA PACKAGE STAGING VALIDATION ==="
Write-Host "Package root: $PackageRoot"
Write-Host "Release type: $ReleaseType"
Write-Host "Strict: $($Strict.IsPresent)"
Write-Host "ValidateLegalOnly: $($ValidateLegalOnly.IsPresent)"
Write-Host "SkipLauncherCheck: $($SkipLauncherCheck.IsPresent)"
Write-Host ""

$resolvedPackageRoot = Resolve-RequiredDirectory -Path $PackageRoot -Label "Package root"

if ($resolvedPackageRoot) {
  Assert-SafePackageRoot -ResolvedPackageRoot $resolvedPackageRoot

  $eula = Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "legal\EULA.txt" -Label "Legal EULA"
  $license = Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "legal\LICENSE.txt" -Label "Legal LICENSE"
  $betaTerms = Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "legal\BETA-TERMS.md" -Label "Legal BETA-TERMS"
  $thirdParty = Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "legal\THIRD-PARTY-NOTICES.md" -Label "Legal THIRD-PARTY-NOTICES"

  Test-FileContainsAny -Path $eula -Patterns @("Voila", "beta") -Label "EULA content"
  Test-FileContainsAny -Path $license -Patterns @("All rights reserved", "proprietary") -Label "LICENSE content"
  Test-FileContainsAny -Path $betaTerms -Patterns @("beta", "Beta") -Label "BETA-TERMS content"
  Test-FileContainsAny -Path $thirdParty -Patterns @("third-party", "Third-party", "third party") -Label "THIRD-PARTY-NOTICES content"

  if (-not $ValidateLegalOnly) {
    $readmeMissingStatus = "FAIL"
    $readme = Test-OptionalFile -BasePath $resolvedPackageRoot -RelativePaths @("README-WINDOWS.txt", "README-TESTERS.txt", "README.md") -Label "README" -MissingStatus $readmeMissingStatus
    Test-FileContainsAny -Path $readme -Patterns @("legal/", "legal\", "EULA") -Label "README legal reference" -MissingStatus "FAIL"
    Test-FileContainsAny -Path $readme -Patterns @("START", "start", "Start") -Label "README start instructions" -MissingStatus "WARN"
    Test-FileContainsAny -Path $readme -Patterns @("STOP", "stop", "Stop") -Label "README stop instructions" -MissingStatus "WARN"

    $releaseNotes = Test-OptionalFile -BasePath $resolvedPackageRoot -RelativePaths @("RELEASE-NOTES.txt", "RELEASE-NOTES.md") -Label "Release notes" -MissingStatus "WARN"
    Test-FileContainsAny -Path $releaseNotes -Patterns @("Release type", "PublicBeta", "TesterDemo", "release type") -Label "Release notes type" -MissingStatus "WARN"
    Test-FileContainsAny -Path $releaseNotes -Patterns @("SHA256", "checksum", "Checksum") -Label "Release notes checksum" -MissingStatus "WARN"

    if (-not $SkipLauncherCheck) {
      $launcherMissingStatus = "FAIL"
      if ($ReleaseType -eq "Internal") {
        $launcherMissingStatus = "WARN"
      }

      Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "START-VOILA.bat" -Label "Start launcher" | Out-Null
      Test-RequiredFile -BasePath $resolvedPackageRoot -RelativePath "STOP-VOILA.bat" -Label "Stop launcher" | Out-Null
    } else {
      Add-Check -Name "Launcher check" -Status "WARN" -Message "Skipped by -SkipLauncherCheck."
    }

    Test-ForbiddenPackageContent -BasePath $resolvedPackageRoot
    Test-AdvisoryPlanningDocs -BasePath $resolvedPackageRoot
  }
}

Write-Host ""
Write-Host "Checks:"
foreach ($result in $Results) {
  $line = "- {0}: {1}" -f $result.Name, $result.Status
  if ($result.Message) {
    $line += " — " + $result.Message
  }
  Write-Host $line
}

$failCount = @($Results | Where-Object { $_.Status -eq "FAIL" }).Count
$warnCount = @($Results | Where-Object { $_.Status -eq "WARN" }).Count

Write-Host ""

if ($failCount -gt 0) {
  Write-Host "Result: FAIL"
  throw "Voila package staging validation failed with $failCount failure(s) and $warnCount warning(s)."
}

if (($warnCount -gt 0) -and $Strict) {
  Write-Host "Result: FAIL"
  throw "Voila package staging validation has $warnCount warning(s), and -Strict was used."
}

if ($warnCount -gt 0) {
  Write-Host "Result: CONDITIONAL"
  Write-Host "Validation completed with $warnCount warning(s)."
} else {
  Write-Host "Result: PASS"
  Write-Host "Validation completed without failures or warnings."
}
