$ErrorActionPreference = "Stop"

Write-Host "v0.7.89 check: start"

$script = "scripts/dev/build-formula-visual-evidence-manifest.py"
$doc = "docs/dev/formula-visual-evidence-manifest-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0789-formula-visual-evidence-manifest"
$sourceInspect = "$evidenceDir\V0.7.89-FORMULA-VISUAL-EVIDENCE-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.89-FORMULA-VISUAL-EVIDENCE-MANIFEST-SMOKE.json"

$courseId = "03-pag-30-34-vectori-trigonometrie"
$manifest = "data/output/$courseId/formula_visual_evidence.manifest.json"
$cropsDir = "data/output/$courseId/formula_visual_evidence/crops"
$pagesDir = "data/output/$courseId/formula_visual_evidence/pages"

foreach ($p in @($script, $doc, $sourceInspect, $smoke, $manifest, $cropsDir, $pagesDir)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence/artifact: $p" }
}

python -m py_compile $script

$scriptText = Get-Content $script -Raw
foreach ($item in @(
  "VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_BUILD=PASS",
  "formula_visual_evidence_manifest",
  "formula_visual_evidence.manifest.json",
  "formula_visual_evidence",
  "get_pixmap",
  "bbox",
  "crop_path",
  "pending_owner_review",
  "uses_llm",
  "uses_cloud",
  "ocr_rewrite_performed",
  "formula_ocr_performed"
)) {
  if ($scriptText -notlike "*$item*") { throw "Script missing expected text: $item" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.modules.fitz -ne $true) { throw "fitz availability mismatch" }
if ($sourceData.pdf_probe.can_render_pixmap -ne $true) { throw "can_render_pixmap mismatch" }
if ($sourceData.paths.pages_json.exists -ne $true) { throw "pages_json_exists mismatch" }
if ($sourceData.implementation_readiness -ne "READY_FOR_LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST") { throw "implementation_readiness mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.manifest_exists -ne $true) { throw "manifest_exists mismatch" }
if ($smokeData.page_count -ne 5) { throw "page_count mismatch" }
if ($smokeData.candidate_count -ne 43) { throw "candidate_count mismatch" }
if ($smokeData.page_image_count -ne 5) { throw "page_image_count mismatch" }
if ($smokeData.sample_crop_exists -ne $true) { throw "sample_crop_exists mismatch" }
if ($smokeData.uses_pymupdf -ne $true) { throw "uses_pymupdf mismatch" }
if ($smokeData.uses_llm -ne $false) { throw "uses_llm mismatch" }
if ($smokeData.uses_cloud -ne $false) { throw "uses_cloud mismatch" }
if ($smokeData.ocr_rewrite_performed -ne $false) { throw "ocr_rewrite_performed mismatch" }
if ($smokeData.formula_ocr_performed -ne $false) { throw "formula_ocr_performed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$manifestData = Get-Content $manifest -Raw | ConvertFrom-Json
if ($manifestData.artifact -ne "formula_visual_evidence_manifest") { throw "Manifest artifact mismatch" }
if ($manifestData.version -ne "v0.7.89") { throw "Manifest version mismatch" }
if ($manifestData.course_id -ne $courseId) { throw "Manifest course_id mismatch" }
if ($manifestData.page_count -ne 5) { throw "Manifest page_count mismatch" }
if ($manifestData.candidate_count -ne 43) { throw "Manifest candidate_count mismatch" }
if (($manifestData.page_images | Measure-Object).Count -ne 5) { throw "Manifest page image count mismatch" }
if (($manifestData.candidates | Measure-Object).Count -ne 43) { throw "Manifest candidates count mismatch" }

$firstCandidate = $manifestData.candidates | Select-Object -First 1
if (-not $firstCandidate.id) { throw "First candidate missing id" }
if (-not $firstCandidate.crop_path) { throw "First candidate missing crop_path" }
if (-not $firstCandidate.bbox) { throw "First candidate missing bbox" }
if (-not $firstCandidate.reasons) { throw "First candidate missing reasons" }
if ($firstCandidate.review_status -ne "pending_owner_review") { throw "First candidate review status mismatch" }

$firstCrop = Join-Path "data/output/$courseId" $firstCandidate.crop_path
if (!(Test-Path $firstCrop)) { throw "First crop file missing: $firstCrop" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_CHECK=PASS",
  "PASS_FORMULA_VISUAL_EVIDENCE_MANIFEST",
  "VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_SOURCE_INSPECT=PASS",
  "IMPLEMENTATION_READINESS=READY_FOR_LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST",
  "VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_BUILD=PASS",
  "VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_SMOKE=PASS",
  "page_count=5",
  "candidate_count=43",
  "page_image_count=5",
  "sample_crop_exists=True",
  "uses_pymupdf=True",
  "uses_llm=False",
  "uses_cloud=False",
  "ocr_rewrite_performed=False",
  "formula_ocr_performed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "scripts/dev/build-formula-visual-evidence-manifest.py",
  "docs/dev/formula-visual-evidence-manifest-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-formula-visual-evidence-manifest-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_CHECK=PASS"
"IMPLEMENTATION_READINESS=READY_FOR_LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST"
"PAGE_COUNT=5"
"CANDIDATE_COUNT=43"
"PAGE_IMAGE_COUNT=5"
"SAMPLE_CROP_EXISTS=True"
"USES_PYMUPDF=True"
"USES_LLM=False"
"USES_CLOUD=False"
"OCR_REWRITE_PERFORMED=False"
"FORMULA_OCR_PERFORMED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST_PASS_NOT_PACKAGED"
"POLICY=formula_visual_evidence_manifest_no_build_no_zip_no_share_no_delivery_no_distribution"
