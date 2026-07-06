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

$WebAppPath = Join-Path $RepoRoot "services/api/web_app.py"
$DocPath = Join-Path $RepoRoot "docs/dev/v0.7.27-generated-romanian-diacritics-and-responsiveness-fix-no-delivery.md"

Assert-True (Test-Path $WebAppPath) "web_app.py exists"
Assert-True (Test-Path $DocPath) "v0.7.27 doc exists"

$WebApp = Get-Content $WebAppPath -Raw -Encoding UTF8
$Doc = Get-Content $DocPath -Raw -Encoding UTF8

Assert-Contains $WebApp "def _voila_v0727_normalize_romanian_ocr_display_text" "Romanian OCR display normalizer exists"
Assert-Contains $WebApp "def _voila_v0727_polish_html_response_text" "HTML response polish helper exists"
Assert-Contains $WebApp '@app.middleware("http")' "HTML response middleware exists"
Assert-Contains $WebApp "text/html" "middleware targets HTML only"
Assert-Contains $WebApp "ǎ" "normalizer handles caron a artifact"
Assert-Contains $WebApp "˘a" "normalizer handles breve-before-a artifact"
Assert-Contains $WebApp "s¸" "normalizer handles s cedilla artifact"
Assert-Contains $WebApp "t¸" "normalizer handles t cedilla artifact"
Assert-Contains $WebApp "ş" "normalizer handles legacy s cedilla"
Assert-Contains $WebApp "ţ" "normalizer handles legacy t cedilla"
Assert-Contains $WebApp "voila-v0727-bottom-nav-polish" "bottom nav CSS marker exists"
Assert-Contains $WebApp "position: static !important" "bottom nav is forced non-overlapping/static"
Assert-Contains $WebApp "_voila_v0727_remove_duplicate_bottom_nav_blocks" "duplicate bottom nav guard exists"
Assert-Contains $WebApp "content-length" "middleware removes stale content-length"

Assert-Contains $Doc "NO_SHARE" "doc records no share"
Assert-Contains $Doc "NO_DELIVERY" "doc records no delivery"
Assert-Contains $Doc "NO_PUBLIC_RELEASE" "doc records no public release"
Assert-Contains $Doc "NO_BUILD" "doc records no build"
Assert-Contains $Doc "NO_ZIP" "doc records no ZIP"
Assert-Contains $Doc "not a tester delivery milestone" "doc blocks tester delivery"

Write-Host ""
Write-Host "--- Python compile ---"
$PythonCandidates = @(
    (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
    "python",
    "py"
)
$PythonExe = $null
foreach ($Candidate in $PythonCandidates) {
    if ($Candidate -like "*\python.exe") {
        if (Test-Path $Candidate) { $PythonExe = $Candidate; break }
    } else {
        $Cmd = Get-Command $Candidate -ErrorAction SilentlyContinue
        if ($null -ne $Cmd) { $PythonExe = $Candidate; break }
    }
}
Assert-True (-not [string]::IsNullOrWhiteSpace($PythonExe)) "Python executable found"

& $PythonExe -m py_compile $WebAppPath
if ($LASTEXITCODE -ne 0) { throw "Python compile failed for web_app.py" }
Write-Host "[PASS] Python compile passed"

Write-Host ""
Write-Host "--- Mapping smoke ---"
$Sample = "Dacǎ existǎ o vecin˘atate si o condi¸tie; func¸tie cu ş si ţ."
$Fixed = $Sample.
    Replace("ǎ", "ă").
    Replace("˘a", "ă").
    Replace("¸t", "ț").
    Replace("¸T", "Ț").
    Replace("t¸", "ț").
    Replace("s¸", "ș").
    Replace("ş", "ș").
    Replace("ţ", "ț")
Assert-Contains $Fixed "Dacă există" "mapping smoke repairs Dacă există"
Assert-Contains $Fixed "vecinătate" "mapping smoke repairs vecinătate"
Assert-Contains $Fixed "condiție" "mapping smoke repairs condiție"
Assert-Contains $Fixed "funcție" "mapping smoke repairs funcție"

Write-Host ""
Write-Host "--- No delivery artifacts ---"
$GitStatus = @(git status --porcelain)
Assert-True (@($GitStatus | Where-Object { $_ -match "\.zip($|\s)" }).Count -eq 0) "git status does not include ZIP artifact"
Assert-True (@($GitStatus | Where-Object { $_ -match "OneDrive|share-folder|controlled-tester-share-folder" }).Count -eq 0) "git status does not include OneDrive/share artifact"

Write-Host ""
Write-Host "VOILA_V0_7_27_GENERATED_ROMANIAN_DIACRITICS_AND_RESPONSIVENESS_FIX_NO_DELIVERY_CHECK=PASS"
