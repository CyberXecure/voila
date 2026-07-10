$ErrorActionPreference = "Stop"

$requiredPaths = @(
  "services/api/ocr_math_report.py",
  "services/api/ocr_math_visual_fallback_candidates.py",
  "services/api/ocr_math_visual_fallback_figures_bridge.py",
  "services/api/crop_editor_app.py",
  "services/api/ocr_math_sidecar_crop_manifest_importer.py",

  "docs/dev/ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-visual-fallback-candidates-to-figures-crop-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-visual-fallback-sidecar-visible-in-crop-ui-no-import-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-sidecar-explicit-import-to-crop-manifest-owner-local-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-sidecar-explicit-import-button-crop-ui-owner-local-no-auto-import-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.md",
  "docs/dev/ocr-math-visual-fallback-flow-final-audit-no-build-no-zip-no-delivery.md",

  "scripts/dev/check-ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-visual-fallback-candidates-to-figures-crop-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-visual-fallback-sidecar-visible-in-crop-ui-no-import-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-explicit-import-to-crop-manifest-owner-local-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-explicit-import-button-crop-ui-owner-local-no-auto-import-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-visual-fallback-flow-final-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $requiredPaths) {
  if (!(Test-Path $path)) {
    throw "Missing required audited path: $path"
  }
}

$pythonFiles = @(
  "services/api/ocr_math_report.py",
  "services/api/ocr_math_visual_fallback_candidates.py",
  "services/api/ocr_math_visual_fallback_figures_bridge.py",
  "services/api/crop_editor_app.py",
  "services/api/ocr_math_sidecar_crop_manifest_importer.py"
)

foreach ($path in $pythonFiles) {
  python -m py_compile $path
}

$cropEditorText = Get-Content "services/api/crop_editor_app.py" -Raw
$importerText = Get-Content "services/api/ocr_math_sidecar_crop_manifest_importer.py" -Raw
$candidatesText = Get-Content "services/api/ocr_math_visual_fallback_candidates.py" -Raw
$bridgeText = Get-Content "services/api/ocr_math_visual_fallback_figures_bridge.py" -Raw
$docText = Get-Content "docs/dev/ocr-math-visual-fallback-flow-final-audit-no-build-no-zip-no-delivery.md" -Raw

$requiredCropEditorText = @(
  "ocr_math_visual_fallback_manifest.json",
  "Import OCR Math sidecar candidates",
  "/ocr-math-sidecar-import",
  "no auto-import",
  "source_candidate_id"
)

foreach ($item in $requiredCropEditorText) {
  if ($cropEditorText -notlike "*$item*") {
    throw "Crop Editor missing expected text: $item"
  }
}

$requiredImporterText = @(
  "apply: bool = False",
  "manifest_written",
  "duplicate_count",
  "source_candidate_id",
  "figures_manifest.hybrid.json.v0.7.46.bak"
)

foreach ($item in $requiredImporterText) {
  if ($importerText -notlike "*$item*") {
    throw "Importer missing expected text: $item"
  }
}

$requiredCandidatesText = @(
  "visual_fallback_candidates.json",
  "ocr_math_report.json",
  "page_images"
)

foreach ($item in $requiredCandidatesText) {
  if ($candidatesText -notlike "*$item*") {
    throw "Candidates generator missing expected text: $item"
  }
}

$requiredBridgeText = @(
  "ocr_math_visual_fallback_manifest.json",
  "figures_hybrid",
  "figure_crops",
  "crop_editor_manifest_overwritten"
)

foreach ($item in $requiredBridgeText) {
  if ($bridgeText -notlike "*$item*") {
    throw "Figures bridge missing expected text: $item"
  }
}

$requiredDocText = @(
  "VOILA_V0_7_49_OCR_MATH_VISUAL_FALLBACK_FLOW_FINAL_AUDIT_CHECK=PASS",
  "v0.7.42",
  "v0.7.43",
  "v0.7.44",
  "v0.7.45",
  "v0.7.46",
  "v0.7.47",
  "v0.7.48",
  "No OCR text rewrite",
  "No Course rewrite",
  "No Study rewrite",
  "No Progress rewrite",
  "No build",
  "No ZIP",
  "No share",
  "No delivery",
  "No distribution"
)

foreach ($item in $requiredDocText) {
  if ($docText -notlike "*$item*") {
    throw "Final audit doc missing expected text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "docs/dev/ocr-math-visual-fallback-flow-final-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-ocr-math-visual-fallback-flow-final-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_49_OCR_MATH_VISUAL_FALLBACK_FLOW_FINAL_AUDIT_CHECK=PASS"
"POLICY=no_behavior_change_no_build_no_zip_no_share_no_delivery_no_distribution"
