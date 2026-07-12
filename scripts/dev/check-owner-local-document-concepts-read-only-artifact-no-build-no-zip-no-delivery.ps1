$ErrorActionPreference = "Stop"

$module = "services/api/document_concepts.py"
$doc = "docs/dev/owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery.md"
$v0760Doc = "docs/dev/owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.61-owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery"
$outDir = Join-Path $evidenceRoot "output-small"
$jsonPath = Join-Path $outDir "document_concepts.json"
$mdPath = Join-Path $outDir "document_concepts.md"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }
if (!(Test-Path $v0760Doc)) { throw "Missing v0.7.60 baseline doc: $v0760Doc" }

python -m py_compile $module

if (!(Test-Path $jsonPath)) { throw "Missing evidence document_concepts.json: $jsonPath" }
if (!(Test-Path $mdPath)) { throw "Missing evidence document_concepts.md: $mdPath" }

$concepts = Get-Content $jsonPath -Raw | ConvertFrom-Json

if ($concepts.artifact -ne "document_concepts") { throw "Unexpected artifact name" }
if ($concepts.source_language.code -ne "ro") { throw "Expected Romanian language detection" }
if ($concepts.detected_domain.name -ne "mathematics") { throw "Expected mathematics domain detection" }
if ([int]$concepts.concept_count -lt 3) { throw "Expected at least 3 extracted concepts" }
if ($concepts.quality.generation_quality_status -ne "PASS") { throw "Expected PASS quality for controlled fixture" }
if ($concepts.quality.static_technical_terms_primary_source -ne $false) { throw "Static technical terms must not be primary source" }
if ($concepts.policy.no_lesson_generation -ne $true) { throw "Expected no lesson generation policy" }
if ($concepts.policy.no_quiz_generation -ne $true) { throw "Expected no quiz generation policy" }
if ($concepts.policy.no_flashcard_generation -ne $true) { throw "Expected no flashcard generation policy" }
if ($concepts.policy.no_glossary_generation -ne $true) { throw "Expected no glossary generation policy" }

$termsText = (($concepts.concepts | ForEach-Object { $_.term }) -join "`n").ToLowerInvariant()
foreach ($term in @("vector", "segment orientat", "modul")) {
  if ($termsText -notlike "*$term*") {
    throw "Expected extracted concept term: $term"
  }
}

$moduleText = Get-Content $module -Raw
foreach ($item in @("def build_document_concepts", "def write_document_concepts", "document_concepts.json", "document_concepts.md", "generation_quality_status", "LOW_QUALITY_BLOCKED", "static_technical_terms_primary_source")) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*document_concepts.py*") {
  throw "v0.7.61 must not integrate document_concepts.py into web_app.py"
}

$docText = Get-Content $doc -Raw
foreach ($item in @("VOILA_V0_7_61_DOCUMENT_CONCEPTS_READ_ONLY_ARTIFACT_CHECK=PASS", "IMPLEMENTED_LOCAL_ARTIFACT / NOT_INTEGRATED_IN_GENERATE", "document_concepts.json", "document_concepts.md", "No build.", "No ZIP.", "No share.", "No delivery.", "No distribution.", "Tester readiness remains BLOCKED")) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected v0.7.61 text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/document_concepts.py",
  "docs/dev/owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-document-concepts-read-only-artifact-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.61: $line"
  }
}

"VOILA_V0_7_61_DOCUMENT_CONCEPTS_READ_ONLY_ARTIFACT_CHECK=PASS"
"DOCUMENT_CONCEPTS_ARTIFACT=PASS"
"DOCUMENT_CONCEPTS_LANGUAGE=ro"
"DOCUMENT_CONCEPTS_DOMAIN=mathematics"
"DOCUMENT_CONCEPTS_MIN_COUNT=PASS"
"GENERATE_INTEGRATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_artifact_only_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
