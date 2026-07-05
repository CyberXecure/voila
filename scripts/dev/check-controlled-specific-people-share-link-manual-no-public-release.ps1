# v0.7.23 controlled specific-people share link manual, no public release
# Prepares manual OneDrive "Specific people" share-link checklist/evidence only.
# Policy: no public release, no GitHub release, no automated link creation, no public/anyone link.
# Expected marker:
# VOILA_V0_7_23_CONTROLLED_SPECIFIC_PEOPLE_SHARE_LINK_MANUAL_NO_PUBLIC_RELEASE_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$SharePrepRoot = "D:\dev\release-assets\voila\v0.7.22-controlled-tester-share-preparation-no-public-release",
    [string]$ManualShareRoot = "D:\dev\release-assets\voila\v0.7.23-controlled-specific-people-share-link-manual-no-public-release",
    [string]$OneDriveRoot = "$env:USERPROFILE\OneDrive",
    [string]$OneDriveTargetRelativePath = "CX Trading Lab\Voila\v0.7.22-controlled-tester-share-preparation-no-public-release",
    [string]$PackageName = "voila-v0.7.20-controlled-tester-windows-package-candidate",
    [switch]$AllowDirtyWorktree,
    [switch]$ValidateManualEvidence
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_23_CONTROLLED_SPECIFIC_PEOPLE_SHARE_LINK_MANUAL_NO_PUBLIC_RELEASE_CHECK=PASS"

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

function Compare-HashChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Label
    )

    Assert-File $Source "$Label source"
    Assert-File $Destination "$Label destination"

    $sourceHash = Get-FileHash -LiteralPath $Source -Algorithm SHA256
    $destHash = Get-FileHash -LiteralPath $Destination -Algorithm SHA256

    if ($sourceHash.Hash -ne $destHash.Hash) {
        Fail "$Label hash mismatch: source=$($sourceHash.Hash) destination=$($destHash.Hash)"
    }

    Write-Pass "$Label hash verified"
    return $destHash.Hash
}

function Get-KeyValueEvidence {
    param([string]$Path)

    $result = @{}
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $result
    }

    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        $idx = $trimmed.IndexOf("=")
        if ($idx -lt 1) {
            continue
        }
        $key = $trimmed.Substring(0, $idx).Trim()
        $value = $trimmed.Substring($idx + 1).Trim()
        $result[$key] = $value
    }

    return $result
}

function Assert-EvidenceValue {
    param(
        [hashtable]$Evidence,
        [string]$Key,
        [string]$ExpectedValue
    )

    if (-not $Evidence.ContainsKey($Key)) {
        Fail "manual evidence key missing: $Key"
    }

    $actual = "$($Evidence[$Key])"
    if ($actual.ToLowerInvariant() -ne $ExpectedValue.ToLowerInvariant()) {
        Fail "manual evidence $Key expected $ExpectedValue but got $actual"
    }

    Write-Pass "manual evidence $Key=$ExpectedValue"
}

Write-Host "SCRIPT_VERSION=v0.7.23-controlled-specific-people-share-link-manual-no-public-release-1"

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

Write-Step "v0.7.23 policy guard"
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
    Write-Host "NO_AUTOMATED_LINK_CREATION=PASS"
    Write-Host "NO_PUBLIC_ANYONE_LINK=PASS"
    Write-Host "NO_LINK_STORED_IN_REPO=PASS"
    Write-Host "MANUAL_SPECIFIC_PEOPLE_ONLY=PASS"
    Write-Host "PUBLIC_RELEASE_CREATED=false"
    Write-Host "GITHUB_RELEASE_CREATED=false"
    Write-Host "AUTOMATED_SHARE_LINK_CREATED=false"
    Write-Host "PUBLIC_ANYONE_LINK_CREATED=false"
    Write-Host "TESTER_EMAIL_SENT=false"
    Write-Host "BROADCAST_DELIVERY_PERFORMED=false"

    Write-Step "Baseline v0.7.22 files and marker"
    $v022Check = Join-Path $RepoRoot "scripts\dev\check-controlled-tester-share-preparation-no-public-release.ps1"
    $v022Doc = Join-Path $RepoRoot "docs\dev\v0.7.22-controlled-tester-share-preparation-no-public-release.md"
    Assert-File $v022Check "v0.7.22 check script"
    Assert-File $v022Doc "v0.7.22 doc"

    $v022Text = Get-Content -LiteralPath $v022Check -Raw -Encoding UTF8
    if ($v022Text -notmatch "VOILA_V0_7_22_CONTROLLED_TESTER_SHARE_PREPARATION_NO_PUBLIC_RELEASE_CHECK=PASS") {
        Fail "v0.7.22 final marker missing from v0.7.22 script"
    }
    Write-Pass "v0.7.22 marker present in check script"

    Write-Step "Verify v0.7.22 share-preparation outputs"
    Assert-Dir $SharePrepRoot "v0.7.22 share-prep root"

    $sharePrepManifestPath = Join-Path $SharePrepRoot "CONTROLLED-SHARE-PREPARATION-MANIFEST.json"
    $sharePrepSummaryPath = Join-Path $SharePrepRoot "CONTROLLED-SHARE-PREPARATION-SUMMARY.txt"
    $sharePrepNoPublicReleasePath = Join-Path $SharePrepRoot "NO-PUBLIC-RELEASE-NOTICE.txt"

    Assert-File $sharePrepManifestPath "v0.7.22 share-prep manifest"
    Assert-File $sharePrepSummaryPath "v0.7.22 share-prep summary"
    Assert-File $sharePrepNoPublicReleasePath "v0.7.22 no-public-release notice"

    $sharePrepManifest = Load-JsonFile -Path $sharePrepManifestPath -Label "v0.7.22 share-prep manifest"

    Assert-FalseLike $sharePrepManifest.public_release_created "share_prep_manifest.public_release_created"
    Assert-FalseLike $sharePrepManifest.github_release_created "share_prep_manifest.github_release_created"
    Assert-FalseLike $sharePrepManifest.share_link_created "share_prep_manifest.share_link_created"
    Assert-FalseLike $sharePrepManifest.tester_email_sent "share_prep_manifest.tester_email_sent"
    Assert-FalseLike $sharePrepManifest.public_upload_performed "share_prep_manifest.public_upload_performed"
    Assert-FalseLike $sharePrepManifest.broadcast_delivery_performed "share_prep_manifest.broadcast_delivery_performed"
    Assert-FalseLike $sharePrepManifest.delivery_approved "share_prep_manifest.delivery_approved"

    Assert-TextContains -Path $sharePrepSummaryPath -Pattern "share_link_created=false" -Label "v0.7.22 share-prep summary"
    Assert-TextContains -Path $sharePrepNoPublicReleasePath -Pattern "public_release_created=false" -Label "v0.7.22 no-public-release notice"

    Write-Step "Verify OneDrive controlled folder and ZIP"
    $oneDriveTarget = Join-Path $OneDriveRoot $OneDriveTargetRelativePath
    Assert-Dir $OneDriveRoot "OneDrive root"
    Assert-Dir $oneDriveTarget "OneDrive controlled folder"

    $oneDriveZipPath = Join-Path $oneDriveTarget "$PackageName.zip"
    $oneDriveShaPath = "$oneDriveZipPath.sha256"
    $oneDriveReadmePath = Join-Path $oneDriveTarget "README-TESTERS-SHORT-v0.7.22.txt"
    $oneDriveNoPublicReleasePath = Join-Path $oneDriveTarget "NO-PUBLIC-RELEASE-NOTICE-v0.7.22.txt"
    $oneDriveLinkNotCreatedPath = Join-Path $oneDriveTarget "SHARE-LINK-NOT-CREATED-v0.7.22.txt"

    Assert-File $oneDriveZipPath "OneDrive ZIP"
    Assert-File $oneDriveShaPath "OneDrive SHA256"
    Assert-File $oneDriveReadmePath "OneDrive tester README"
    Assert-File $oneDriveNoPublicReleasePath "OneDrive no public release notice"
    Assert-File $oneDriveLinkNotCreatedPath "OneDrive share-link-not-created notice"

    $reviewedZipPath = "$($sharePrepManifest.reviewed_zip_path)"
    $reviewedZipHash = "$($sharePrepManifest.reviewed_zip_sha256)"
    Assert-File $reviewedZipPath "reviewed source ZIP"

    $oneDriveHash = Compare-HashChecked -Source $reviewedZipPath -Destination $oneDriveZipPath -Label "OneDrive ZIP"
    if ($oneDriveHash -ne $reviewedZipHash) {
        Fail "OneDrive ZIP hash mismatch against manifest: $oneDriveHash vs $reviewedZipHash"
    }
    Write-Pass "OneDrive ZIP hash matches v0.7.22 manifest hash"

    $shaText = Get-Content -LiteralPath $oneDriveShaPath -Raw -Encoding ASCII
    if ($shaText -notmatch [regex]::Escape($oneDriveHash)) {
        Fail "OneDrive SHA256 file does not contain ZIP hash"
    }
    Write-Pass "OneDrive SHA256 file contains ZIP hash"

    Write-Step "Create manual specific-people share-link instructions/evidence only"
    New-Item -ItemType Directory -Force -Path $ManualShareRoot | Out-Null

    $manualInstructionsPath = Join-Path $ManualShareRoot "MANUAL-SPECIFIC-PEOPLE-SHARE-STEPS-v0.7.23.txt"
    $manualEvidenceTemplatePath = Join-Path $ManualShareRoot "PRIVATE-MANUAL-SHARE-EVIDENCE-TEMPLATE-v0.7.23.txt"
    $manualEvidencePath = Join-Path $ManualShareRoot "PRIVATE-MANUAL-SHARE-EVIDENCE-v0.7.23.txt"
    $testerMessageTemplatePath = Join-Path $ManualShareRoot "CONTROLLED-TESTER-MESSAGE-TEMPLATE-v0.7.23.txt"
    $noPublicReleaseNoticePath = Join-Path $ManualShareRoot "NO-PUBLIC-RELEASE-NOTICE-v0.7.23.txt"
    $noRepoLinkNoticePath = Join-Path $ManualShareRoot "DO-NOT-COMMIT-SHARE-LINK-v0.7.23.txt"
    $finalManifestPath = Join-Path $ManualShareRoot "CONTROLLED-SPECIFIC-PEOPLE-SHARE-LINK-MANUAL-MANIFEST.json"
    $finalSummaryPath = Join-Path $ManualShareRoot "CONTROLLED-SPECIFIC-PEOPLE-SHARE-LINK-MANUAL-SUMMARY.txt"

    Write-TextFile -Path $manualInstructionsPath -Content @"
Voila v0.7.23 manual OneDrive specific-people share steps

Folder to share:
$oneDriveTarget

ZIP:
$oneDriveZipPath

SHA256:
$oneDriveHash

Manual steps:
1. Open File Explorer.
2. Go to the folder above.
3. Right-click the folder, not only the ZIP.
4. Choose Share.
5. Open Link settings.
6. Choose Specific people.
7. Do NOT choose Anyone with the link.
8. Do NOT choose People in your organization unless all testers are intentionally included.
9. Keep access view-only if OneDrive shows an edit permission toggle.
10. Add only explicitly approved tester email addresses.
11. Create/copy/send the link manually from OneDrive UI.
12. Do not paste the link into Git, docs, PR body, public chat, GitHub release, Product Hunt, BetaList, or website.
13. Record private evidence only in:
$manualEvidencePath

Allowed:
- OneDrive specific-people access only
- approved testers only

Forbidden:
- public link
- anyone-with-link
- GitHub release
- public website upload
- public launch listing download
- broad email blast
"@

    Write-TextFile -Path $manualEvidenceTemplatePath -Content @"
# PRIVATE manual share evidence template for v0.7.23
# Copy this file to PRIVATE-MANUAL-SHARE-EVIDENCE-v0.7.23.txt and edit only after manual OneDrive UI steps.
# Do NOT commit this file.
# Do NOT paste the actual share link into Git, PRs, public docs, or public chat.

specific_people_selected=false
approved_testers_only=false
public_anyone_link_created=false
github_release_created=false
public_release_created=false
public_upload_performed=false
broadcast_delivery_performed=false
share_link_stored_in_repo=false
tester_email_sent=false
manual_share_link_created=false
manual_share_link_sent=false
share_link_location_private_note=not_recorded_here
approved_tester_count=0
manual_operator_initials=
manual_share_datetime_local=
"@

    if (-not (Test-Path -LiteralPath $manualEvidencePath -PathType Leaf)) {
        Copy-Item -LiteralPath $manualEvidenceTemplatePath -Destination $manualEvidencePath -Force
    }

    Write-TextFile -Path $testerMessageTemplatePath -Content @"
Subject: Voila controlled tester access

Hi,

Thank you for helping test Voila.

This is a controlled Windows tester package. Please use only small, non-confidential PDFs.

Please do not upload or test with:
- personal documents
- confidential company files
- legal documents
- medical documents
- financial documents
- safety-critical documents

Basic steps:
1. Download the ZIP from the controlled OneDrive folder.
2. Verify SHA256 if possible:
   $oneDriveHash
3. Extract the ZIP to a local Windows folder.
4. Run START-VOILA.bat.
5. Open http://127.0.0.1:8787/ if it does not open automatically.
6. Test Upload, Generate, Course view, Study, Progress, OCR Review, OCR Math report/viewer, Exam Prep and Quick tools.

Please send feedback on:
- whether start/open was clear
- where anything failed
- confusing screens or wording
- OCR/course quality
- Exam Prep usefulness

Please do not forward the ZIP or share link.
"@

    Write-TextFile -Path $noPublicReleaseNoticePath -Content @"
NO PUBLIC RELEASE NOTICE

public_release_created=false
github_release_created=false
public_upload_performed=false
broadcast_delivery_performed=false
automated_share_link_created=false
public_anyone_link_created=false
share_link_stored_in_repo=false

Only manual OneDrive specific-people sharing is allowed after explicit owner action.
"@

    Write-TextFile -Path $noRepoLinkNoticePath -Content @"
DO NOT COMMIT SHARE LINK

The OneDrive share link, if manually created, must remain private.

Do not store the link in:
- Git
- GitHub PR body
- GitHub release
- public website
- Product Hunt/BetaList pages
- public ChatGPT transcript exports
- docs committed to repo

Only record private non-secret evidence fields locally.
"@

    Assert-File $manualInstructionsPath "manual share instructions"
    Assert-File $manualEvidenceTemplatePath "manual evidence template"
    Assert-File $manualEvidencePath "manual evidence file"
    Assert-File $testerMessageTemplatePath "tester message template"
    Assert-File $noPublicReleaseNoticePath "v0.7.23 no-public-release notice"
    Assert-File $noRepoLinkNoticePath "do-not-commit-share-link notice"

    Assert-TextContains -Path $manualInstructionsPath -Pattern "Specific people" -Label "manual share instructions"
    Assert-TextContains -Path $manualInstructionsPath -Pattern "Do NOT choose Anyone" -Label "manual share instructions"
    Assert-TextContains -Path $noRepoLinkNoticePath -Pattern "Do not store the link in" -Label "do-not-commit-share-link notice"
    Assert-TextContains -Path $testerMessageTemplatePath -Pattern "Please use only small, non-confidential PDFs" -Label "tester message template"

    $manualEvidenceValidated = $false

    if ($ValidateManualEvidence) {
        Write-Step "Validate private manual share evidence"
        $evidence = Get-KeyValueEvidence -Path $manualEvidencePath

        Assert-EvidenceValue -Evidence $evidence -Key "specific_people_selected" -ExpectedValue "true"
        Assert-EvidenceValue -Evidence $evidence -Key "approved_testers_only" -ExpectedValue "true"
        Assert-EvidenceValue -Evidence $evidence -Key "public_anyone_link_created" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "github_release_created" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "public_release_created" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "public_upload_performed" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "broadcast_delivery_performed" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "share_link_stored_in_repo" -ExpectedValue "false"
        Assert-EvidenceValue -Evidence $evidence -Key "manual_share_link_created" -ExpectedValue "true"

        $manualEvidenceValidated = $true
    }
    else {
        Write-WarnLine "manual evidence validation skipped; link is not created by this script"
    }

    Write-Step "Write v0.7.23 manifest and summary"
    $manifest = [ordered]@{
        milestone = "v0.7.23-controlled-specific-people-share-link-manual-no-public-release"
        repo_root = $RepoRoot
        git_branch = $branch
        git_head_short = $head
        git_head = $fullHead
        share_prep_root = $SharePrepRoot
        manual_share_root = $ManualShareRoot
        onedrive_target = $oneDriveTarget
        onedrive_zip_path = $oneDriveZipPath
        onedrive_zip_sha256 = $oneDriveHash
        package_name = $PackageName
        manual_instructions_path = $manualInstructionsPath
        manual_evidence_template_path = $manualEvidenceTemplatePath
        manual_evidence_path = $manualEvidencePath
        tester_message_template_path = $testerMessageTemplatePath
        no_public_release_notice_path = $noPublicReleaseNoticePath
        no_repo_link_notice_path = $noRepoLinkNoticePath
        validate_manual_evidence = [bool]$ValidateManualEvidence
        manual_evidence_validated = [bool]$manualEvidenceValidated
        no_build = $true
        no_new_zip = $true
        no_public_release = $true
        no_github_release = $true
        no_automated_link_creation = $true
        no_public_anyone_link = $true
        no_link_stored_in_repo = $true
        manual_specific_people_only = $true
        public_release_created = $false
        github_release_created = $false
        automated_share_link_created = $false
        public_anyone_link_created = $false
        tester_email_sent_by_script = $false
        broadcast_delivery_performed = $false
        final_marker = $Marker
    }

    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $finalManifestPath -Encoding UTF8

    $summary = @"
Voila v0.7.23 controlled specific-people share-link manual — no public release

OneDrive controlled folder:
$oneDriveTarget

ZIP:
$oneDriveZipPath

SHA256:
$oneDriveHash

Manual instructions:
$manualInstructionsPath

Private evidence file:
$manualEvidencePath

Tester message template:
$testerMessageTemplatePath

Policy:
no_build=true
no_new_zip=true
no_public_release=true
no_github_release=true
no_automated_link_creation=true
no_public_anyone_link=true
no_link_stored_in_repo=true
manual_specific_people_only=true
public_release_created=false
github_release_created=false
automated_share_link_created=false
public_anyone_link_created=false
tester_email_sent_by_script=false
broadcast_delivery_performed=false

Interpretation:
This milestone prepares manual OneDrive specific-people link instructions and private evidence only.
It does not create a share link automatically.
It does not store any link in the repo.
It does not send access to testers.
After owner manually creates a specific-people link, private evidence may be filled locally and validated with -ValidateManualEvidence.
"@

    Write-TextFile -Path $finalSummaryPath -Content $summary

    Assert-File $finalManifestPath "v0.7.23 manual share manifest"
    Assert-File $finalSummaryPath "v0.7.23 manual share summary"

    Write-Step "Final v0.7.23 result"
    Write-Host "controlled_specific_people_share_link_manual_ready=true"
    Write-Host "onedrive_target=$oneDriveTarget"
    Write-Host "onedrive_zip_path=$oneDriveZipPath"
    Write-Host "onedrive_zip_sha256=$oneDriveHash"
    Write-Host "manual_instructions_path=$manualInstructionsPath"
    Write-Host "manual_evidence_path=$manualEvidencePath"
    Write-Host "tester_message_template_path=$testerMessageTemplatePath"
    Write-Host "manual_evidence_validated=$manualEvidenceValidated"
    Write-Host "no_build=true"
    Write-Host "no_new_zip=true"
    Write-Host "no_public_release=true"
    Write-Host "no_github_release=true"
    Write-Host "no_automated_link_creation=true"
    Write-Host "no_public_anyone_link=true"
    Write-Host "no_link_stored_in_repo=true"
    Write-Host "manual_specific_people_only=true"
    Write-Host "public_release_created=false"
    Write-Host "github_release_created=false"
    Write-Host "automated_share_link_created=false"
    Write-Host "public_anyone_link_created=false"
    Write-Host "tester_email_sent_by_script=false"
    Write-Host "broadcast_delivery_performed=false"
    Write-Host "NO_PUBLIC_RELEASE=PASS"
    Write-Host "NO_PUBLIC_ANYONE_LINK=PASS"
    Write-Host "NO_LINK_STORED_IN_REPO=PASS"
    Write-Host $Marker
}
finally {
    Pop-Location
}
