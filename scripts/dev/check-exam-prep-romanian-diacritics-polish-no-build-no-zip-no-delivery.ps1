$ErrorActionPreference = "Stop"

Write-Host "v0.7.79 check: start"

$requiredFiles = @(
  "assets/exam_prep/bac/matematica_m1/skill_tree.json",
  "services/api/exam_prep.py",
  "services/api/web_app.py",
  "services/api/study_quiz_builder.py",
  "docs/dev/exam-prep-romanian-diacritics-polish-no-build-no-zip-no-delivery.md",
  "D:\dev\tester-runs\v0779-exam-prep-romanian-diacritics\V0.7.79-EXAM-PREP-ROMANIAN-DIACRITICS-SMOKE.json"
)

foreach ($p in $requiredFiles) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile services/api/exam_prep.py services/api/web_app.py services/api/study_quiz_builder.py

$skillTree = Get-Content "assets/exam_prep/bac/matematica_m1/skill_tree.json" -Raw
foreach ($item in @(
  "Mulțimi și operații",
  "Mulțimi, operații cu mulțimi și notații de bază.",
  "Ecuații și inecuații",
  "Limite și continuitate",
  "Probabilități și combinatorică"
)) {
  if ($skillTree -notlike "*$item*") { throw "skill_tree missing expected text: $item" }
}

foreach ($bad in @(
  "Multimi si operatii",
  "Ecuatii si inecuatii",
  "Limite si continuitate",
  "Probabilitati si combinatorica",
  "Multimi, operatii",
  "notatii de baza"
)) {
  if ($skillTree -like "*$bad*") { throw "skill_tree still has bad text: $bad" }
}

$examPrep = Get-Content "services/api/exam_prep.py" -Raw
foreach ($item in @(
  "Folosește acțiunea Studiu pentru întrebări legate de acest skill.",
  "Revino în Exam Prep pentru a vedea progresul actualizat din Modul Studiu.",
  "Obiectivul este să ajungi treptat la nivel Consolidat, fără să modificăm motorul BKT existent."
)) {
  if ($examPrep -notlike "*$item*") { throw "exam_prep.py missing expected text: $item" }
}

$studyBuilder = Get-Content "services/api/study_quiz_builder.py" -Raw
foreach ($item in @("mulțime", "mulțimi", "intersecție")) {
  if ($studyBuilder -notlike "*$item*") { throw "study_quiz_builder.py missing expected text: $item" }
}
foreach ($bad in @("mulÈ›ime", "mulÈ›imi", "intersecÈ›ie")) {
  if ($studyBuilder -like "*$bad*") { throw "study_quiz_builder.py still has mojibake: $bad" }
}

$combinedSource = (Get-Content "services/api/exam_prep.py" -Raw) + "`n" + (Get-Content "services/api/web_app.py" -Raw)
foreach ($badMarker in @(
  "VOILA_V0_7_79_EXAM_PREP_WEBAPP_HTML_DIACRITICS_FILTER_START",
  "VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_POLISH_START"
)) {
  if ($combinedSource -like "*$badMarker*") { throw "Experimental wrapper marker still present: $badMarker" }
}

$smokeData = Get-Content "D:\dev\tester-runs\v0779-exam-prep-romanian-diacritics\V0.7.79-EXAM-PREP-ROMANIAN-DIACRITICS-SMOKE.json" -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_BROWSER_TEXT_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content "docs/dev/exam-prep-romanian-diacritics-polish-no-build-no-zip-no-delivery.md" -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_CHECK=PASS",
  "PASS_EXAM_PREP_ROMANIAN_DIACRITICS_POLISH",
  "VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_BROWSER_TEXT_SMOKE=PASS",
  "ROUTES_CHECKED=2",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_EXAM_PREP_DIACRITICS_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "assets/exam_prep/bac/matematica_m1/skill_tree.json",
  "services/api/exam_prep.py",
  "services/api/study_quiz_builder.py",
  "services/api/web_app.py",
  "docs/dev/exam-prep-romanian-diacritics-polish-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-exam-prep-romanian-diacritics-polish-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_CHECK=PASS"
"ROUTES_CHECKED=2"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_EXAM_PREP_DIACRITICS_PASS_NOT_PACKAGED"
"POLICY=exam_prep_romanian_diacritics_polish_no_build_no_zip_no_share_no_delivery_no_distribution"
