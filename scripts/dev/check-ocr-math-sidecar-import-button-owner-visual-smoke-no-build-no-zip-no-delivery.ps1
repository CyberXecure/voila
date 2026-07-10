$ErrorActionPreference = "Stop"

$prepare = "scripts/dev/prepare-ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.ps1"
$doc = "docs/dev/ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.md"
$cropEditor = "services/api/crop_editor_app.py"
$importer = "services/api/ocr_math_sidecar_crop_manifest_importer.py"

foreach ($path in @($prepare, $doc, $cropEditor, $importer)) {
  if (!(Test-Path $path)) {
    throw "Missing required path: $path"
  }
}

python -m py_compile $cropEditor
python -m py_compile $importer

$output = & ".\$prepare"
$text = ($output | Out-String)

$requiredOutput = @(
  "VOILA_V0_7_48_OWNER_VISUAL_SMOKE_FIXTURE_READY=PASS",
  "CROP_EDITOR_URL=http://127.0.0.1:8790/?pdf=v0748-ocr-math-sidecar-import-button-smoke.pdf",
  "POLICY=explicit_owner_local_import_no_auto_import_no_build_no_zip_no_share_no_delivery_no_distribution"
)

foreach ($item in $requiredOutput) {
  if ($text -notlike "*$item*") {
    throw "Missing prepare output: $item"
  }
}

$stem = "v0748-ocr-math-sidecar-import-button-smoke"
$out = "data/output/$stem"
$manifestPath = "$out/figures_hybrid/figures_manifest.hybrid.json"
$sidecarPath = "$out/figures_hybrid/ocr_math_visual_fallback_manifest.json"

foreach ($path in @("data/input/$stem.pdf", $manifestPath, $sidecarPath)) {
  if (!(Test-Path $path)) {
    throw "Missing owner-local fixture file: $path"
  }
}

$docText = Get-Content $doc -Raw
$requiredDoc = @(
  "VOILA_V0_7_48_OWNER_VISUAL_SMOKE_CHECK=PASS",
  "Manual visual result",
  "PASS",
  "Import OCR Math sidecar candidates button is visible",
  "Hybrid figure crops shows Figure 1 and imported Figure 2",
  "duplicates skipped: 1",
  "No build",
  "No ZIP",
  "No share",
  "No delivery",
  "No distribution"
)

foreach ($item in $requiredDoc) {
  if ($docText -notlike "*$item*") {
    throw "Missing doc text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "scripts/dev/prepare-ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.ps1",
  "docs/dev/ocr-math-sidecar-import-button-owner-visual-smoke-no-build-no-zip-no-delivery.md"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_48_OWNER_VISUAL_SMOKE_CHECK=PASS"
"POLICY=explicit_owner_local_import_no_auto_import_no_build_no_zip_no_share_no_delivery_no_distribution"
