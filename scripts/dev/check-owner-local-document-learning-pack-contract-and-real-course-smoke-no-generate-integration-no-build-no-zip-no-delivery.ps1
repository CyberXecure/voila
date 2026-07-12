$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-document-learning-pack-contract-and-real-course-smoke-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0761Module = "services/api/document_concepts.py"
$v0761Doc = "docs/dev/owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery.md"
$courseDir = "data\output\03-pag-30-34-vectori-trigonometrie"
$pagesPath = Join-Path $courseDir "pages.json"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.62-owner-local-document-learning-pack-contract-and-real-course-smoke-no-generate-integration-no-build-no-zip-no-delivery"
$conceptsJson = Join-Path $evidenceRoot "document-concepts-real-course\document_concepts.json"
$candidateLinesJson = Join-Path $evidenceRoot "V0.7.62-REAL-OCR-CANDIDATE-LINES.json"
$inventoryJson = Join-Path $evidenceRoot "V0.7.62-REAL-COURSE-INVENTORY.json"

if (!(Test-Path $doc)) { throw "Missing v0.7.62 doc: $doc" }
if (!(Test-Path $v0761Module)) { throw "Missing v0.7.61 module: $v0761Module" }
if (!(Test-Path $v0761Doc)) { throw "Missing v0.7.61 doc: $v0761Doc" }
if (!(Test-Path $pagesPath)) { throw "Missing real course pages.json: $pagesPath" }
if (!(Test-Path $conceptsJson)) { throw "Missing real course document concepts evidence: $conceptsJson" }
if (!(Test-Path $candidateLinesJson)) { throw "Missing real OCR candidate lines evidence: $candidateLinesJson" }
if (!(Test-Path $inventoryJson)) { throw "Missing real course inventory evidence: $inventoryJson" }

python -m py_compile $v0761Module

$concepts = Get-Content $conceptsJson -Raw | ConvertFrom-Json
if ($concepts.artifact -ne "document_concepts") { throw "Unexpected artifact name in real course smoke" }
if ($concepts.source_language.code -ne "ro") { throw "Expected Romanian language in real course smoke" }
if ($concepts.detected_domain.name -ne "mathematics") { throw "Expected mathematics domain in real course smoke" }
if ([int]$concepts.concept_count -ne 0) { throw "v0.7.62 records current real-course blocker: expected concept_count=0 before extractor improvement" }
if ($concepts.quality.generation_quality_status -ne "LOW_QUALITY_BLOCKED") { throw "Expected LOW_QUALITY_BLOCKED for current real course smoke" }

$candidates = Get-Content $candidateLinesJson -Raw | ConvertFrom-Json
if ($candidates.Count -lt 10) { throw "Expected real OCR candidate learning lines" }

$candidateText = ($candidates | ForEach-Object { $_.text }) -join "`n"
foreach ($item in @("segment orientat", "vector", "direc", "sens", "coordon", "trigonometr")) {
  if ($candidateText -notlike "*$item*") { throw "Missing expected real OCR candidate text fragment: $item" }
}

$inventory = Get-Content $inventoryJson -Raw | ConvertFrom-Json
function Require-Inventory($name, $expectedExists) {
  $row = $inventory | Where-Object { $_.name -eq $name } | Select-Object -First 1
  if ($null -eq $row) { throw "Missing inventory row: $name" }
  if ([bool]$row.exists -ne [bool]$expectedExists) { throw "Unexpected inventory exists for $name" }
}

Require-Inventory "pages.json" $true
Require-Inventory "course_outline.json" $true
Require-Inventory "course.cleaned.html" $true
Require-Inventory "quiz.json" $true
Require-Inventory "flashcards.json" $true
Require-Inventory "glossary.json" $true
Require-Inventory "ocr_report.json" $false
Require-Inventory "ocr_math_report.json" $false
Require-Inventory "ocr_math_report.md" $false

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_62_DOCUMENT_LEARNING_PACK_CONTRACT_AND_REAL_COURSE_SMOKE_CHECK=PASS_BLOCKED",
  "PASS_CONTRACT_WITH_REAL_COURSE_BLOCKER",
  "document_learning_pack.json",
  "document_learning_pack.md",
  "LOW_QUALITY_BLOCKED",
  "ocr_report.json",
  "ocr_math_report.json",
  "ocr_math_report.md",
  "first learn the document and only then teach it",
  "No `/generate` route change.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*document_learning_pack*") {
  throw "v0.7.62 must not integrate document_learning_pack into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-document-learning-pack-contract-and-real-course-smoke-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-document-learning-pack-contract-and-real-course-smoke-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.62: $line"
  }
}

"VOILA_V0_7_62_DOCUMENT_LEARNING_PACK_CONTRACT_AND_REAL_COURSE_SMOKE_CHECK=PASS_BLOCKED"
"REAL_COURSE_LANGUAGE=ro"
"REAL_COURSE_DOMAIN=mathematics"
"REAL_COURSE_DOCUMENT_CONCEPTS=LOW_QUALITY_BLOCKED"
"REAL_OCR_CANDIDATE_LINES=PASS"
"OCR_REPORT_PRESENT=False"
"OCR_MATH_REPORT_PRESENT=False"
"DOCUMENT_LEARNING_PACK_CONTRACT=DEFINED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=contract_and_real_course_smoke_only_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
