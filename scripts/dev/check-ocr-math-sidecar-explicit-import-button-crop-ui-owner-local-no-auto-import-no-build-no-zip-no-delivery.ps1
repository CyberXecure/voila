$ErrorActionPreference = "Stop"

$cropEditor = "services/api/crop_editor_app.py"
$importer = "services/api/ocr_math_sidecar_crop_manifest_importer.py"
$doc = "docs/dev/ocr-math-sidecar-explicit-import-button-crop-ui-owner-local-no-auto-import-no-build-no-zip-no-delivery.md"

if (!(Test-Path $cropEditor)) { throw "Missing Crop Editor app: $cropEditor" }
if (!(Test-Path $importer)) { throw "Missing importer: $importer" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }

python -m py_compile $cropEditor
python -m py_compile $importer

$text = Get-Content $cropEditor -Raw

$required = @(
  "VOILA_V0_7_47_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_BUTTON_CROP_UI_OWNER_LOCAL",
  "Import OCR Math sidecar candidates",
  "/ocr-math-sidecar-import",
  "no auto-import",
  "creates backup",
  "skips duplicate source_candidate_id",
  "import_sidecar_to_crop_manifest",
  "apply=True",
  "ocr_math_import=PASS",
  "ocr_math_import=FAIL"
)

foreach ($item in $required) {
  if ($text -notlike "*$item*") {
    throw "Missing Crop UI import text: $item"
  }
}

$fixture = Join-Path $env:TEMP "voila-v0.7.47-crop-ui-import-button-fixture"
Remove-Item $fixture -Recurse -Force -ErrorAction SilentlyContinue

$inputDir = Join-Path $fixture "input"
$outputRoot = Join-Path $fixture "output"
$stem = "v0747-ocr-math-import-button"
$pdfName = "$stem.pdf"
$outputFolder = Join-Path $outputRoot $stem
$figuresDir = Join-Path $outputFolder "figures_hybrid"
$cropsDir = Join-Path $figuresDir "crops"
$pageImagesDir = Join-Path $outputFolder "ocr/page_images"

New-Item -ItemType Directory -Force $inputDir, $figuresDir, $cropsDir, $pageImagesDir | Out-Null

Set-Content -Path (Join-Path $inputDir $pdfName) -Value "%PDF-1.4`n% v0.7.47 fixture`n" -Encoding ASCII
[IO.File]::WriteAllBytes((Join-Path $cropsDir "figure_001.png"), [byte[]](137,80,78,71,13,10,26,10))
[IO.File]::WriteAllBytes((Join-Path $pageImagesDir "page_0001.png"), [byte[]](137,80,78,71,13,10,26,10))

$manifest = [ordered]@{
  render_zoom = 3.0
  figure_crops = @(
    [ordered]@{
      number = "1"
      caption = "Existing crop"
      pdf_page = 1
      crop_method = "existing"
      relative_path = "crops/figure_001.png"
      crop_rect = @(10, 10, 120, 80)
      status = "accepted"
    }
  )
}

$sidecar = [ordered]@{
  marker = "VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR"
  candidate_count = 1
  crop_editor_manifest_overwritten = $false
  figures_gallery_overwritten = $false
  figure_crops = @(
    [ordered]@{
      number = "ocr-math-p001-001"
      caption = "OCR Math visual fallback candidate"
      pdf_page = 1
      crop_method = "ocr_math_visual_fallback_sidecar"
      relative_path = "../ocr/page_images/page_0001.png"
      crop_status = "needs_crop"
      import_status = "sidecar_only_not_in_crop_editor_manifest"
      source_candidate_id = "math-p001-001"
      source_line_number = 8
      source_file = "pages.md"
      risk_level = "high"
      severity = "high"
      rule_id = "OCR_MATH_SYMBOL"
      reason = "Math symbol may be damaged"
      original = "x -> x0"
      replacement = "x -> x_0"
      capture_source = "ocr/page_images/page_0001.png"
      capture_exists = $true
      study_reference_allowed = $true
    }
  )
}

$manifestPath = Join-Path $figuresDir "figures_manifest.hybrid.json"
$sidecarPath = Join-Path $figuresDir "ocr_math_visual_fallback_manifest.json"
$backupPath = Join-Path $figuresDir "figures_manifest.hybrid.json.v0.7.46.bak"
$importedPreviewPath = Join-Path $figuresDir "crops/ocr_math_math-p001-001.png"

$manifest | ConvertTo-Json -Depth 20 | Set-Content -Path $manifestPath -Encoding UTF8
$sidecar | ConvertTo-Json -Depth 20 | Set-Content -Path $sidecarPath -Encoding UTF8

$probe = @"
from pathlib import Path
import sys

sys.path.insert(0, str(Path("services/api").resolve()))
import crop_editor_app

crop_editor_app.INPUT_DIR = Path(r"$inputDir")
crop_editor_app.OUTPUT_DIR = Path(r"$outputRoot")

pdf_name = "$pdfName"
manifest_path = Path(r"$manifestPath")
backup_path = Path(r"$backupPath")
preview_path = Path(r"$importedPreviewPath")

before_html = crop_editor_app.editor(pdf=pdf_name).body.decode("utf-8")
required_html = [
    "Import OCR Math sidecar candidates",
    "/ocr-math-sidecar-import",
    "no auto-import",
    "creates backup",
    "skips duplicate source_candidate_id",
]
for item in required_html:
    if item not in before_html:
        raise SystemExit(f"Missing import button HTML: {item}")

import json
before_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if len(before_manifest.get("figure_crops", [])) != 1:
    raise SystemExit("GET render must not auto-import")

if backup_path.exists():
    raise SystemExit("GET render must not create backup")

response = crop_editor_app.ocr_math_sidecar_import(pdf_name=pdf_name)
location = response.headers.get("location", "")

required_location = [
    "ocr_math_import=PASS",
    "imported=1",
    "duplicates=0",
    "manifest_written=true",
]
for item in required_location:
    if item not in location:
        raise SystemExit(f"Missing redirect status after import: {item}")

after_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if len(after_manifest.get("figure_crops", [])) != 2:
    raise SystemExit("Explicit POST should import exactly one sidecar candidate")

if not backup_path.exists():
    raise SystemExit("Explicit POST should create backup")

if not preview_path.exists():
    raise SystemExit("Explicit POST should copy preview into crops")

imported = [item for item in after_manifest.get("figure_crops", []) if item.get("source_candidate_id") == "math-p001-001"]
if len(imported) != 1:
    raise SystemExit("Imported item missing or duplicated after first POST")

if imported[0].get("import_status") != "imported_from_sidecar_pending_owner_crop":
    raise SystemExit("Bad imported item status")

second = crop_editor_app.ocr_math_sidecar_import(pdf_name=pdf_name)
second_location = second.headers.get("location", "")

if "imported=0" not in second_location:
    raise SystemExit("Second POST should import zero items")

if "duplicates=1" not in second_location:
    raise SystemExit("Second POST should report one duplicate")

after_second = json.loads(manifest_path.read_text(encoding="utf-8"))
if len(after_second.get("figure_crops", [])) != 2:
    raise SystemExit("Second POST must not duplicate imported candidate")

status_html = crop_editor_app.editor(
    pdf=pdf_name,
    ocr_math_import="PASS",
    imported=1,
    duplicates=0,
    manifest_written="true",
).body.decode("utf-8")

for item in ["OCR Math sidecar import result", "Import PASS", "imported: 1", "duplicates skipped: 0"]:
    if item not in status_html:
        raise SystemExit(f"Missing import result HTML: {item}")
"@

$probePath = Join-Path $env:TEMP "voila-v0.7.47-crop-ui-import-button-probe.py"
Set-Content -Path $probePath -Value $probe -Encoding UTF8
python $probePath

$docText = Get-Content $doc -Raw
$requiredDoc = @("VOILA_V0_7_47_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_BUTTON_CROP_UI_OWNER_LOCAL_CHECK=PASS","There is no auto-import","button appears in HTML","No build","No ZIP","No share","No delivery","No distribution")
foreach ($item in $requiredDoc) { if ($docText -notlike "*$item*") { throw "Missing doc text: $item" } }

"VOILA_V0_7_47_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_BUTTON_CROP_UI_OWNER_LOCAL_CHECK=PASS"
"POLICY=explicit_owner_local_import_no_auto_import_no_build_no_zip_no_share_no_delivery_no_distribution"
