$ErrorActionPreference = "Stop"

$target = "services/api/crop_editor_app.py"
$doc = "docs/dev/crop-editor-ui-language-bridge-owner-local-no-build-no-zip-no-delivery.md"

foreach ($path in @($target, $doc)) {
  if (!(Test-Path $path)) {
    throw "Missing required path: $path"
  }
}

python -m py_compile $target

$text = Get-Content $target -Raw
$docText = Get-Content $doc -Raw

$requiredTargetText = @(
  "VOILA_V0_7_51_CROP_EDITOR_UI_LANGUAGE_BRIDGE_START",
  "VOILA_V0_7_51_CROP_EDITOR_UI_LANGUAGE_BRIDGE_END",
  "def _crop_editor_ui_language_code()",
  "def _crop_editor_text(en: str, ro: str) -> str",
  "i18n.get_ui_language(PROJECT_ROOT)",
  '<html lang="{html.escape(_crop_editor_ui_language_code(), quote=True)}">',
  "sidecar_heading",
  "import_confirm",
  "import_button",
  "import_note",
  "OCR Math visual fallback candidates",
  "Candida\u021bi vizuali OCR Math pentru fallback",
  "Import OCR Math sidecar candidates",
  "Import\u0103 candida\u021bii OCR Math din sidecar",
  "/ocr-math-sidecar-import",
  "no auto-import"
)

foreach ($item in $requiredTargetText) {
  if ($text -notlike "*$item*") {
    throw "Crop Editor missing expected v0.7.51 text: $item"
  }
}

$forbiddenTargetText = @(
  "Candida╚",
  "Ac╚",
  "┬╖",
  "Practical owner-local checklist",
  "Checklist practic owner-local"
)

foreach ($item in $forbiddenTargetText) {
  if ($text -like "*$item*") {
    throw "Crop Editor contains corrupted or abandoned v0.7.51 text: $item"
  }
}

$requiredDocText = @(
  "VOILA_V0_7_51_CROP_EDITOR_UI_LANGUAGE_BRIDGE_CHECK=PASS",
  "i18n.get_ui_language(PROJECT_ROOT)",
  'html lang="ro"',
  'html lang="en"',
  "localizes only the OCR Math sidecar import",
  "preserves existing import behavior",
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
    throw "Doc missing expected v0.7.51 text: $item"
  }
}

$changed = git diff --name-only --
$allowed = @(
  "services/api/crop_editor_app.py",
  "docs/dev/crop-editor-ui-language-bridge-owner-local-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-crop-editor-ui-language-bridge-owner-local-no-build-no-zip-no-delivery.ps1"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_51_CROP_EDITOR_UI_LANGUAGE_BRIDGE_CHECK=PASS"
"POLICY=owner_local_ui_language_bridge_no_import_logic_change_no_build_no_zip_no_share_no_delivery_no_distribution"
