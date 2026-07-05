# v0.7.22 controlled tester share preparation, no public release
# Prepares a local OneDrive controlled tester share folder from the reviewed v0.7.20 ZIP candidate.
# Policy: no public release, no GitHub release, no generated share link, no broadcast delivery.
# Expected marker:
# VOILA_V0_7_22_CONTROLLED_TESTER_SHARE_PREPARATION_NO_PUBLIC_RELEASE_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$ReviewedReleaseRoot = "D:\dev\release-assets\voila\v0.7.20-controlled-tester-zip-preparation-no-delivery",
    [string]$ReviewRoot = "D:\dev\release-assets\voila\v0.7.21-controlled-zip-review-and-delivery-readiness-no-share",
    [string]$SharePrepRoot = "D:\dev\release-assets\voila\v0.7.22-controlled-tester-share-preparation-no-public-release",
    [string]$OneDriveRoot = "$env:USERPROFILE\OneDrive",
    [string]$OneDriveTargetRelativePath = "CX Trading Lab\Voila\v0.7.22-controlled-tester-share-preparation-no-public-release",
    [string]$PackageName = "voila-v0.7.20-controlled-tester-windows-package-candidate",
    [switch]$AllowDirtyWorktree,
    [switch]$SkipOneDriveCopy
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_22_CONTROLLED_TESTER_SHARE_PREPARATION_NO_PUBLIC_RELEASE_CHECK=PASS"

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

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content,
        [string]$Encoding = "UTF8"
    )
    $dir = Split-Path -Parent $Path
    if ($dir) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Set-Content -LiteralPath $Path -Value $Content -Encoding $Encoding
}

function New-CleanDirectory {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Copy-FileChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Label
    )
    Assert-File $Source "$Label source"
    $destDir = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
    Assert-File $Destination "$Label destination"
}

function Compare-HashChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Label
    )
    $sourceHash = Get-FileHash -LiteralPath $Source -Algorithm SHA256
    $destHash = Get-FileHash -LiteralPath $Destination -Algorithm SHA256
    if ($sourceHash.Hash -ne $destHash.Hash) {
        Fail "$Label hash mismatch: source=$($sourceHash.Hash) destination=$($destHash.Hash)"
    }
    Write-Pass "$Label hash verified"
    return $destHash.Hash
}

function Load-JsonFile {
    param([string]$Path, [string]$Label)
    Assert-File $Path $Label
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        Fail "$Label is invalid JSON: $($_.Exception.Message)"
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

Write-Host "SCRIPT_VERSION=v0.7.22-controlled-tester-share-preparation-no-public-release-hotfix1"

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Step "v0.7.22 policy guard"
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
    Write-Host "NO_PUBLIC_RELEASE=PASS"
    Write-Host "NO_GITHUB_RELEASE=PASS"
    Write-Host "NO_SHARE_LINK_CREATED=PASS"
    Write-Host "NO_BROADCAST_DELIVERY=PASS"
    Write-Host "CONTROLLED_SHARE_PREPARATION_ONLY=PASS"
    Write-Host "PUBLIC_RELEASE_CREATED=false"
    Write-Host "GITHUB_RELEASE_CREATED=false"
    Write-Host "SHARE_LINK_CREATED=false"
    Write-Host "TESTER_EMAIL_SENT=false"
    Write-Host "PUBLIC_UPLOAD_PERFORMED=false"
    Write-Host "BROADCAST_DELIVERY_PERFORMED=false"

    Write-Step "Baseline v0.7.21 files and marker"
    $v021Check = Join-Path $RepoRoot "scripts\dev\check-controlled-zip-review-and-delivery-readiness-no-share.ps1"
    $v021Doc = Join-Path $RepoRoot "docs\dev\v0.7.21-controlled-zip-review-and-delivery-readiness-no-share.md"
    Assert-File $v021Check "v0.7.21 check script"
    Assert-File $v021Doc "v0.7.21 doc"

    $v021Text = Get-Content -LiteralPath $v021Check -Raw -Encoding UTF8
    if ($v021Text -notmatch "VOILA_V0_7_21_CONTROLLED_ZIP_REVIEW_AND_DELIVERY_READINESS_NO_SHARE_CHECK=PASS") {
        Fail "v0.7.21 final marker missing from v0.7.21 script"
    }
    Write-Pass "v0.7.21 marker present in check script"

    Write-Step "Reviewed ZIP source artifacts"
    Assert-Dir $ReviewedReleaseRoot "v0.7.20 reviewed release root"
    Assert-Dir $ReviewRoot "v0.7.21 review root"

    $zipPath = Join-Path $ReviewedReleaseRoot "$PackageName.zip"
    $shaPath = "$zipPath.sha256"
    $sourceManifestPath = Join-Path $ReviewedReleaseRoot "ZIP-PREPARATION-MANIFEST.json"
    $sourceSummaryPath = Join-Path $ReviewedReleaseRoot "ZIP-PREPARATION-SUMMARY.txt"
    $sourceNoDeliveryPath = Join-Path $ReviewedReleaseRoot "NO-DELIVERY-NOTICE.txt"

    $reviewManifestPath = Join-Path $ReviewRoot "ZIP-REVIEW-MANIFEST.json"
    $reviewSummaryPath = Join-Path $ReviewRoot "DELIVERY-READINESS-NO-SHARE-SUMMARY.txt"
    $reviewNoSharePath = Join-Path $ReviewRoot "NO-SHARE-NO-DELIVERY-NOTICE.txt"

    Assert-File $zipPath "reviewed ZIP candidate"
    Assert-File $shaPath "reviewed ZIP SHA256"
    Assert-File $sourceManifestPath "v0.7.20 source manifest"
    Assert-File $sourceSummaryPath "v0.7.20 source summary"
    Assert-File $sourceNoDeliveryPath "v0.7.20 source no-delivery notice"
    Assert-File $reviewManifestPath "v0.7.21 review manifest"
    Assert-File $reviewSummaryPath "v0.7.21 readiness summary"
    Assert-File $reviewNoSharePath "v0.7.21 no-share notice"

    Write-Step "SHA and manifest verification"
    $zipItem = Get-Item -LiteralPath $zipPath
    $hash = Get-FileHash -LiteralPath $zipPath -Algorithm SHA256
    $shaText = Get-Content -LiteralPath $shaPath -Raw -Encoding ASCII

    if ($shaText -notmatch [regex]::Escape($hash.Hash)) {
        Fail "SHA256 file does not contain computed hash. computed=$($hash.Hash)"
    }
    Write-Pass "SHA256 file matches computed hash"

    $sourceManifest = Load-JsonFile -Path $sourceManifestPath -Label "v0.7.20 manifest"
    $reviewManifest = Load-JsonFile -Path $reviewManifestPath -Label "v0.7.21 review manifest"

    if ($sourceManifest.sha256 -ne $hash.Hash) {
        Fail "v0.7.20 manifest sha256 mismatch: $($sourceManifest.sha256) vs $($hash.Hash)"
    }
    if ($reviewManifest.zip_sha256 -ne $hash.Hash) {
        Fail "v0.7.21 review manifest sha256 mismatch: $($reviewManifest.zip_sha256) vs $($hash.Hash)"
    }

    Write-Pass "v0.7.20/v0.7.21 manifests match ZIP SHA256"

    Assert-FalseLike $sourceManifest.installer_created "source_manifest.installer_created"
    Assert-FalseLike $sourceManifest.onedrive_share_created "source_manifest.onedrive_share_created"
    Assert-FalseLike $sourceManifest.github_release_created "source_manifest.github_release_created"
    Assert-FalseLike $sourceManifest.delivery_performed "source_manifest.delivery_performed"
    Assert-FalseLike $sourceManifest.distribution_performed "source_manifest.distribution_performed"

    Assert-FalseLike $reviewManifest.onedrive_share_created "review_manifest.onedrive_share_created"
    Assert-FalseLike $reviewManifest.github_release_created "review_manifest.github_release_created"
    Assert-FalseLike $reviewManifest.delivery_performed "review_manifest.delivery_performed"
    Assert-FalseLike $reviewManifest.distribution_performed "review_manifest.distribution_performed"
    Assert-FalseLike $reviewManifest.delivery_approved "review_manifest.delivery_approved"
    Assert-FalseLike $reviewManifest.share_allowed_now "review_manifest.share_allowed_now"

    Assert-TextContains -Path $reviewSummaryPath -Pattern "share_allowed_now=false" -Label "v0.7.21 readiness summary"
    Assert-TextContains -Path $reviewNoSharePath -Pattern "no_share=true" -Label "v0.7.21 no-share notice"

    Write-Step "Prepare local share-preparation root"
    New-CleanDirectory -Path $SharePrepRoot

    $localShareFolder = Join-Path $SharePrepRoot "controlled-tester-share-folder"
    New-Item -ItemType Directory -Force -Path $localShareFolder | Out-Null

    $targetZip = Join-Path $localShareFolder (Split-Path -Leaf $zipPath)
    $targetSha = Join-Path $localShareFolder (Split-Path -Leaf $shaPath)
    $targetSourceManifest = Join-Path $localShareFolder "ZIP-PREPARATION-MANIFEST.json"
    $targetSourceSummary = Join-Path $localShareFolder "ZIP-PREPARATION-SUMMARY.txt"
    $targetReviewManifest = Join-Path $localShareFolder "ZIP-REVIEW-MANIFEST.json"
    $targetReadinessSummary = Join-Path $localShareFolder "DELIVERY-READINESS-NO-SHARE-SUMMARY.txt"

    Copy-FileChecked -Source $zipPath -Destination $targetZip -Label "ZIP candidate"
    Copy-FileChecked -Source $shaPath -Destination $targetSha -Label "ZIP SHA256"
    Copy-FileChecked -Source $sourceManifestPath -Destination $targetSourceManifest -Label "source manifest"
    Copy-FileChecked -Source $sourceSummaryPath -Destination $targetSourceSummary -Label "source summary"
    Copy-FileChecked -Source $reviewManifestPath -Destination $targetReviewManifest -Label "review manifest"
    Copy-FileChecked -Source $reviewSummaryPath -Destination $targetReadinessSummary -Label "readiness summary"

    $targetZipHash = Compare-HashChecked -Source $zipPath -Destination $targetZip -Label "local share-prep ZIP"
    $targetShaHash = Compare-HashChecked -Source $shaPath -Destination $targetSha -Label "local share-prep SHA256 file"

    $testerReadmePath = Join-Path $localShareFolder "README-TESTERS-SHORT-v0.7.22.txt"
    $knownLimitationsPath = Join-Path $localShareFolder "KNOWN-LIMITATIONS-TESTERS-v0.7.22.txt"
    $controlledAccessPath = Join-Path $localShareFolder "CONTROLLED-ACCESS-NOTE-v0.7.22.txt"
    $noPublicReleasePath = Join-Path $localShareFolder "NO-PUBLIC-RELEASE-NOTICE-v0.7.22.txt"
    $linkNotCreatedPath = Join-Path $localShareFolder "SHARE-LINK-NOT-CREATED-v0.7.22.txt"

    Write-TextFile -Path $testerReadmePath -Content @"
Voila controlled tester ZIP candidate

Package:
$(Split-Path -Leaf $zipPath)

SHA256:
$($hash.Hash)

How to test:
1. Download the ZIP from the controlled folder only after access is explicitly granted.
2. Extract it to a local Windows folder.
3. Run START-VOILA.bat.
4. Open http://127.0.0.1:8787/ if the browser does not open automatically.
5. Use only small, non-confidential PDFs.

Please do not use:
- confidential files
- personal documents
- legal documents
- medical documents
- financial documents
- safety-critical documents

Testing focus:
- Upload
- Generate
- Course view
- Study
- Progress
- OCR Review / corrected OCR
- OCR Math report/viewer
- Exam Prep
- Quick tools

This folder is prepared for controlled tester access only.
No public release is approved.
"@

    Write-TextFile -Path $knownLimitationsPath -Content @"
Known limitations for controlled testers

- Windows local tester package candidate only.
- Large package because local runtime dependencies may be included.
- Use only small non-confidential PDFs.
- OCR and generated learning material must be reviewed manually.
- Not approved for production, public release, paid distribution, or sensitive documents.
- Tester access should be granted only to specifically approved people.
"@

    Write-TextFile -Path $controlledAccessPath -Content @"
Controlled access note

This share-preparation folder is for specifically approved testers only.

Do not forward the ZIP or link.
Do not post publicly.
Do not upload to GitHub Releases.
Do not use Product Hunt/BetaList/public download links for this artifact.

Access/link creation remains a manual controlled step after this milestone.
"@

    Write-TextFile -Path $noPublicReleasePath -Content @"
NO PUBLIC RELEASE NOTICE

public_release_created=false
github_release_created=false
share_link_created=false
public_upload_performed=false
broadcast_delivery_performed=false
tester_email_sent=false

This milestone only prepares a controlled tester share folder locally.
It does not approve or perform public release.
"@

    Write-TextFile -Path $linkNotCreatedPath -Content @"
SHARE LINK NOT CREATED

share_link_created=false
link_sent_to_testers=false
tester_email_sent=false
public_release_created=false

A separate explicit step is required to create a OneDrive specific-people link or otherwise deliver access to testers.
"@

    Assert-File $testerReadmePath "tester short README"
    Assert-File $knownLimitationsPath "known limitations note"
    Assert-File $controlledAccessPath "controlled access note"
    Assert-File $noPublicReleasePath "no public release notice"
    Assert-File $linkNotCreatedPath "share-link-not-created notice"

    $oneDriveTarget = Join-Path $OneDriveRoot $OneDriveTargetRelativePath
    $oneDriveFolderPrepared = $false
    $oneDriveZipPath = $null
    $oneDriveZipHash = $null

    if ($SkipOneDriveCopy) {
        Write-WarnLine "OneDrive copy skipped by parameter"
    }
    else {
        Write-Step "Prepare OneDrive local controlled share folder"
        Assert-Dir $OneDriveRoot "OneDrive root"

        New-CleanDirectory -Path $oneDriveTarget

        Copy-Item -Path (Join-Path $localShareFolder "*") -Destination $oneDriveTarget -Recurse -Force

        $oneDriveZipPath = Join-Path $oneDriveTarget (Split-Path -Leaf $zipPath)
        Assert-File $oneDriveZipPath "OneDrive target ZIP"
        $oneDriveZipHash = Compare-HashChecked -Source $zipPath -Destination $oneDriveZipPath -Label "OneDrive target ZIP"

        Assert-File (Join-Path $oneDriveTarget (Split-Path -Leaf $shaPath)) "OneDrive target SHA256"
        Assert-File (Join-Path $oneDriveTarget "README-TESTERS-SHORT-v0.7.22.txt") "OneDrive target tester README"
        Assert-File (Join-Path $oneDriveTarget "NO-PUBLIC-RELEASE-NOTICE-v0.7.22.txt") "OneDrive target no public release notice"
        Assert-File (Join-Path $oneDriveTarget "SHARE-LINK-NOT-CREATED-v0.7.22.txt") "OneDrive target share link not created notice"

        $oneDriveFolderPrepared = $true
    }

    Write-Step "Write v0.7.22 manifests"
    $sharePrepManifestPath = Join-Path $SharePrepRoot "CONTROLLED-SHARE-PREPARATION-MANIFEST.json"
    $sharePrepSummaryPath = Join-Path $SharePrepRoot "CONTROLLED-SHARE-PREPARATION-SUMMARY.txt"
    $sharePrepNoPublicReleasePath = Join-Path $SharePrepRoot "NO-PUBLIC-RELEASE-NOTICE.txt"

    $sharePrepManifest = [ordered]@{
        milestone = "v0.7.22-controlled-tester-share-preparation-no-public-release"
        repo_root = $RepoRoot
        git_branch = $branch
        git_head_short = $head
        git_head = $fullHead
        reviewed_release_root = $ReviewedReleaseRoot
        review_root = $ReviewRoot
        share_prep_root = $SharePrepRoot
        local_share_folder = $localShareFolder
        onedrive_root = $OneDriveRoot
        onedrive_target_relative_path = $OneDriveTargetRelativePath
        onedrive_target = $oneDriveTarget
        reviewed_zip_path = $zipPath
        reviewed_zip_sha256 = $hash.Hash
        reviewed_zip_size_bytes = $zipItem.Length
        local_share_zip_path = $targetZip
        local_share_zip_sha256 = $targetZipHash
        onedrive_folder_prepared = [bool]$oneDriveFolderPrepared
        onedrive_zip_path = $oneDriveZipPath
        onedrive_zip_sha256 = $oneDriveZipHash
        one_drive_copy_skipped = [bool]$SkipOneDriveCopy
        public_release_created = $false
        github_release_created = $false
        share_link_created = $false
        tester_email_sent = $false
        public_upload_performed = $false
        broadcast_delivery_performed = $false
        controlled_share_preparation_only = $true
        delivery_approved = $false
        final_marker = $Marker
    }

    $sharePrepManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $sharePrepManifestPath -Encoding UTF8

    $summary = @"
Voila v0.7.22 controlled tester share preparation — no public release

Reviewed ZIP:
$zipPath

SHA256:
$($hash.Hash)

Local share-preparation folder:
$localShareFolder

OneDrive target folder:
$oneDriveTarget

OneDrive folder prepared:
$oneDriveFolderPrepared

Policy:
no_build=true
no_new_zip=true
no_public_release=true
no_github_release=true
share_link_created=false
tester_email_sent=false
public_upload_performed=false
broadcast_delivery_performed=false
controlled_share_preparation_only=true
delivery_approved=false

Interpretation:
The reviewed v0.7.20 ZIP candidate has been copied into a controlled local share-preparation folder.
If OneDrive copy was enabled, the same controlled assets were copied into the local OneDrive folder.

This milestone does NOT create a share link and does NOT send access to testers.
A separate explicit step is required to create a specific-people link or send the access instructions.
"@

    Write-TextFile -Path $sharePrepSummaryPath -Content $summary

    Write-TextFile -Path $sharePrepNoPublicReleasePath -Content @"
NO PUBLIC RELEASE

public_release_created=false
github_release_created=false
share_link_created=false
tester_email_sent=false
public_upload_performed=false
broadcast_delivery_performed=false
delivery_approved=false

Only a controlled tester share-preparation folder was prepared locally.
"@

    Assert-File $sharePrepManifestPath "v0.7.22 share-prep manifest"
    Assert-File $sharePrepSummaryPath "v0.7.22 share-prep summary"
    Assert-File $sharePrepNoPublicReleasePath "v0.7.22 no-public-release notice"

    Write-Step "Final v0.7.22 result"
    Write-Host "controlled_tester_share_preparation_passed=true"
    Write-Host "reviewed_zip_path=$zipPath"
    Write-Host "reviewed_zip_sha256=$($hash.Hash)"
    Write-Host "local_share_folder=$localShareFolder"
    Write-Host "onedrive_folder_prepared=$oneDriveFolderPrepared"
    Write-Host "onedrive_target=$oneDriveTarget"
    Write-Host "onedrive_zip_path=$oneDriveZipPath"
    Write-Host "share_prep_manifest_path=$sharePrepManifestPath"
    Write-Host "share_prep_summary_path=$sharePrepSummaryPath"
    Write-Host "no_build=true"
    Write-Host "no_new_zip=true"
    Write-Host "no_public_release=true"
    Write-Host "no_github_release=true"
    Write-Host "share_link_created=false"
    Write-Host "tester_email_sent=false"
    Write-Host "public_upload_performed=false"
    Write-Host "broadcast_delivery_performed=false"
    Write-Host "controlled_share_preparation_only=true"
    Write-Host "delivery_approved=false"
    Write-Host "NO_PUBLIC_RELEASE=PASS"
    Write-Host "NO_SHARE_LINK_CREATED=PASS"
    Write-Host $Marker
}
finally {
    Pop-Location
}

