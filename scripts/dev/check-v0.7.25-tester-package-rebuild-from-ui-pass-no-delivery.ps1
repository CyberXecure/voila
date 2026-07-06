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
    param([string]$Haystack, [string]$Needle, [string]$Message)
    if ($null -eq $Haystack -or -not $Haystack.Contains($Needle)) {
        throw "[FAIL] $Message -- missing: $Needle"
    }
    Write-Host "[PASS] $Message"
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$DocPath = Join-Path $RepoRoot "docs\dev\v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery.md"
$ResultPath = 'D:\dev\release-assets\voila\v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery\V0.7.25-PACKAGE-REBUILD-NO-DELIVERY-RESULT.json'
$ZipPath = 'D:\dev\release-assets\voila\v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery\voila-v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery.zip'
$ShaPath = 'D:\dev\release-assets\voila\v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery\voila-v0.7.25-tester-package-rebuild-from-ui-pass-no-delivery.zip.sha256'
$ExpectedSha = 'E985D813040CDE9ACDA9706C479429BF879FB1D5D36D471297A83178976FF871'
$ExtractedRepoRoot = 'D:\dev\tester-runs\voila-v0.7.25-package-rebuild-from-ui-pass-no-delivery\voila'
$ExtractedWebApp = Join-Path $ExtractedRepoRoot "services\api\web_app.py"

Assert-True (Test-Path $DocPath) "v0.7.25 doc exists"
Assert-True (Test-Path $ResultPath) "v0.7.25 local result JSON exists"
Assert-True (Test-Path $ZipPath) "v0.7.25 ZIP exists"
Assert-True (Test-Path $ShaPath) "v0.7.25 SHA256 file exists"
Assert-True ($ZipPath -notmatch "\\OneDrive\\") "ZIP is not in OneDrive"
Assert-True ($ZipPath -notmatch "\\public_html\\") "ZIP is not in public web folder"

$ActualSha = (Get-FileHash -Algorithm SHA256 -Path $ZipPath).Hash.ToUpperInvariant()
Assert-True ($ActualSha -eq $ExpectedSha) "ZIP SHA256 matches recorded hash"

$ShaText = Get-Content $ShaPath -Raw -Encoding ASCII
Assert-Contains $ShaText $ExpectedSha "SHA256 file records hash"

$Doc = Get-Content $DocPath -Raw -Encoding UTF8
Assert-Contains $Doc "NO_SHARE" "doc records no share"
Assert-Contains $Doc "NO_DELIVERY" "doc records no delivery"
Assert-Contains $Doc "NO_PUBLIC_RELEASE" "doc records no public release"
Assert-Contains $Doc "No tester delivery is allowed from this milestone." "doc blocks delivery"

Assert-True (Test-Path $ExtractedWebApp) "extracted web_app.py exists"
$WebApp = Get-Content $ExtractedWebApp -Raw -Encoding UTF8
Assert-Contains $WebApp "def ensure_course_html_for_pdf" "extracted package has HTML ensure helper"
Assert-Contains $WebApp "Generated · HTML pending" "extracted package has truthful homepage status"
Assert-Contains $WebApp '@app.get("/course-open")' "extracted package has course-open route"
Assert-Contains $WebApp "OCR Math Diagnostic" "extracted package has OCR Math Diagnostic"
Assert-Contains $WebApp "voila-tester-flow-bottom-nav-v0724" "extracted package has bottom nav injection"
Assert-Contains $WebApp "fixedCourseToolsLink" "extracted package has Course Tools fixed nav"
Assert-Contains $WebApp "fixedExamPrepLink" "extracted package has Exam Prep fixed nav"

Assert-True (Test-Path (Join-Path $ExtractedRepoRoot "README-WINDOWS.txt")) "extracted package has README-WINDOWS.txt"
Assert-True (Test-Path (Join-Path $ExtractedRepoRoot "RELEASE-NOTES.txt")) "extracted package has RELEASE-NOTES.txt"
Assert-True (-not (Test-Path (Join-Path $ExtractedRepoRoot "docs\commercial"))) "extracted package has no docs/commercial"
Assert-True (Test-Path (Join-Path $ExtractedRepoRoot "START-VOILA.bat")) "extracted package has START-VOILA.bat"
Assert-True (Test-Path (Join-Path $ExtractedRepoRoot "STOP-VOILA.bat")) "extracted package has STOP-VOILA.bat"
Assert-True (Test-Path (Join-Path $ExtractedRepoRoot ".venv\Scripts\python.exe")) "extracted package has packaged Python venv"
Assert-True (Test-Path (Join-Path $ExtractedRepoRoot "scripts\dev\check-tester-ui-generation-navigation-and-ocr-math-reality-fix-no-delivery.ps1")) "extracted package has v0.7.24 UI gate check"

$GitStatusLines = @(git status --porcelain)
$ZipStatus = @($GitStatusLines | Where-Object { $_ -match "\.zip($|\s)" })
$ShareStatus = @($GitStatusLines | Where-Object { $_ -match "OneDrive|share-folder|controlled-tester-share-folder" })
Assert-True ($ZipStatus.Count -eq 0) "git status does not include ZIP artifact"
Assert-True ($ShareStatus.Count -eq 0) "git status does not include OneDrive/share artifact"

Write-Host ""
Write-Host "VOILA_V0_7_25_TESTER_PACKAGE_REBUILD_FROM_UI_PASS_NO_DELIVERY_CHECK=PASS"
