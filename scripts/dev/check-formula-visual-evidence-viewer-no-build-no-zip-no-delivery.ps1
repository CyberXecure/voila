$ErrorActionPreference = "Stop"

Write-Host "v0.7.90 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/formula-visual-evidence-viewer-no-build-no-zip-no-delivery.md"

$evidenceDir = "D:\dev\tester-runs\v0790-formula-visual-evidence-viewer"
$sourceInspect = "$evidenceDir\V0.7.90-FORMULA-VISUAL-EVIDENCE-VIEWER-SOURCE-INSPECT.json"
$smoke = "$evidenceDir\V0.7.90-FORMULA-VISUAL-EVIDENCE-VIEWER-SMOKE.json"

foreach ($p in @($web, $doc, $sourceInspect, $smoke)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web

$webText = Get-Content $web -Raw
foreach ($item in @(
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_START",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_END",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_BOOL_DISPLAY_START",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_BOOL_DISPLAY_END",
  "owner_formula_visual_evidence_view",
  "owner_formula_visual_evidence_asset",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_SAFE_ASSET_START",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_SAFE_ASSET_END",
  "safe_candidate_id",
  "candidate_id",
  "formula_visual_evidence.manifest.json",
  "formula_visual_evidence",
  "crop_path",
  "Motiv detectare:",
  "BBox:",
  "uses_llm_label",
  "uses_cloud_label",
  "formula_ocr_label"
)) {
  if ($webText -notlike "*$item*") { throw "web_app.py missing expected v0.7.90 text: $item" }
}

$sourceData = Get-Content $sourceInspect -Raw | ConvertFrom-Json
if ($sourceData.VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SOURCE_INSPECT -ne "PASS") { throw "Source inspect marker mismatch" }
if ($sourceData.manifest.exists -ne $true) { throw "manifest_exists mismatch" }
if ($sourceData.manifest.candidate_count -ne 43) { throw "candidate_count mismatch" }
if ($sourceData.manifest.page_count -ne 5) { throw "page_count mismatch" }
if ($sourceData.manifest.sample_crop_exists -ne $true) { throw "sample_crop_exists mismatch" }
if ($sourceData.BUILD_PERFORMED -ne $false) { throw "Source inspect BUILD_PERFORMED mismatch" }
if ($sourceData.ZIP_CREATED -ne $false) { throw "Source inspect ZIP_CREATED mismatch" }
if ($sourceData.SHARE_CREATED -ne $false) { throw "Source inspect SHARE_CREATED mismatch" }
if ($sourceData.DELIVERY_PERFORMED -ne $false) { throw "Source inspect DELIVERY_PERFORMED mismatch" }

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SMOKE -ne "PASS") { throw "Smoke marker mismatch" }
if ($smokeData.viewer_status -ne 200) { throw "viewer_status mismatch" }
if ($smokeData.asset_status -ne 200) { throw "asset_status mismatch" }
if ($smokeData.safe_candidate_id_asset_route -ne $true) { throw "safe_candidate_id_asset_route mismatch" }
if ($smokeData.unsafe_rel_path_removed -ne $true) { throw "unsafe_rel_path_removed mismatch" }
if ($smokeData.bad_asset_blocked -ne $true) { throw "bad_asset_blocked mismatch" }
if ($smokeData.candidate_count_visible -ne $true) { throw "candidate_count_visible mismatch" }
if ($smokeData.page_image_count_visible -ne $true) { throw "page_image_count_visible mismatch" }
if ($smokeData.crop_image_renderable -ne $true) { throw "crop_image_renderable mismatch" }
if ($smokeData.text_ocr_visible -ne $true) { throw "text_ocr_visible mismatch" }
if ($smokeData.reason_visible -ne $true) { throw "reason_visible mismatch" }
if ($smokeData.bbox_visible -ne $true) { throw "bbox_visible mismatch" }
if ($smokeData.review_status_visible -ne $true) { throw "review_status_visible mismatch" }
if ($smokeData.bool_false_labels_visible -ne $true) { throw "bool_false_labels_visible mismatch" }
if ($smokeData.uses_llm -ne $false) { throw "uses_llm mismatch" }
if ($smokeData.uses_cloud -ne $false) { throw "uses_cloud mismatch" }
if ($smokeData.ocr_rewrite_performed -ne $false) { throw "ocr_rewrite_performed mismatch" }
if ($smokeData.formula_ocr_performed -ne $false) { throw "formula_ocr_performed mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "Smoke BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "Smoke ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "Smoke SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "Smoke DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_CHECK=PASS",
  "PASS_FORMULA_VISUAL_EVIDENCE_VIEWER",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SOURCE_INSPECT=PASS",
  "manifest_exists=True",
  "candidate_count=43",
  "page_count=5",
  "sample_crop_exists=True",
  "VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SMOKE=PASS",
  "viewer_status=200",
  "asset_status=200",
  "safe_candidate_id_asset_route=True",
  "unsafe_rel_path_removed=True",
  "bad_asset_blocked=True",
  "candidate_count_visible=True",
  "page_image_count_visible=True",
  "crop_image_renderable=True",
  "text_ocr_visible=True",
  "reason_visible=True",
  "bbox_visible=True",
  "review_status_visible=True",
  "bool_false_labels_visible=True",
  "uses_llm=False",
  "uses_cloud=False",
  "ocr_rewrite_performed=False",
  "formula_ocr_performed=False",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_VIEWER_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/formula-visual-evidence-viewer-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-formula-visual-evidence-viewer-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_CHECK=PASS"
"VIEWER_STATUS=200"
"ASSET_STATUS=200"
"SAFE_CANDIDATE_ID_ASSET_ROUTE=True"
"UNSAFE_REL_PATH_REMOVED=True"
"BAD_ASSET_BLOCKED=True"
"CANDIDATE_COUNT_VISIBLE=True"
"PAGE_IMAGE_COUNT_VISIBLE=True"
"CROP_IMAGE_RENDERABLE=True"
"TEXT_OCR_VISIBLE=True"
"REASON_VISIBLE=True"
"BBOX_VISIBLE=True"
"REVIEW_STATUS_VISIBLE=True"
"BOOL_FALSE_LABELS_VISIBLE=True"
"USES_LLM=False"
"USES_CLOUD=False"
"OCR_REWRITE_PERFORMED=False"
"FORMULA_OCR_PERFORMED=False"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_VIEWER_PASS_NOT_PACKAGED"
"POLICY=formula_visual_evidence_viewer_no_build_no_zip_no_share_no_delivery_no_distribution"
