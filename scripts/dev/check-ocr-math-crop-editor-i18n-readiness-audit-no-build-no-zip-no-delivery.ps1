$ErrorActionPreference = "Stop"

$doc = "docs/dev/ocr-math-crop-editor-i18n-readiness-audit-no-build-no-zip-no-delivery.md"
$cropEditor = "services/api/crop_editor_app.py"
$webApp = "services/api/web_app.py"

foreach ($path in @($doc, $cropEditor, $webApp)) {
  if (!(Test-Path $path)) {
    throw "Missing required path: $path"
  }
}

python -m py_compile $cropEditor
python -m py_compile $webApp

$cropText = Get-Content $cropEditor -Raw
$webText = Get-Content $webApp -Raw
$docText = Get-Content $doc -Raw

$requiredCropText = @(
  "<html lang=`"en`">",
  "Import OCR Math sidecar candidates",
  "/ocr-math-sidecar-import",
  "no auto-import"
)

foreach ($item in $requiredCropText) {
  if ($cropText -notlike "*$item*") {
    throw "Crop Editor missing expected audited text: $item"
  }
}

$forbiddenCropText = @(
  "VOILA_V0_7_50_OCR_MATH_SIDECAR_IMPORT_PRACTICAL_READINESS_NOTE",
  "Practical owner-local checklist",
  "Checklist practic owner-local"
)

foreach ($item in $forbiddenCropText) {
  if ($cropText -like "*$item*") {
    throw "Crop Editor still contains abandoned v0.7.50 hard-coded note: $item"
  }
}

$requiredWebText = @(
  "def _ut",
  "get_ui_language",
  "ui-language-form",
  "Interface language"
)

foreach ($item in $requiredWebText) {
  if ($webText -notlike "*$item*") {
    throw "web_app missing expected i18n evidence: $item"
  }
}

$requiredDocText = @(
  "VOILA_V0_7_50_OCR_MATH_CROP_EDITOR_I18N_READINESS_AUDIT_CHECK=PASS",
  "Crop Editor is currently a standalone FastAPI app with hard-coded English UI strings",
  "main Voila web app already has UI language support",
  "Do not commit the v0.7.50 hard-coded readiness note",
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
    throw "Doc missing expected text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "docs/dev/ocr-math-crop-editor-i18n-readiness-audit-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-ocr-math-crop-editor-i18n-readiness-audit-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_50_OCR_MATH_CROP_EDITOR_I18N_READINESS_AUDIT_CHECK=PASS"
"POLICY=no_behavior_change_no_build_no_zip_no_share_no_delivery_no_distribution"
