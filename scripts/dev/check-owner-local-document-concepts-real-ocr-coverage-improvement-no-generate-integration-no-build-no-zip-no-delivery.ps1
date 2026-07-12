$ErrorActionPreference = "Stop"

$module = "services/api/document_concepts.py"
$doc = "docs/dev/owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0762Doc = "docs/dev/owner-local-document-learning-pack-contract-and-real-course-smoke-no-generate-integration-no-build-no-zip-no-delivery.md"
$coursePages = "data\output\03-pag-30-34-vectori-trigonometrie\pages.json"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.63-owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery"
$baselineJson = Join-Path $evidenceRoot "baseline-before-patch\document_concepts.json"
$smallJson = Join-Path $evidenceRoot "output-small-after-fix\document_concepts.json"
$realJson = Join-Path $evidenceRoot "real-course-after-fix\document_concepts.json"

if (!(Test-Path $module)) { throw "Missing module: $module" }
if (!(Test-Path $doc)) { throw "Missing v0.7.63 doc: $doc" }
if (!(Test-Path $v0762Doc)) { throw "Missing v0.7.62 baseline doc: $v0762Doc" }
if (!(Test-Path $coursePages)) { throw "Missing real course pages.json: $coursePages" }
if (!(Test-Path $baselineJson)) { throw "Missing v0.7.63 baseline evidence: $baselineJson" }
if (!(Test-Path $smallJson)) { throw "Missing v0.7.63 small fixture evidence: $smallJson" }
if (!(Test-Path $realJson)) { throw "Missing v0.7.63 real course evidence: $realJson" }

python -m py_compile $module

$baseline = Get-Content $baselineJson -Raw | ConvertFrom-Json
if ([int]$baseline.concept_count -ne 0) { throw "Expected baseline concept_count=0 before patch" }
if ($baseline.quality.generation_quality_status -ne "LOW_QUALITY_BLOCKED") { throw "Expected baseline LOW_QUALITY_BLOCKED before patch" }

$small = Get-Content $smallJson -Raw | ConvertFrom-Json
if ([int]$small.concept_count -lt 3) { throw "Expected small fixture concept_count >= 3 after patch" }
if ($small.quality.generation_quality_status -ne "PASS") { throw "Expected small fixture PASS after patch" }

$smallTerms = (($small.concepts | ForEach-Object { $_.term }) -join "`n").ToLowerInvariant()
foreach ($term in @("vector", "segment orientat", "modul")) {
  if ($smallTerms -notlike "*$term*") { throw "Missing small fixture term: $term" }
}

$real = Get-Content $realJson -Raw | ConvertFrom-Json
if ($real.source_language.code -ne "ro") { throw "Expected real course language ro" }
if ($real.detected_domain.name -ne "mathematics") { throw "Expected real course domain mathematics" }
if ([int]$real.concept_count -lt 10) { throw "Expected real course concept_count >= 10 after patch" }
if ($real.quality.generation_quality_status -ne "PASS") { throw "Expected real course PASS after patch" }

$realTerms = (($real.concepts | ForEach-Object { $_.term }) -join "`n").ToLowerInvariant()
foreach ($term in @(
  "segment orientat",
  "vector",
  "modul",
  "direcție",
  "vectori egali",
  "vectori opuși",
  "vectori coliniari",
  "vectori necoliniari",
  "bază",
  "coordonatele vectorului",
  "versorii axelor de coordonate",
  "bază ortonormată",
  "produsul scalar",
  "funcții trigonometrice"
)) {
  if ($realTerms -notlike "*$term*") { throw "Missing real course term after patch: $term" }
}

if ($realTerms -like "*vectori coliniari dacă*") {
  throw "Real course term cleanup failed for vectori coliniari"
}

$moduleText = Get-Content $module -Raw
foreach ($item in @(
  "normalize_legacy_ro",
  "split_candidate_units",
  "extract_definition_markers",
  "extract_characteristics",
  "extract_named_notation",
  "romanian_definition_se_numeste",
  "romanian_definition_se_numesc",
  "romanian_vector_relation_daca",
  "romanian_named_formula_scalar_product",
  "romanian_named_section_trigonometric_functions"
)) {
  if ($moduleText -notlike "*$item*") { throw "Module missing expected v0.7.63 extraction marker: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_63_DOCUMENT_CONCEPTS_REAL_OCR_COVERAGE_IMPROVEMENT_CHECK=PASS",
  "PASS_REAL_OCR_COVERAGE_IMPROVED",
  "concept_count=14",
  "quality_status=PASS",
  "User-friendly OCR Review requirement",
  "show only suspect lines/formulas",
  "allow simple actions: accept, edit, ignore",
  "continue course generation only after the quality gate passes",
  "No /generate route change.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.63 text: $item" }
}

$webAppText = Get-Content "services/api/web_app.py" -Raw
if ($webAppText -like "*document_learning_pack*" -or $webAppText -like "*document_concepts.py*") {
  throw "v0.7.63 must not integrate document concepts/learning pack into web_app.py"
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/document_concepts.py",
  "docs/dev/owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-document-concepts-real-ocr-coverage-improvement-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.63: $line"
  }
}

"VOILA_V0_7_63_DOCUMENT_CONCEPTS_REAL_OCR_COVERAGE_IMPROVEMENT_CHECK=PASS"
"BASELINE_BEFORE_PATCH=LOW_QUALITY_BLOCKED"
"SMALL_FIXTURE_CONCEPTS=PASS"
"REAL_COURSE_LANGUAGE=ro"
"REAL_COURSE_DOMAIN=mathematics"
"REAL_COURSE_CONCEPT_COUNT=14"
"REAL_COURSE_DOCUMENT_CONCEPTS=PASS"
"OCR_REVIEW_REQUIREMENT=USER_FRIENDLY_GUIDED_REVIEW_REQUIRED_WHEN_BLOCKED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"LESSONS_QUIZ_FLASHCARDS_GLOSSARY=NOT_CHANGED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_document_concepts_only_no_generate_integration_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
