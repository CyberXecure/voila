param(
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\dev\projects\voila"
$PackageRoot = "D:\dev\tester-runs\v0839\x\voila-v0.8.38-controlled-tester-windows-package-candidate"
$CourseId = "03-pag-30-34-vectori-trigonometrie"
$PdfName = "$CourseId.pdf"
$OutDir = "D:\dev\tester-runs\v0841-owner-personal-manual-study-workflow-smoke-no-share-no-delivery"
$OutJson = Join-Path $OutDir "V0.8.41-OWNER-PERSONAL-MANUAL-STUDY-WORKFLOW-SMOKE.json"
$OutMd = Join-Path $OutDir "V0.8.41-OWNER-PERSONAL-MANUAL-STUDY-WORKFLOW-SMOKE.md"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

if (-not (Test-Path -LiteralPath $PackageRoot)) {
    throw "Nu gasesc pachetul extras validat v0.8.39: $PackageRoot"
}

$StartScript = Join-Path $PackageRoot "scripts\dev\start-voila-packaged.ps1"
$StopScript = Join-Path $PackageRoot "scripts\dev\stop-voila.ps1"

if (-not (Test-Path -LiteralPath $StartScript)) {
    throw "Nu gasesc start-voila-packaged.ps1 in pachetul extras: $StartScript"
}

if (-not $NoStart) {
    Write-Output "Oprire instanțe existente..."
    & (Join-Path $RepoRoot "scripts\dev\stop-voila.ps1")

    Write-Output "Pornire pachet extras validat..."
    Push-Location $PackageRoot
    try {
        & $StartScript -Silent -NoBrowser
    } finally {
        Pop-Location
    }
}

$HealthOk = $false
for ($i = 1; $i -le 40; $i++) {
    try {
        $health = Invoke-WebRequest "http://127.0.0.1:8787/health" -UseBasicParsing -TimeoutSec 5
        if ($health.StatusCode -eq 200) {
            $HealthOk = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $HealthOk) {
    throw "Voila nu raspunde la /health pe 127.0.0.1:8787"
}

$HomeUrl = "http://127.0.0.1:8787/"
$CourseToolsUrl = "http://127.0.0.1:8787/course-tools?pdf=$PdfName"
$StudyUrl = "http://127.0.0.1:8787/study?pdf=$PdfName"
$ShadowUrl = "http://127.0.0.1:8787/study?manual_study_shadow=1&course_id=$CourseId"
$DryRunUrl = "http://127.0.0.1:8787/owner/manual-study-integration-dry-run/$CourseId" + "?enabled=0"

Write-Output ""
Write-Output "Deschid workflow-ul principal in browser..."
Start-Process $HomeUrl | Out-Null
Start-Sleep -Seconds 1
Start-Process $CourseToolsUrl | Out-Null
Start-Sleep -Seconds 1
Start-Process $StudyUrl | Out-Null

Write-Output ""
Write-Output "URL-uri utile pentru testul tau personal:"
Write-Output "HOME=$HomeUrl"
Write-Output "COURSE_TOOLS=$CourseToolsUrl"
Write-Output "STUDY_NORMAL=$StudyUrl"
Write-Output "STUDY_SHADOW=$ShadowUrl"
Write-Output "DRY_RUN=$DryRunUrl"

try {
    $courseTools = Invoke-WebRequest $CourseToolsUrl -UseBasicParsing -TimeoutSec 20
    $links = [regex]::Matches($courseTools.Content, 'href="([^"]+)"') |
        ForEach-Object { $_.Groups[1].Value.Replace("&amp;", "&") } |
        Where-Object { $_ -match "study|manual|learning|evidence|dry-run|course-tools" } |
        Sort-Object -Unique

    Write-Output ""
    Write-Output "Link-uri relevante detectate in Course Tools:"
    foreach ($link in $links) {
        Write-Output " - $link"
    }
} catch {
    Write-Output "Nu am putut lista link-urile din Course Tools: $($_.Exception.Message)"
}

Write-Output ""
Write-Output "Acum testeaza manual in browser."
Write-Output "Raspunde cu da/nu. Nu incerca sa fii politicos: daca e neclar, scrie nu."
Write-Output ""

function Ask-YesNo {
    param([string]$Question)

    while ($true) {
        $answer = Read-Host $Question
        $normalized = $answer.Trim().ToLowerInvariant()
        if ($normalized -in @("da", "d", "yes", "y")) { return $true }
        if ($normalized -in @("nu", "n", "no")) { return $false }
        Write-Output "Te rog raspunde cu da sau nu."
    }
}

$HomeClear = Ask-YesNo "1. Din Home iti este clar ce document testezi?"
$CourseToolsClear = Ask-YesNo "2. Din Home/Course Tools iti este clar unde intri pentru acest document?"
$ManualEvidenceFound = Ask-YesNo "3. Ai gasit sau ai inteles zona Manual Learning Evidence / evidence workflow?"
$EvidenceConceptClear = Ask-YesNo "4. Iti este clar ca Manual Study se bazeaza pe bucati verificate de tine, nu pe OCR brut?"
$ExportClear = Ask-YesNo "5. Iti este clar ca trebuie exportat Learning Pack / Manual Study Items preview inainte de Study final?"
$StudyWorks = Ask-YesNo "6. Study normal afiseaza Manual Study default?"
$CardsVisible = Ask-YesNo "7. Cardurile Manual Study sunt vizibile si utile?"
$ReadOnlyOk = Ask-YesNo "8. Raspunsurile sunt read-only / in details, nu par editabile accidental?"
$SourceVisible = Ask-YesNo "9. Source metadata este vizibil?"
$TesterReadyFeeling = Ask-YesNo "10. Ai trimite acest workflow unui tester fara explicatii suplimentare?"

$BiggestBlocker = Read-Host "Care este cel mai mare blocaj/neclaritate observata?"
$OwnerNotes = Read-Host "Observatii scurte pentru urmatorul milestone"

$CoreTechnicalOk = $StudyWorks -and $CardsVisible -and $ReadOnlyOk -and $SourceVisible
$WorkflowClear = $HomeClear -and $CourseToolsClear -and $ManualEvidenceFound -and $EvidenceConceptClear -and $ExportClear -and $TesterReadyFeeling

if ($CoreTechnicalOk -and $WorkflowClear) {
    $Result = "PASS_OWNER_PERSONAL_CLEAR"
} elseif ($CoreTechnicalOk) {
    $Result = "NEEDS_UX_POLISH"
} else {
    $Result = "BLOCKED"
}

$Evidence = [ordered]@{
    VOILA_V0_8_41_OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE_RECORDED = "PASS"
    owner_personal_workflow_result = $Result
    tested_package_root = $PackageRoot
    course_id = $CourseId
    pdf_name = $PdfName
    health_ok = $HealthOk
    home_url = $HomeUrl
    course_tools_url = $CourseToolsUrl
    study_normal_url = $StudyUrl
    shadow_url = $ShadowUrl
    dry_run_url = $DryRunUrl
    home_clear = $HomeClear
    course_tools_clear = $CourseToolsClear
    manual_learning_evidence_found_or_understood = $ManualEvidenceFound
    evidence_concept_clear = $EvidenceConceptClear
    export_learning_pack_or_manual_study_items_clear = $ExportClear
    study_normal_renders_manual_default = $StudyWorks
    manual_study_cards_visible_and_useful = $CardsVisible
    answer_details_remain_read_only = $ReadOnlyOk
    source_metadata_visible = $SourceVisible
    tester_ready_without_extra_explanation = $TesterReadyFeeling
    biggest_blocker_or_unclear_step = $BiggestBlocker
    owner_notes = $OwnerNotes
    package_rebuild_performed = $false
    new_zip_created = $false
    onedrive_copy_created = $false
    share_created = $false
    delivery_performed = $false
    distribution_performed = $false
    public_release_created = $false
    POLICY = "owner_personal_manual_study_workflow_smoke_no_share_no_delivery"
    RECOMMENDED_NEXT = $(if ($Result -eq "PASS_OWNER_PERSONAL_CLEAR") { "separate_owner_decision_before_any_share_or_delivery" } elseif ($Result -eq "NEEDS_UX_POLISH") { "v0.8.42-owner-local-manual-study-workflow-ux-polish-no-share-no-delivery" } else { "v0.8.42-owner-local-manual-study-workflow-blocker-fix-no-share-no-delivery" })
}

$Evidence | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $OutJson

$md = @()
$md += "# v0.8.41 Owner personal Manual Study workflow smoke"
$md += ""
$md += "## Result"
$md += ""
$md += "- VOILA_V0_8_41_OWNER_PERSONAL_MANUAL_STUDY_WORKFLOW_SMOKE_RECORDED: PASS"
$md += "- owner_personal_workflow_result: $Result"
$md += ""
$md += "## Answers"
foreach ($key in $Evidence.Keys) {
    $md += "- ${key}: $($Evidence[$key])"
}
$md | Set-Content -Encoding UTF8 $OutMd

Write-Output ""
foreach ($key in $Evidence.Keys) {
    Write-Output "$key=$($Evidence[$key])"
}
Write-Output "EVIDENCE_JSON=$OutJson"
Write-Output "EVIDENCE_MD=$OutMd"
