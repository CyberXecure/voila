# v0.7.21 controlled ZIP review and delivery readiness, no share
# Reviews the existing v0.7.20 local ZIP candidate only.
# Policy: no build, no new ZIP, no share, no delivery, no distribution, no OneDrive, no GitHub release.
# Expected marker:
# VOILA_V0_7_21_CONTROLLED_ZIP_REVIEW_AND_DELIVERY_READINESS_NO_SHARE_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$PreviousReleaseRoot = "D:\dev\release-assets\voila\v0.7.20-controlled-tester-zip-preparation-no-delivery",
    [string]$ReviewRoot = "D:\dev\release-assets\voila\v0.7.21-controlled-zip-review-and-delivery-readiness-no-share",
    [string]$PackageName = "voila-v0.7.20-controlled-tester-windows-package-candidate",
    [switch]$AllowDirtyWorktree,
    [switch]$SkipExtractReview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_21_CONTROLLED_ZIP_REVIEW_AND_DELIVERY_READINESS_NO_SHARE_CHECK=PASS"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Write-Pass {
    param([string]$Message)
    Write-Host "PASS: $Message"
}

function Write-WarnLine {
    param([string]$Message)
    Write-Host "WARN: $Message"
}

function Fail {
    param([string]$Message)
    throw "FAIL: $Message"
}

function Assert-File {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Assert-Dir {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Assert-TextContains {
    param(
        [string]$Path,
        [string]$Pattern,
        [string]$Label
    )
    Assert-File $Path $Label
    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ($text -notmatch $Pattern) {
        Fail "$Label does not contain expected pattern: $Pattern"
    }
    Write-Pass "$Label contains expected pattern"
}

function Normalize-ZipEntryName {
    param([string]$Name)
    return ($Name -replace "\\", "/").TrimStart("/")
}

function Get-ZipEntries {
    param([string]$ZipPath)

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        return @($zip.Entries | ForEach-Object { Normalize-ZipEntryName $_.FullName })
    }
    finally {
        $zip.Dispose()
    }
}

function Assert-ZipContains {
    param(
        [string[]]$Entries,
        [string]$Expected,
        [string]$Label
    )

    $needle = Normalize-ZipEntryName $Expected
    if ($Entries -notcontains $needle) {
        Fail "$Label missing from ZIP: $needle"
    }
    Write-Pass "$Label found in ZIP"
}

function Assert-ZipDoesNotMatch {
    param(
        [string[]]$Entries,
        [string[]]$ForbiddenPatterns
    )

    foreach ($entry in $Entries) {
        foreach ($pattern in $ForbiddenPatterns) {
            if ($entry -match $pattern) {
                Fail "forbidden ZIP entry detected: $entry matches $pattern"
            }
        }
    }
    Write-Pass "forbidden ZIP entry scan passed"
}

function Get-JsonFile {
    param([string]$Path, [string]$Label)

    Assert-File $Path $Label
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        Fail "$Label is not valid JSON: $($_.Exception.Message)"
    }
}

function Assert-FalseLike {
    param($Value, [string]$Label)

    $isFalse = $false
    if ($Value -is [bool]) {
        $isFalse = (-not $Value)
    }
    elseif ($null -ne $Value) {
        $isFalse = (("$Value").ToLowerInvariant() -eq "false")
    }

    if (-not $isFalse) {
        Fail "$Label expected false but got: $Value"
    }
    Write-Pass "$Label=false"
}

function New-CleanDirectory {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Invoke-ExtractedPyCompile {
    param([string]$ExtractRoot)

    $venvPython = Join-Path $ExtractRoot ".venv\Scripts\python.exe"
    $python = if (Test-Path -LiteralPath $venvPython -PathType Leaf) { $venvPython } else { "python" }

    $targets = @(
        "services\api\web_app.py",
        "services\api\exam_prep.py",
        "services\api\study_quiz_builder.py",
        "services\api\ocr_math_report.py",
        "services\api\ocr_math_normalizer.py"
    )

    foreach ($target in $targets) {
        $full = Join-Path $ExtractRoot $target
        if (Test-Path -LiteralPath $full -PathType Leaf) {
            Write-Host "extracted_py_compile: $target"
            & $python -m py_compile $full
            if ($LASTEXITCODE -ne 0) {
                Fail "extracted py_compile failed: $target"
            }
            Write-Pass "extracted py_compile $target"
        }
        else {
            Write-WarnLine "extracted py_compile target missing, skipped: $target"
        }
    }
}

function Count-Files {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return 0
    }
    return @(Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue).Length
}

Write-Host "SCRIPT_VERSION=v0.7.21-controlled-zip-review-and-delivery-readiness-no-share-1"

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Step "v0.7.21 policy guard"
Assert-Dir $RepoRoot "repo root"
Assert-Dir (Join-Path $RepoRoot ".git") "git metadata"

Push-Location $RepoRoot
try {
    $topLevel = (& git rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0) { Fail "not a git repo" }
    if ((Resolve-Path -LiteralPath $topLevel).Path -ne $RepoRoot) {
        Fail "repo root mismatch: expected $RepoRoot but git top-level is $topLevel"
    }

    $branch = (& git branch --show-current).Trim()
    $head = (& git rev-parse --short HEAD).Trim()
    $fullHead = (& git rev-parse HEAD).Trim()

    Write-Host "BRANCH=$branch"
    Write-Host "HEAD=$head"

    $status = @(& git status --short)
    if (@($status).Length -gt 0 -and -not $AllowDirtyWorktree) {
        $status | ForEach-Object { Write-Host $_ }
        Fail "worktree is dirty. Use -AllowDirtyWorktree only while testing the new milestone files before commit."
    }
    elseif (@($status).Length -gt 0 -and $AllowDirtyWorktree) {
        Write-WarnLine "worktree is dirty but allowed for pre-commit milestone check"
        $status | ForEach-Object { Write-Host $_ }
    }
    else {
        Write-Pass "worktree clean"
    }

    Write-Host "NO_BUILD=PASS"
    Write-Host "NO_NEW_ZIP=PASS"
    Write-Host "NO_SHARE=PASS"
    Write-Host "NO_DELIVERY=PASS"
    Write-Host "NO_DISTRIBUTION=PASS"
    Write-Host "ONEDRIVE_SHARE_CREATED=false"
    Write-Host "GITHUB_RELEASE_CREATED=false"
    Write-Host "DELIVERY_APPROVED=false"
    Write-Host "SHARE_ALLOWED_NOW=false"

    Write-Step "Baseline v0.7.20 files and marker"
    $v020Check = Join-Path $RepoRoot "scripts\dev\check-controlled-tester-zip-preparation-no-delivery.ps1"
    $v020Doc = Join-Path $RepoRoot "docs\dev\v0.7.20-controlled-tester-zip-preparation-no-delivery.md"
    Assert-File $v020Check "v0.7.20 check script"
    Assert-File $v020Doc "v0.7.20 doc"

    $v020Text = Get-Content -LiteralPath $v020Check -Raw -Encoding UTF8
    if ($v020Text -notmatch "VOILA_V0_7_20_CONTROLLED_TESTER_ZIP_PREPARATION_NO_DELIVERY_CHECK=PASS") {
        Fail "v0.7.20 final marker missing from v0.7.20 script"
    }
    Write-Pass "v0.7.20 marker present in check script"

    Write-Step "Existing v0.7.20 ZIP artifacts"
    Assert-Dir $PreviousReleaseRoot "previous v0.7.20 release asset root"

    $zipPath = Join-Path $PreviousReleaseRoot "$PackageName.zip"
    $shaPath = "$zipPath.sha256"
    $manifestPath = Join-Path $PreviousReleaseRoot "ZIP-PREPARATION-MANIFEST.json"
    $summaryPath = Join-Path $PreviousReleaseRoot "ZIP-PREPARATION-SUMMARY.txt"
    $noDeliveryPath = Join-Path $PreviousReleaseRoot "NO-DELIVERY-NOTICE.txt"

    Assert-File $zipPath "v0.7.20 ZIP candidate"
    Assert-File $shaPath "v0.7.20 ZIP SHA256"
    Assert-File $manifestPath "v0.7.20 ZIP manifest"
    Assert-File $summaryPath "v0.7.20 ZIP summary"
    Assert-File $noDeliveryPath "v0.7.20 release no-delivery notice"

    Write-Step "SHA256 verification"
    $zipItem = Get-Item -LiteralPath $zipPath
    $hash = Get-FileHash -LiteralPath $zipPath -Algorithm SHA256
    $shaText = Get-Content -LiteralPath $shaPath -Raw -Encoding ASCII

    if ($shaText -notmatch [regex]::Escape($hash.Hash)) {
        Fail "SHA256 file does not contain computed hash. computed=$($hash.Hash)"
    }

    Write-Pass "SHA256 file matches computed hash"
    Write-Host "zip_path=$zipPath"
    Write-Host "zip_sha256=$($hash.Hash)"
    Write-Host "zip_size_bytes=$($zipItem.Length)"

    Write-Step "Manifest policy verification"
    $manifest = Get-JsonFile -Path $manifestPath -Label "v0.7.20 manifest"

    if ($manifest.sha256 -ne $hash.Hash) {
        Fail "manifest sha256 mismatch: manifest=$($manifest.sha256) computed=$($hash.Hash)"
    }
    Write-Pass "manifest sha256 matches computed hash"

    if ([int64]$manifest.zip_size_bytes -ne [int64]$zipItem.Length) {
        Fail "manifest zip_size_bytes mismatch: manifest=$($manifest.zip_size_bytes) actual=$($zipItem.Length)"
    }
    Write-Pass "manifest zip size matches actual ZIP size"

    Assert-FalseLike $manifest.installer_created "manifest.installer_created"
    Assert-FalseLike $manifest.onedrive_share_created "manifest.onedrive_share_created"
    Assert-FalseLike $manifest.github_release_created "manifest.github_release_created"
    Assert-FalseLike $manifest.delivery_performed "manifest.delivery_performed"
    Assert-FalseLike $manifest.distribution_performed "manifest.distribution_performed"

    if ("$($manifest.final_marker)" -ne "VOILA_V0_7_20_CONTROLLED_TESTER_ZIP_PREPARATION_NO_DELIVERY_CHECK=PASS") {
        Fail "manifest final marker mismatch: $($manifest.final_marker)"
    }
    Write-Pass "manifest final marker matches v0.7.20"

    Assert-TextContains -Path $summaryPath -Pattern "delivery_performed=false" -Label "v0.7.20 summary"
    Assert-TextContains -Path $summaryPath -Pattern "distribution_performed=false" -Label "v0.7.20 summary"
    Assert-TextContains -Path $noDeliveryPath -Pattern "delivery_performed=false" -Label "v0.7.20 no-delivery notice"
    Assert-TextContains -Path $noDeliveryPath -Pattern "distribution_performed=false" -Label "v0.7.20 no-delivery notice"

    Write-Step "ZIP entry inventory and forbidden content scan"
    $entries = Get-ZipEntries -ZipPath $zipPath
    $entryCount = @($entries).Length
    Write-Host "zip_entry_count=$entryCount"

    if ($entryCount -lt 100) {
        Fail "ZIP entry count unexpectedly low: $entryCount"
    }

    Assert-ZipContains -Entries $entries -Expected "services/api/web_app.py" -Label "web_app.py"
    Assert-ZipContains -Entries $entries -Expected "scripts/dev/start-voila.ps1" -Label "start-voila.ps1"
    Assert-ZipContains -Entries $entries -Expected "scripts/dev/stop-voila.ps1" -Label "stop-voila.ps1"
    Assert-ZipContains -Entries $entries -Expected "START-VOILA.bat" -Label "START-VOILA.bat"
    Assert-ZipContains -Entries $entries -Expected "STOP-VOILA.bat" -Label "STOP-VOILA.bat"
    Assert-ZipContains -Entries $entries -Expected "README-TESTERS-v0.7.20.txt" -Label "README-TESTERS-v0.7.20.txt"
    Assert-ZipContains -Entries $entries -Expected "NO-DELIVERY-NOTICE.txt" -Label "package no-delivery notice"
    Assert-ZipContains -Entries $entries -Expected "data/README-EMPTY-DATA.txt" -Label "empty data README"

    $venvPythonEntry = ".venv/Scripts/python.exe"
    $venvIncluded = $entries -contains $venvPythonEntry
    Write-Host "venv_included=$venvIncluded"
    if ($manifest.venv_included -and -not $venvIncluded) {
        Fail "manifest says venv included but .venv/Scripts/python.exe is absent from ZIP"
    }

    Assert-ZipDoesNotMatch -Entries $entries -ForbiddenPatterns @(
        "^\.git(/|$)",
        "^\.release-cache(/|$)",
        "^data/input/.+",
        "^data/output/.+",
        "(^|/)\.env($|[./])",
        "\.zip$",
        "\.7z$",
        "\.rar$"
    )

    Write-Step "Create local review reports only"
    New-Item -ItemType Directory -Force -Path $ReviewRoot | Out-Null

    $reviewManifestPath = Join-Path $ReviewRoot "ZIP-REVIEW-MANIFEST.json"
    $readinessSummaryPath = Join-Path $ReviewRoot "DELIVERY-READINESS-NO-SHARE-SUMMARY.txt"
    $reviewNoShareNoticePath = Join-Path $ReviewRoot "NO-SHARE-NO-DELIVERY-NOTICE.txt"

    $extractRoot = Join-Path $ReviewRoot "extract-review"
    $extractedPackageRoot = Join-Path $extractRoot $PackageName

    $extractionPerformed = $false
    $extractedDataInputFileCount = $null
    $extractedDataOutputFileCount = $null
    $extractedPyCompilePassed = $false

    if (-not $SkipExtractReview) {
        Write-Step "Extract ZIP to local review folder"
        New-CleanDirectory -Path $extractRoot
        Expand-Archive -LiteralPath $zipPath -DestinationPath $extractedPackageRoot -Force
        $extractionPerformed = $true

        Assert-File (Join-Path $extractedPackageRoot "services\api\web_app.py") "extracted web_app.py"
        Assert-File (Join-Path $extractedPackageRoot "scripts\dev\start-voila.ps1") "extracted start-voila.ps1"
        Assert-File (Join-Path $extractedPackageRoot "scripts\dev\stop-voila.ps1") "extracted stop-voila.ps1"
        Assert-File (Join-Path $extractedPackageRoot "START-VOILA.bat") "extracted START-VOILA.bat"
        Assert-File (Join-Path $extractedPackageRoot "STOP-VOILA.bat") "extracted STOP-VOILA.bat"
        Assert-File (Join-Path $extractedPackageRoot "README-TESTERS-v0.7.20.txt") "extracted tester README"
        Assert-File (Join-Path $extractedPackageRoot "NO-DELIVERY-NOTICE.txt") "extracted package no-delivery notice"

        Assert-TextContains -Path (Join-Path $extractedPackageRoot "README-TESTERS-v0.7.20.txt") -Pattern "non-confidential" -Label "extracted tester README"
        Assert-TextContains -Path (Join-Path $extractedPackageRoot "NO-DELIVERY-NOTICE.txt") -Pattern "delivery_performed=false" -Label "extracted package no-delivery notice"
        Assert-TextContains -Path (Join-Path $extractedPackageRoot "NO-DELIVERY-NOTICE.txt") -Pattern "distribution_performed=false" -Label "extracted package no-delivery notice"

        $extractedDataInputFileCount = Count-Files -Path (Join-Path $extractedPackageRoot "data\input")
        $extractedDataOutputFileCount = Count-Files -Path (Join-Path $extractedPackageRoot "data\output")
        Write-Host "extracted_data_input_file_count=$extractedDataInputFileCount"
        Write-Host "extracted_data_output_file_count=$extractedDataOutputFileCount"

        if ($extractedDataInputFileCount -ne 0 -or $extractedDataOutputFileCount -ne 0) {
            Fail "extracted package contains data/input or data/output files"
        }
        Write-Pass "extracted data/input and data/output are empty"

        Write-Step "Extracted package Python syntax sanity"
        Invoke-ExtractedPyCompile -ExtractRoot $extractedPackageRoot
        $extractedPyCompilePassed = $true
    }
    else {
        Write-WarnLine "extract review skipped by parameter"
    }

    $reviewManifest = [ordered]@{
        milestone = "v0.7.21-controlled-zip-review-and-delivery-readiness-no-share"
        repo_root = $RepoRoot
        git_branch = $branch
        git_head_short = $head
        git_head = $fullHead
        previous_release_root = $PreviousReleaseRoot
        review_root = $ReviewRoot
        package_name = $PackageName
        reviewed_zip_path = $zipPath
        reviewed_sha256_path = $shaPath
        reviewed_manifest_path = $manifestPath
        reviewed_summary_path = $summaryPath
        reviewed_no_delivery_notice_path = $noDeliveryPath
        zip_sha256 = $hash.Hash
        zip_size_bytes = $zipItem.Length
        zip_entry_count = $entryCount
        venv_included = [bool]$venvIncluded
        extraction_performed = [bool]$extractionPerformed
        extracted_package_root = $extractedPackageRoot
        extracted_data_input_file_count = $extractedDataInputFileCount
        extracted_data_output_file_count = $extractedDataOutputFileCount
        extracted_py_compile_passed = [bool]$extractedPyCompilePassed
        forbidden_zip_entries_detected = $false
        sha256_verified = $true
        manifest_verified = $true
        required_entries_verified = $true
        no_share = $true
        no_delivery = $true
        no_distribution = $true
        no_new_zip_created = $true
        no_build = $true
        onedrive_share_created = $false
        github_release_created = $false
        delivery_performed = $false
        distribution_performed = $false
        delivery_approved = $false
        share_allowed_now = $false
        policy = "review existing local ZIP candidate only; no share; no delivery; no distribution"
        final_marker = $Marker
    }

    $reviewManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reviewManifestPath -Encoding UTF8

    $readinessSummary = @"
Voila v0.7.21 controlled ZIP review and delivery readiness — no share

Reviewed ZIP:
$zipPath

SHA256:
$($hash.Hash)

ZIP size bytes:
$($zipItem.Length)

ZIP entry count:
$entryCount

Review results:
sha256_verified=true
manifest_verified=true
required_entries_verified=true
forbidden_zip_entries_detected=false
venv_included=$venvIncluded
extraction_performed=$extractionPerformed
extracted_data_input_file_count=$extractedDataInputFileCount
extracted_data_output_file_count=$extractedDataOutputFileCount
extracted_py_compile_passed=$extractedPyCompilePassed

Policy:
no_build=true
no_new_zip_created=true
no_share=true
no_delivery=true
no_distribution=true
onedrive_share_created=false
github_release_created=false
delivery_performed=false
distribution_performed=false
delivery_approved=false
share_allowed_now=false

Interpretation:
The existing v0.7.20 ZIP candidate passed local review and is delivery-ready from a technical checklist perspective only.
This is NOT approval to send, upload, publish, share, or distribute the ZIP.
A separate explicit delivery/share milestone is required before any tester access is created.
"@
    Set-Content -LiteralPath $readinessSummaryPath -Value $readinessSummary -Encoding UTF8

    $reviewNoShareNotice = @"
NO SHARE / NO DELIVERY NOTICE

This v0.7.21 milestone reviewed the existing local v0.7.20 ZIP candidate only.

no_new_zip_created=true
no_share=true
no_delivery=true
no_distribution=true
onedrive_share_created=false
github_release_created=false
delivery_performed=false
distribution_performed=false
delivery_approved=false
share_allowed_now=false

Separate explicit approval is required before any OneDrive share, link creation, GitHub release, upload, or tester delivery.
"@
    Set-Content -LiteralPath $reviewNoShareNoticePath -Value $reviewNoShareNotice -Encoding UTF8

    Assert-File $reviewManifestPath "v0.7.21 review manifest"
    Assert-File $readinessSummaryPath "v0.7.21 readiness summary"
    Assert-File $reviewNoShareNoticePath "v0.7.21 no-share notice"

    Write-Step "Final v0.7.21 result"
    Write-Host "controlled_zip_review_passed=true"
    Write-Host "delivery_readiness_review_passed=true"
    Write-Host "reviewed_zip_path=$zipPath"
    Write-Host "zip_sha256=$($hash.Hash)"
    Write-Host "zip_size_bytes=$($zipItem.Length)"
    Write-Host "zip_entry_count=$entryCount"
    Write-Host "review_manifest_path=$reviewManifestPath"
    Write-Host "readiness_summary_path=$readinessSummaryPath"
    Write-Host "no_share_notice_path=$reviewNoShareNoticePath"
    Write-Host "no_build=true"
    Write-Host "no_new_zip_created=true"
    Write-Host "no_share=true"
    Write-Host "no_delivery=true"
    Write-Host "no_distribution=true"
    Write-Host "onedrive_share_created=false"
    Write-Host "github_release_created=false"
    Write-Host "delivery_performed=false"
    Write-Host "distribution_performed=false"
    Write-Host "delivery_approved=false"
    Write-Host "share_allowed_now=false"
    Write-Host "NO_SHARE=PASS"
    Write-Host "NO_DELIVERY=PASS"
    Write-Host "NO_DISTRIBUTION=PASS"
    Write-Host $Marker
}
finally {
    Pop-Location
}
