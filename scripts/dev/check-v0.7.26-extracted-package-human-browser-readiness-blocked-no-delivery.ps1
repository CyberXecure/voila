param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "[FAIL] $Message" }
    Write-Host "[PASS] $Message"
}

function Assert-Contains {
    param([string]$Text, [string]$Needle, [string]$Message)
    Assert-True ($Text.Contains($Needle)) $Message
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$DocPath = Join-Path $RepoRoot "docs/dev/v0.7.26-extracted-package-human-browser-readiness-blocked-no-delivery.md"
$BlockerJson = "D:\dev\tester-runs\voila-v0.7.26-extracted-package-human-browser-readiness-no-delivery\blocker-evidence\V0.7.26-HUMAN-BROWSER-READINESS-BLOCKED.json"
$BlockerMd = "D:\dev\tester-runs\voila-v0.7.26-extracted-package-human-browser-readiness-no-delivery\blocker-evidence\V0.7.26-HUMAN-BROWSER-READINESS-BLOCKED.md"
$SuspiciousHits = "D:\dev\tester-runs\voila-v0.7.26-extracted-package-human-browser-readiness-no-delivery\blocker-evidence\suspicious-diacritic-ocr-hits.json"
$PackageZip = "D:\dev\release-assets\voila\v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery\voila-v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery.zip"
$ExpectedSha = "E985D813040CDE9ACDA9706C479429BF879FB1D5D36D471297A83178976FF871"

Assert-True (Test-Path $DocPath) "v0.7.26 blocked doc exists"
Assert-True (Test-Path $BlockerJson) "blocker JSON exists outside repo"
Assert-True (Test-Path $BlockerMd) "blocker MD exists outside repo"
Assert-True (Test-Path $SuspiciousHits) "suspicious hits JSON exists outside repo"
Assert-True (Test-Path $PackageZip) "local package ZIP exists"
Assert-True ($PackageZip -notmatch "\\OneDrive\\") "ZIP is not in OneDrive"
Assert-True ($PackageZip -notmatch "\\public_html\\") "ZIP is not in public web folder"

$ActualSha = (Get-FileHash -Algorithm SHA256 -Path $PackageZip).Hash.ToUpperInvariant()
Assert-True ($ActualSha -eq $ExpectedSha) "ZIP SHA256 matches expected"

$Doc = Get-Content $DocPath -Raw -Encoding UTF8
Assert-Contains $Doc "VOILA_V0_7_26_HUMAN_BROWSER_READINESS_BLOCKED_NO_DELIVERY=FAIL" "doc records final blocked marker"
Assert-Contains $Doc "NO_SHARE" "doc records no share"
Assert-Contains $Doc "NO_DELIVERY" "doc records no delivery"
Assert-Contains $Doc "NO_PUBLIC_RELEASE" "doc records no public release"
Assert-Contains $Doc "Do not deliver this package to testers." "doc blocks tester delivery"
Assert-Contains $Doc "Generated Romanian course text shows corrupted/incorrect diacritics/OCR output." "doc records diacritic/OCR blocker"
Assert-Contains $Doc "Extracted package browser session becomes very slow / unresponsive." "doc records responsiveness blocker"

$BlockerJsonText = Get-Content $BlockerJson -Raw -Encoding UTF8
Assert-Contains $BlockerJsonText "BLOCKED_FAIL" "blocker JSON records blocked fail"

$GitStatus = @(git status --porcelain)
Assert-True (@($GitStatus | Where-Object { $_ -match "\.zip($|\s)" }).Count -eq 0) "git status does not include ZIP artifact"
Assert-True (@($GitStatus | Where-Object { $_ -match "OneDrive|share-folder|controlled-tester-share-folder" }).Count -eq 0) "git status does not include OneDrive/share artifact"

Write-Host ""
Write-Host "VOILA_V0_7_26_HUMAN_BROWSER_READINESS_BLOCKED_NO_DELIVERY=FAIL"
