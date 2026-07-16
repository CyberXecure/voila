$ErrorActionPreference = "Stop"

Write-Host "v0.7.80 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/study-ux-progress-consistency-audit-no-build-no-zip-no-delivery.md"
$audit = "D:\dev\tester-runs\v0780-study-ux-progress-audit\V0.7.80-STUDY-UX-PROGRESS-AUDIT.json"
$smoke = "D:\dev\tester-runs\v0780-study-ux-progress-audit\V0.7.80-STUDY-UX-PROGRESS-CONSISTENCY-SMOKE.json"

foreach ($p in @($web, $doc, $audit, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw

foreach ($item in @(
  "VOILA_V0_7_80_STUDY_UX_REASON_LABEL_START",
  "_voila_v080_study_recommendation_reason_label",
  '"concept nou": "Concept nou"',
  '"legacy short answer": "răspuns scurt"',
  "padding-bottom: 168px !important",
  'study.concept_mastery_changed',
  "Nivelul conceptului s-a schimbat de la",
  'study.current_overall_mastery',
  "Nivel general curent"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected v0.7.80 text: $item" }
}

foreach ($bad in @(
  "padding-bottom: 104px !important",
  '{_ut("mastery_changed", "Mastery changed from")} <strong>{before}%</strong>',
  '{_ut("status.overall_mastery", _ut("overall_mastery", "Overall mastery"))}: <strong>{view.get("overall_mastery_percent")}%</strong>'
)) {
  if ($webText -like "*$bad*") { throw "web_app.py still has old Study UX text: $bad" }
}

$auditData = Get-Content $audit -Raw | ConvertFrom-Json
if ($auditData.VOILA_V0_7_80_STUDY_UX_PROGRESS_AUDIT -ne "PASS_WITH_FINDINGS") { throw "Audit marker mismatch" }
if ($auditData.BUILD_PERFORMED -ne $false) { throw "Audit BUILD_PERFORMED mismatch" }
if ($auditData.ZIP_CREATED -ne $false) { throw "Audit ZIP_CREATED mismatch" }
if ($auditData.SHARE_CREATED -ne $false) { throw "Audit SHARE_CREATED mismatch" }
if ($auditData.DELIVERY_PERFORMED -ne $false) { throw "Audit DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_80_STUDY_UX_PROGRESS_CONSISTENCY_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.legacy_short_answer_hidden -ne $true) { throw "legacy_short_answer_hidden mismatch" }
if ($smokeData.reason_label_polished -ne $true) { throw "reason_label_polished mismatch" }
if ($smokeData.current_overall_label_visible -ne $true) { throw "current_overall_label_visible mismatch" }
if ($smokeData.concept_level_delta_label_visible -ne $true) { throw "concept_level_delta_label_visible mismatch" }
if ($smokeData.bottom_nav_padding_px -ne 168) { throw "bottom_nav_padding_px mismatch" }
if ($smokeData.question_generation_changed -ne $false) { throw "question_generation_changed mismatch" }
if ($smokeData.bkt_logic_changed -ne $false) { throw "bkt_logic_changed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_80_STUDY_UX_PROGRESS_CONSISTENCY_CHECK=PASS",
  "PASS_STUDY_UX_PROGRESS_CONSISTENCY",
  "VOILA_V0_7_80_STUDY_UX_PROGRESS_AUDIT=PASS_WITH_FINDINGS",
  "VOILA_V0_7_80_STUDY_UX_PROGRESS_CONSISTENCY_SMOKE=PASS",
  "legacy_short_answer_hidden=True",
  "reason_label_polished=True",
  "current_overall_label_visible=True",
  "concept_level_delta_label_visible=True",
  "bottom_nav_padding_px=168",
  "question_generation_changed=False",
  "bkt_logic_changed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_STUDY_UX_PROGRESS_CONSISTENCY_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/study-ux-progress-consistency-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-study-ux-progress-consistency-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_80_STUDY_UX_PROGRESS_CONSISTENCY_CHECK=PASS"
"LEGACY_SHORT_ANSWER_HIDDEN=True"
"REASON_LABEL_POLISHED=True"
"CURRENT_OVERALL_LABEL_VISIBLE=True"
"CONCEPT_LEVEL_DELTA_LABEL_VISIBLE=True"
"BOTTOM_NAV_PADDING_PX=168"
"QUESTION_GENERATION_CHANGED=False"
"BKT_LOGIC_CHANGED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_STUDY_UX_PROGRESS_CONSISTENCY_PASS_NOT_PACKAGED"
"POLICY=study_ux_progress_consistency_no_build_no_zip_no_share_no_delivery_no_distribution"
