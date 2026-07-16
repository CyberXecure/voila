$ErrorActionPreference = "Stop"

Write-Host "v0.7.77 check: start"

$web = "services/api/web_app.py"
$generator = "services/api/course_generator.py"
$polisher = "services/api/course_polisher.py"
$doc = "docs/dev/owner-local-generate-integration-from-readiness-gated-learning-pack-and-browser-smoke-no-build-no-zip-no-delivery.md"

$outDir = "D:\dev\projects\voila\data\output\03-pag-30-34-vectori-trigonometrie"
$integrationReport = Join-Path $outDir "generate_integration_report.json"
$courseMd = Join-Path $outDir "course.md"
$cleanMd = Join-Path $outDir "course.cleaned.md"
$cleanHtml = Join-Path $outDir "course.cleaned.html"
$glossaryJson = Join-Path $outDir "glossary.json"
$quizJson = Join-Path $outDir "quiz.json"
$flashcardsJson = Join-Path $outDir "flashcards.json"

$realSmoke = "D:\dev\tester-runs\v0777-real-generate-integration-smoke\V0.7.77-REAL-GENERATE-INTEGRATION-SMOKE.json"
$browserSmoke = "D:\dev\tester-runs\v0777-browser-smoke\V0.7.77-BROWSER-SMOKE.json"

foreach ($p in @($web,$generator,$polisher,$doc,$integrationReport,$courseMd,$cleanMd,$cleanHtml,$glossaryJson,$quizJson,$flashcardsJson,$realSmoke,$browserSmoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web $generator $polisher

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_77_OWNER_LOCAL_GENERATE_INTEGRATION_FROM_READINESS_GATED_LEARNING_PACK_START",
  "_voila_v0777_ready_learning_pack_for_generate",
  "_voila_v0777_write_generate_integration_report",
  "learning_pack_path = _voila_v0777_ready_learning_pack_for_generate(output_dir)",
  "--learning-pack-json",
  "stale_course_html.unlink()",
  "owner_local_generate_integration_from_readiness_gated_learning_pack"
)) {
  if ($webText -notlike "*$item*") { throw "web_app missing expected text: $item" }
}

$generatorText = Get-Content $generator -Raw
foreach ($item in @(
  "VOILA_V0_7_77_COURSE_GENERATOR_LEARNING_PACK_INTEGRATION_START",
  "load_learning_pack",
  "append_learning_pack_assets",
  "write_learning_pack_course_section",
  "v0.7.77_learning_pack_verified_evidence",
  "document_learning_pack.json",
  "ocr_review_decisions.applied.json",
  "--learning-pack-json",
  "Document learning pack integration"
)) {
  if ($generatorText -notlike "*$item*") { throw "course_generator missing expected text: $item" }
}

$polisherText = Get-Content $polisher -Raw
foreach ($item in @(
  "VOILA_V0_7_77_COURSE_POLISHER_LEARNING_PACK_INTEGRATION_START",
  "load_learning_pack",
  "append_learning_pack_clean_course_section",
  "Learning pack verificat",
  "v0.7.77 readiness-gated learning pack",
  "--learning-pack-json"
)) {
  if ($polisherText -notlike "*$item*") { throw "course_polisher missing expected text: $item" }
}

$report = Get-Content $integrationReport -Raw | ConvertFrom-Json
if ($report.artifact -ne "owner_local_generate_integration_from_readiness_gated_learning_pack") { throw "integration report artifact mismatch" }
if ($report.artifact_version -ne "v0.7.77") { throw "integration report version mismatch" }
if ($report.learning_pack_used -ne $true) { throw "learning_pack_used mismatch" }
if ($report.generate_integration_changed -ne $true) { throw "generate_integration_changed mismatch" }
if ($report.generator_route_changed -ne $true) { throw "generator_route_changed mismatch" }
if ($report.course_regeneration_performed -ne $true) { throw "course_regeneration_performed mismatch" }
if ($report.build_performed -ne $false) { throw "build_performed mismatch" }
if ($report.zip_created -ne $false) { throw "zip_created mismatch" }
if ($report.share_created -ne $false) { throw "share_created mismatch" }
if ($report.delivery_performed -ne $false) { throw "delivery_performed mismatch" }

$glossary = Get-Content $glossaryJson -Raw | ConvertFrom-Json
$quiz = Get-Content $quizJson -Raw | ConvertFrom-Json
$flashcards = Get-Content $flashcardsJson -Raw | ConvertFrom-Json

function Count-LearningPackItems($items) {
  $count = 0
  foreach ($item in $items) {
    if ($item.generation_method -eq "v0.7.77_learning_pack_verified_evidence") { $count++ }
  }
  return $count
}

$glossaryLp = Count-LearningPackItems $glossary
$quizLp = Count-LearningPackItems $quiz
$flashcardsLp = Count-LearningPackItems $flashcards

if ($glossaryLp -lt 14) { throw "learning pack glossary item count too low: $glossaryLp" }
if ($quizLp -lt 34) { throw "learning pack quiz item count too low: $quizLp" }
if ($flashcardsLp -lt 14) { throw "learning pack flashcard item count too low: $flashcardsLp" }

$courseText = Get-Content $courseMd -Raw
$cleanText = Get-Content $cleanMd -Raw
$htmlText = Get-Content $cleanHtml -Raw

if ($courseText -notlike "*v0.7.77 readiness-gated learning pack*") { throw "course.md missing learning pack section" }
if ($cleanText -notlike "*Learning pack verificat*") { throw "course.cleaned.md missing learning pack section" }
if ($htmlText -notlike "*Learning pack verificat*") { throw "course.cleaned.html missing learning pack section" }

$real = Get-Content $realSmoke -Raw | ConvertFrom-Json
if ($real.VOILA_V0_7_77_REAL_GENERATE_INTEGRATION_SMOKE -ne "PASS") { throw "real smoke marker mismatch" }
if ($real.VOILA_V0_7_77_HTML_REBUILT_FROM_LEARNING_PACK_MARKDOWN -ne "PASS") { throw "html rebuild marker mismatch" }
if ($real.LEARNING_PACK_VISIBLE_IN_HTML -ne $true) { throw "real smoke html visibility mismatch" }
if ($real.GENERATE_INTEGRATION -ne "CHANGED_AND_USED") { throw "real smoke generate integration mismatch" }

$browser = Get-Content $browserSmoke -Raw | ConvertFrom-Json
if (($browser | Measure-Object).Count -ne 13) { throw "browser route count mismatch" }
foreach ($route in $browser) {
  if ($route.pass -ne $true) { throw "browser route failed in evidence: $($route.name)" }
}

$docText = (Get-Content $doc -Raw).Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_77_GENERATE_INTEGRATION_AND_BROWSER_SMOKE_CHECK=PASS",
  "PASS_REAL_GENERATE_INTEGRATION_AND_BROWSER_SMOKE",
  "VOILA_V0_7_77_REAL_GENERATE_INTEGRATION_SMOKE=PASS",
  "VOILA_V0_7_77_HTML_REBUILT_FROM_LEARNING_PACK_MARKDOWN=PASS",
  "VOILA_V0_7_77_BROWSER_SMOKE=PASS",
  "ROUTES_CHECKED=13",
  "GENERATE_INTEGRATION=CHANGED_AND_USED",
  "LEARNING_PACK_VISIBLE_IN_COURSE=True",
  "JSON_ARTIFACTS_USE_LEARNING_PACK=True",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_BROWSER_SMOKE_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "services/api/course_generator.py",
  "services/api/course_polisher.py",
  "docs/dev/owner-local-generate-integration-from-readiness-gated-learning-pack-and-browser-smoke-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-generate-integration-from-readiness-gated-learning-pack-and-browser-smoke-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_77_GENERATE_INTEGRATION_AND_BROWSER_SMOKE_CHECK=PASS"
"REAL_GENERATE_INTEGRATION=PASS"
"HTML_REBUILT_FROM_LEARNING_PACK_MARKDOWN=PASS"
"BROWSER_SMOKE=PASS"
"ROUTES_CHECKED=13"
"LEARNING_PACK_USED=True"
"LEARNING_PACK_VISIBLE_IN_COURSE=True"
"JSON_ARTIFACTS_USE_LEARNING_PACK=True"
"LEARNING_PACK_GLOSSARY_ITEMS=$glossaryLp"
"LEARNING_PACK_QUIZ_ITEMS=$quizLp"
"LEARNING_PACK_FLASHCARD_ITEMS=$flashcardsLp"
"GENERATE_INTEGRATION=CHANGED_AND_USED"
"GENERATOR_ROUTE_CHANGED=True"
"COURSE_REGENERATION=True"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_BROWSER_SMOKE_PASS_NOT_PACKAGED"
"POLICY=owner_local_generate_integration_from_readiness_gated_learning_pack_and_browser_smoke_no_build_no_zip_no_share_no_delivery_no_distribution"
