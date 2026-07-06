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

$DocPath = Join-Path $RepoRoot "docs/dev/v0.7.28-source-browser-validation-blocked-no-delivery.md"
$BlockerJson = "D:\dev\tester-runs\voila-v0.7.28-source-browser-validation-no-delivery\blocker-evidence\V0.7.28-SOURCE-BROWSER-VALIDATION-BLOCKED.json"
$BlockerMd = "D:\dev\tester-runs\voila-v0.7.28-source-browser-validation-no-delivery\blocker-evidence\V0.7.28-SOURCE-BROWSER-VALIDATION-BLOCKED.md"
$RawScriptHits = "D:\dev\tester-runs\voila-v0.7.28-source-browser-validation-no-delivery\blocker-evidence\raw-script-marker-hits.json"

Assert-True (Test-Path $DocPath) "v0.7.28 blocked doc exists"
Assert-True (Test-Path $BlockerJson) "blocker JSON exists outside repo"
Assert-True (Test-Path $BlockerMd) "blocker MD exists outside repo"
Assert-True (Test-Path $RawScriptHits) "raw script hits JSON exists outside repo"

$Doc = Get-Content $DocPath -Raw -Encoding UTF8
Assert-Contains $Doc "VOILA_V0_7_28_SOURCE_BROWSER_VALIDATION_BLOCKED_NO_DELIVERY=FAIL" "doc records final blocked marker"
Assert-Contains $Doc "NO_SHARE" "doc records no share"
Assert-Contains $Doc "NO_DELIVERY" "doc records no delivery"
Assert-Contains $Doc "NO_PUBLIC_RELEASE" "doc records no public release"
Assert-Contains $Doc "NO_BUILD" "doc records no build"
Assert-Contains $Doc "NO_ZIP" "doc records no ZIP"
Assert-Contains $Doc "OCR Review / Correct OCR page displays raw JavaScript text in the browser." "doc records raw JS blocker"
Assert-Contains $Doc "OCR Math link/action does not open reliably." "doc records OCR Math blocker"
Assert-Contains $Doc "Course navigation remains visually duplicated/overlapping/heavy." "doc records navigation blocker"
Assert-Contains $Doc "Do not rebuild ZIP." "doc blocks ZIP rebuild"
Assert-Contains $Doc "Do not deliver this package to testers." "doc blocks delivery"

$BlockerJsonText = Get-Content $BlockerJson -Raw -Encoding UTF8
Assert-Contains $BlockerJsonText "BLOCKED_FAIL" "blocker JSON records blocked fail"

$GitStatus = @(git status --porcelain)
Assert-True (@($GitStatus | Where-Object { $_ -match "\.zip($|\s)" }).Count -eq 0) "git status does not include ZIP artifact"
Assert-True (@($GitStatus | Where-Object { $_ -match "OneDrive|share-folder|controlled-tester-share-folder" }).Count -eq 0) "git status does not include OneDrive/share artifact"

Write-Host ""
Write-Host "VOILA_V0_7_28_SOURCE_BROWSER_VALIDATION_BLOCKED_NO_DELIVERY=FAIL"
