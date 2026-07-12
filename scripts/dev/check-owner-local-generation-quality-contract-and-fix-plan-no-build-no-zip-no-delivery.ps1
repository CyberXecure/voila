$ErrorActionPreference = "Stop"

$doc = "docs/dev/owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery.md"
$v0759Doc = "docs/dev/owner-local-active-course-generation-quality-root-cause-audit-no-build-no-zip-no-delivery.md"

if (!(Test-Path $doc)) {
  throw "Missing v0.7.60 doc: $doc"
}

if (!(Test-Path $v0759Doc)) {
  throw "Missing v0.7.59 baseline doc: $v0759Doc"
}

$v0759Text = Get-Content $v0759Doc -Raw
if ($v0759Text -notlike "*VOILA_V0_7_59_ACTIVE_COURSE_GENERATION_QUALITY_ROOT_CAUSE_AUDIT_CHECK=PASS_ROOT_CAUSE_IDENTIFIED*") {
  throw "v0.7.59 baseline marker missing"
}

$docText = Get-Content $doc -Raw

$required = @(
  "VOILA_V0_7_60_GENERATION_QUALITY_CONTRACT_AND_FIX_PLAN_CHECK=PASS_PLAN_ONLY",
  "Status: PLAN_ONLY / CONTRACT_DEFINED / NOT_FIXED",
  "No product patch.",
  "No regeneration.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "TECHNICAL_TERMS",
  "primary generator knowledge source",
  "learn/extract concepts from each OCR-recognized PDF",
  "document_concepts.json",
  "document_concepts.md",
  "PDF input",
  "OCR extraction",
  "document concept extraction",
  "document-specific glossary",
  "document-specific flashcards",
  "document-specific quiz",
  "Translation must not erase the source",
  "generation_quality_status=LOW_QUALITY_BLOCKED",
  "Tester readiness remains BLOCKED",
  "DO NOT package for testers"
)

foreach ($item in $required) {
  if ($docText -notlike "*$item*") {
    throw "v0.7.60 doc missing required text: $item"
  }
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-generation-quality-contract-and-fix-plan-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.60 plan-only milestone: $line"
  }
}

"VOILA_V0_7_60_GENERATION_QUALITY_CONTRACT_AND_FIX_PLAN_CHECK=PASS_PLAN_ONLY"
"GENERATION_DIRECTION=document_specific_concept_extraction_before_lessons"
"STATIC_TECHNICAL_TERMS_PRIMARY_SOURCE=REJECTED"
"PROPOSED_ARTIFACT=document_concepts_json_and_md"
"TESTER_READINESS=BLOCKED"
"POLICY=plan_only_no_product_patch_no_regeneration_no_build_no_zip_no_share_no_delivery_no_distribution"
