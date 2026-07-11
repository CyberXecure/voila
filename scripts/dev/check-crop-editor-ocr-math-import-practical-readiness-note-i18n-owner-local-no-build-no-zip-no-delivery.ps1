$ErrorActionPreference = "Stop"

$target = "services/api/crop_editor_app.py"
$doc = "docs/dev/crop-editor-ocr-math-import-practical-readiness-note-i18n-owner-local-no-build-no-zip-no-delivery.md"

foreach ($path in @($target, $doc)) {
  if (!(Test-Path $path)) {
    throw "Missing required path: $path"
  }
}

python -m py_compile $target

$text = Get-Content $target -Raw
$docText = Get-Content $doc -Raw

$requiredTargetText = @(
  "VOILA_V0_7_53_CROP_EDITOR_OCR_MATH_IMPORT_PRACTICAL_READINESS_NOTE_I18N",
  "practical_note_title",
  "practical_note_body",
  "Practical owner-local checklist",
  "Checklist practic owner-local",
  "Inspect the OCR Math candidate before importing",
  "Inspecteaz\u0103 candidatul OCR Math",
  "Confirm the browser prompt",
  "Confirm\u0103 promptul din browser",
  "ocr-math-practical-readiness-note",
  "def _crop_editor_text(en: str, ro: str) -> str",
  "/ocr-math-sidecar-import"
)

foreach ($item in $requiredTargetText) {
  if ($text -notlike "*$item*") {
    throw "Crop Editor missing expected v0.7.53 text: $item"
  }
}

$forbiddenTargetText = @(
  "Practical owner-local checklist / Checklist practic owner-local",
  "Candida╚",
  "Ac╚"
)

foreach ($item in $forbiddenTargetText) {
  if ($text -like "*$item*") {
    throw "Crop Editor contains abandoned/corrupted text: $item"
  }
}

$requiredDocText = @(
  "VOILA_V0_7_53_CROP_EDITOR_OCR_MATH_IMPORT_PRACTICAL_READINESS_NOTE_I18N_CHECK=PASS",
  "OWNER-LOCAL I18N UI POLISH PASS",
  "Checklist practic owner-local",
  "Practical owner-local checklist",
  "The import button was not clicked",
  "guidance text only",
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
    throw "Doc missing expected v0.7.53 text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "services/api/crop_editor_app.py",
  "docs/dev/crop-editor-ocr-math-import-practical-readiness-note-i18n-owner-local-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-crop-editor-ocr-math-import-practical-readiness-note-i18n-owner-local-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_53_CROP_EDITOR_OCR_MATH_IMPORT_PRACTICAL_READINESS_NOTE_I18N_CHECK=PASS"
"POLICY=owner_local_i18n_ui_guidance_only_no_import_click_no_import_logic_change_no_build_no_zip_no_share_no_delivery_no_distribution"
