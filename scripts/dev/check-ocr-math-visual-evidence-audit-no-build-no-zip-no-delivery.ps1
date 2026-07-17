$ErrorActionPreference = "Stop"

Write-Host "v0.7.88 check: start"

$doc = "docs/dev/ocr-math-visual-evidence-audit-no-build-no-zip-no-delivery.md"
$evidence = "D:\dev\tester-runs\v0788-ocr-math-visual-evidence-audit\V0.7.88-OCR-MATH-VISUAL-EVIDENCE-SOURCE-INSPECT.json"

foreach ($p in @($doc, $evidence)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

$data = Get-Content $evidence -Raw | ConvertFrom-Json

if ($data.VOILA_V0_7_88_OCR_MATH_VISUAL_EVIDENCE_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($data.visual_evidence.figure_image_count -ne 0) { throw "figure_image_count mismatch" }
if ($data.visual_evidence.has_hybrid_manifest -ne $false) { throw "has_hybrid_manifest mismatch" }
if ($data.visual_evidence.manifest_item_count_guess -ne 0) { throw "manifest_item_count_guess mismatch" }
if ($data.report_reality -ne "BLOCKED_NO_VISUAL_EVIDENCE_ARTIFACTS_FOUND") { throw "report_reality mismatch" }
if ($data.BUILD_PERFORMED -ne $false) { throw "BUILD_PERFORMED mismatch" }
if ($data.ZIP_CREATED -ne $false) { throw "ZIP_CREATED mismatch" }
if ($data.SHARE_CREATED -ne $false) { throw "SHARE_CREATED mismatch" }
if ($data.DELIVERY_PERFORMED -ne $false) { throw "DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_88_OCR_MATH_VISUAL_EVIDENCE_AUDIT_CHECK=PASS",
  "BLOCKED_NO_VISUAL_EVIDENCE_ARTIFACTS_FOUND",
  "VOILA_V0_7_88_OCR_MATH_VISUAL_EVIDENCE_SOURCE_INSPECT=PASS",
  "figure_image_count=0",
  "has_hybrid_manifest=False",
  "manifest_item_count_guess=0",
  "REPORT_REALITY=BLOCKED_NO_VISUAL_EVIDENCE_ARTIFACTS_FOUND",
  "formula crops",
  "symbol/formula visual snippets",
  "page coordinates / bounding boxes",
  "No OCR rewrite.",
  "No Formula OCR implementation.",
  "No visual crop extractor implementation.",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=BLOCKED_OCR_MATH_VISUAL_EVIDENCE_MISSING_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "docs/dev/ocr-math-visual-evidence-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-ocr-math-visual-evidence-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_88_OCR_MATH_VISUAL_EVIDENCE_AUDIT_CHECK=PASS"
"REPORT_REALITY=BLOCKED_NO_VISUAL_EVIDENCE_ARTIFACTS_FOUND"
"FIGURE_IMAGE_COUNT=0"
"HAS_HYBRID_MANIFEST=False"
"MANIFEST_ITEM_COUNT_GUESS=0"
"OCR_MATH_USEFULNESS=BLOCKED_VISUAL_EVIDENCE_MISSING"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=BLOCKED_OCR_MATH_VISUAL_EVIDENCE_MISSING_NOT_PACKAGED"
"POLICY=ocr_math_visual_evidence_audit_no_build_no_zip_no_share_no_delivery_no_distribution"
