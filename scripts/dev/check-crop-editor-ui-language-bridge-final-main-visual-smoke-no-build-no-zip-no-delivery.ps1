$ErrorActionPreference = "Stop"

$target = "services/api/crop_editor_app.py"
$v0751Check = "scripts/dev/check-crop-editor-ui-language-bridge-owner-local-no-build-no-zip-no-delivery.ps1"
$doc = "docs/dev/crop-editor-ui-language-bridge-final-main-visual-smoke-no-build-no-zip-no-delivery.md"

foreach ($path in @($target, $v0751Check, $doc)) {
  if (!(Test-Path $path)) {
    throw "Missing required path: $path"
  }
}

python -m py_compile $target
& ".\$v0751Check"

$docText = Get-Content $doc -Raw

$requiredDocText = @(
  "VOILA_V0_7_52_CROP_EDITOR_UI_LANGUAGE_BRIDGE_FINAL_MAIN_VISUAL_SMOKE_CHECK=PASS",
  "FINAL-MAIN VISUAL SMOKE PASS",
  "Candidați vizuali OCR Math pentru fallback",
  "Importă candidații OCR Math din sidecar",
  "Acțiune explicită owner-local",
  "OCR Math visual fallback candidates",
  "Import OCR Math sidecar candidates",
  "Explicit owner-local action",
  "The import button was not clicked",
  "No import logic change",
  "No auto-import",
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
    throw "Doc missing expected v0.7.52 text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "docs/dev/crop-editor-ui-language-bridge-final-main-visual-smoke-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-crop-editor-ui-language-bridge-final-main-visual-smoke-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_52_CROP_EDITOR_UI_LANGUAGE_BRIDGE_FINAL_MAIN_VISUAL_SMOKE_CHECK=PASS"
"POLICY=final_main_visual_smoke_only_no_import_click_no_build_no_zip_no_share_no_delivery_no_distribution"
