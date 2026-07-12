$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery.md"
$evidenceRoot = "D:\dev\tester-runs\voila-v0.7.59-owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery"

$requiredEvidence = @(
  "V0.7.59-REPO-BASELINE.json",
  "V0.7.59-ACTIVE-ARTIFACT-TIMELINE.json",
  "V0.7.59-RUNTIME-GENERATION-SOURCE-HITS.json",
  "V0.7.59-RUNTIME-GENERATION-HOT-SNIPPETS.json",
  "V0.7.59-READONLY-COURSE-GENERATOR-SIMULATION.json",
  "V0.7.59-COURSE-GENERATOR-FOCUSED-WINDOW.txt",
  "V0.7.59-WEBAPP-GENERATE-ROUTE-WINDOW.txt",
  "V0.7.59-OCR-MATH-HOOK-WINDOW.txt",
  "V0.7.59-OCR-REPORT-WINDOW.txt",
  "V0.7.59-NORMALIZED-OUTLINE-COMPARE.json",
  "V0.7.59-GENERATE-STEP-PRESENCE-AUDIT.json",
  "V0.7.59-NORMALIZE-OUTLINE-LESSON-DIFF.json",
  "V0.7.59-NORMALIZE-OUTLINE-SOURCE-WINDOW.txt"
)

if (!(Test-Path $doc)) {
  throw "Missing v0.7.59 audit doc: $doc"
}

foreach ($name in $requiredEvidence) {
  $path = Join-Path $evidenceRoot $name
  if (!(Test-Path $path)) {
    throw "Missing required v0.7.59 evidence: $path"
  }
}

$timeline = Get-Content (Join-Path $evidenceRoot "V0.7.59-ACTIVE-ARTIFACT-TIMELINE.json") -Raw | ConvertFrom-Json
$quizArtifact = $timeline | Where-Object { $_.file -eq "quiz.json" }
$flashcardsArtifact = $timeline | Where-Object { $_.file -eq "flashcards.json" }
$glossaryArtifact = $timeline | Where-Object { $_.file -eq "glossary.json" }
$ocrReportArtifact = $timeline | Where-Object { $_.file -eq "ocr_report.json" }
$ocrMathMdArtifact = $timeline | Where-Object { $_.file -eq "ocr_math_report.md" }
$ocrMathJsonArtifact = $timeline | Where-Object { $_.file -eq "ocr_math_report.json" }

if ($quizArtifact.exists -ne $true) { throw "Expected active quiz.json to exist" }
if ($flashcardsArtifact.empty_array -ne $true) { throw "Expected active flashcards.json to be empty array" }
if ($glossaryArtifact.empty_array -ne $true) { throw "Expected active glossary.json to be empty array" }
if ($ocrReportArtifact.exists -ne $false) { throw "Expected active ocr_report.json to be missing" }
if ($ocrMathMdArtifact.exists -ne $false) { throw "Expected active ocr_math_report.md to be missing" }
if ($ocrMathJsonArtifact.exists -ne $false) { throw "Expected active ocr_math_report.json to be missing" }

$compare = Get-Content (Join-Path $evidenceRoot "V0.7.59-NORMALIZED-OUTLINE-COMPARE.json") -Raw | ConvertFrom-Json
if ([int]$compare.simulation_from_course_outline_json.lesson_count -ne 2) { throw "Expected course_outline.json lesson_count=2" }
if ([int]$compare.simulation_from_course_outline_normalized_json.lesson_count -ne 1) { throw "Expected course_outline.normalized.json lesson_count=1" }
if ([int]$compare.simulation_from_course_outline_json.quiz_count -ne 2) { throw "Expected course_outline.json simulated quiz_count=2" }
if ([int]$compare.simulation_from_course_outline_normalized_json.quiz_count -ne 1) { throw "Expected normalized simulated quiz_count=1" }
if ([int]$compare.active_counts.quiz_count -ne 1) { throw "Expected active quiz_count=1" }
if ($compare.matches_active.normalized_json_quiz_count_matches -ne $true) { throw "Expected normalized quiz count to match active quiz" }
if ($compare.matches_active.normalized_json_flashcards_count_matches -ne $true) { throw "Expected normalized flashcards count to match active flashcards" }
if ($compare.matches_active.normalized_json_glossary_count_matches -ne $true) { throw "Expected normalized glossary count to match active glossary" }

$lessonDiff = Get-Content (Join-Path $evidenceRoot "V0.7.59-NORMALIZE-OUTLINE-LESSON-DIFF.json") -Raw | ConvertFrom-Json
if ([int]$lessonDiff.outline_lesson_count -ne 2) { throw "Expected outline_lesson_count=2" }
if ([int]$lessonDiff.normalized_lesson_count -ne 1) { throw "Expected normalized_lesson_count=1" }
$removed = @($lessonDiff.removed_or_merged_lesson_ids)
if ($removed -notcontains "L002") { throw "Expected lesson diff to record L002 as removed_or_merged due renumbering" }
$originalL001 = @($lessonDiff.outline_lessons) | Where-Object { $_.lesson_id -eq "L001" }
if ([int]$originalL001.word_count -ne 19) { throw "Expected original L001 word_count=19" }

$source = Get-Content (Join-Path $evidenceRoot "V0.7.59-NORMALIZE-OUTLINE-SOURCE-WINDOW.txt") -Raw
if ($source -notlike "*if word_count < 20:*") { throw "Expected normalize_outline source to contain word_count < 20 rule" }
if (($source -notlike "*lesson_id*") -or ($source -notlike "*L{index:03d}*")) { throw "Expected normalize_outline source to contain lesson renumbering" }

$generator = Get-Content (Join-Path $evidenceRoot "V0.7.59-COURSE-GENERATOR-FOCUSED-WINDOW.txt") -Raw
foreach ($term in @("steam trap", "pumping trap", "non-return valve", "bilge system")) {
  if ($generator -notlike "*$term*") {
    throw "Expected English/marine technical term in generator dictionary: $term"
  }
}
if ($generator -notlike "*def find_terms*") { throw "Expected course_generator find_terms" }
if ($generator -notlike "*def make_flashcards*") { throw "Expected course_generator make_flashcards" }

$stepAudit = Get-Content (Join-Path $evidenceRoot "V0.7.59-GENERATE-STEP-PRESENCE-AUDIT.json") -Raw | ConvertFrom-Json
function Assert-Step($Name, $Expected) {
  $row = $stepAudit | Where-Object { $_.check -eq $Name }
  if (!$row) { throw "Missing step audit row: $Name" }
  if ($row.present -ne $Expected) {
    throw "Unexpected step audit result for $Name. Expected $Expected, got $($row.present)"
  }
}

Assert-Step "generate_for_pdf_calls_pdf_extract" $true
Assert-Step "generate_for_pdf_calls_outline_builder" $true
Assert-Step "generate_for_pdf_calls_normalize_outline" $true
Assert-Step "generate_for_pdf_calls_course_generator" $true
Assert-Step "generate_for_pdf_calls_course_polisher" $true
Assert-Step "generate_for_pdf_calls_ocr_report" $false
Assert-Step "generate_for_pdf_calls_ocr_math_report_hook" $false
Assert-Step "generate_for_pdf_mentions_VOILA_ENABLE_OCR_MATH_REPORT_HOOK" $false

$docText = Get-Content $doc -Raw
$requiredDocText = @(
  'VOILA_V0_7_59_ACTIVE_COURSE_GENERATION_QUALITY_ROOT_CAUSE_AUDIT_CHECK=PASS_ROOT_CAUSE_IDENTIFIED',
  'Status: ROOT_CAUSE_IDENTIFIED / NOT FIXED',
  'No product patch.',
  'No regeneration.',
  'No build.',
  'No ZIP.',
  'No share.',
  'No delivery.',
  'No distribution.',
  'normalized outline has only one lesson',
  'rule-based generator is English/marine-term focused',
  'OCR report generation is not part of',
  'OCR Math report hook is not part of',
  '/generate',
  'DO NOT package for testers',
  'v0.7.60-owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery'
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Doc missing expected v0.7.59 text: $item"
  }
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.59 audit: $line"
  }
}

"VOILA_V0_7_59_ACTIVE_COURSE_GENERATION_QUALITY_ROOT_CAUSE_AUDIT_CHECK=PASS_ROOT_CAUSE_IDENTIFIED"
"ROOT_CAUSE_QUIZ_TOO_THIN=normalized_outline_reduces_to_one_lesson_and_generator_runs_on_normalized_outline"
"ROOT_CAUSE_FLASHCARDS_GLOSSARY_EMPTY=english_marine_terms_dictionary_no_romanian_math_terms"
"ROOT_CAUSE_OCR_REPORT_MISSING=generate_for_pdf_does_not_call_ocr_report_py"
"ROOT_CAUSE_OCR_MATH_REPORT_MISSING=generate_for_pdf_does_not_call_ocr_math_report_hook"
"TESTER_READINESS=BLOCKED"
"POLICY=audit_only_no_product_patch_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
