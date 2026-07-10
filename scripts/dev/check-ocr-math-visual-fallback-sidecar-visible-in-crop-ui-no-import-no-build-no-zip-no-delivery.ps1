$ErrorActionPreference = "Stop"

$target = "services/api/crop_editor_app.py"
$doc = "docs/dev/ocr-math-visual-fallback-sidecar-visible-in-crop-ui-no-import-no-build-no-zip-no-delivery.md"
if (!(Test-Path $target)) { throw "Missing Crop Editor app: $target" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }

python -m py_compile $target

$text = Get-Content $target -Raw

$required = @(
  "VOILA_V0_7_44_OCR_MATH_VISUAL_FALLBACK_SIDECAR_VISIBLE_IN_CROP_UI",
  "ocr_math_visual_fallback_manifest.json",
  "load_ocr_math_sidecar",
  "build_ocr_math_sidecar_section",
  "ocr_math_sidecar_image_url",
  "OCR Math visual fallback candidates",
  "Read-only sidecar",
  "no import into Crop Editor manifest",
  "Hybrid figure crops"
)

foreach ($item in $required) {
  if ($text -notlike "*$item*") {
    throw "Missing required Crop UI text: $item"
  }
}

if ($text -notlike '*figures_manifest.hybrid.json*') {
  throw "Crop Editor real manifest reference missing"
}

if ($text -notlike '*def save_manifest*') {
  throw "Existing save_manifest function missing"
}

if ($text -notlike '*def load_manifest*') {
  throw "Existing load_manifest function missing"
}

$fixture = Join-Path $env:TEMP "voila-v0.7.44-crop-ui-readonly-fixture"
Remove-Item $fixture -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force (Join-Path $fixture "demo/figures_hybrid") | Out-Null

$sidecar = [ordered]@{
  marker = "VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR"
  candidate_count = 1
  figure_crops = @(
    [ordered]@{
      number = "ocr-math-p001-001"
      caption = "OCR Math visual fallback candidate: formula may be damaged"
      pdf_page = 1
      risk_level = "high"
      crop_status = "needs_crop"
      import_status = "sidecar_only_not_in_crop_editor_manifest"
      source_candidate_id = "math-p001-001"
      source_line_number = 8
      source_file = "pages.md"
      relative_path = "../ocr/page_images/page_0001.png"
      capture_source = "ocr/page_images/page_0001.png"
      capture_exists = $true
      study_reference_allowed = $true
    }
  )
}

$sidecar | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $fixture "demo/figures_hybrid/ocr_math_visual_fallback_manifest.json") -Encoding UTF8

$probe = @"
from pathlib import Path
import sys

sys.path.insert(0, str(Path("services/api").resolve()))
import crop_editor_app

crop_editor_app.OUTPUT_DIR = Path(r"$fixture")
html = crop_editor_app.build_ocr_math_sidecar_section(Path("demo.pdf"))

required = [
    "OCR Math visual fallback candidates",
    "Read-only sidecar",
    "no import into Crop Editor manifest",
    "ocr-math-p001-001",
    "sidecar_only_not_in_crop_editor_manifest",
    "../ocr/page_images/page_0001.png",
]

for item in required:
    if item not in html:
        raise SystemExit(f"Missing rendered sidecar HTML text: {item}")

real_manifest = Path(r"$fixture") / "demo" / "figures_hybrid" / "figures_manifest.hybrid.json"
gallery = Path(r"$fixture") / "demo" / "figures_hybrid" / "figures_hybrid.html"

if real_manifest.exists():
    raise SystemExit("Must not create/overwrite figures_manifest.hybrid.json")

if gallery.exists():
    raise SystemExit("Must not create/overwrite figures_hybrid.html")
"@

$probePath = Join-Path $env:TEMP "voila-v0.7.44-crop-ui-readonly-probe.py"
Set-Content -Path $probePath -Value $probe -Encoding UTF8
python $probePath

$changed = git diff --name-only --
$allowed = @(
  "services/api/crop_editor_app.py",
  "scripts/dev/check-ocr-math-visual-fallback-sidecar-visible-in-crop-ui-no-import-no-build-no-zip-no-delivery.ps1",
  "docs/dev/ocr-math-visual-fallback-sidecar-visible-in-crop-ui-no-import-no-build-no-zip-no-delivery.md"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_44_OCR_MATH_VISUAL_FALLBACK_SIDECAR_VISIBLE_IN_CROP_UI_CHECK=PASS"
"POLICY=no_import_no_build_no_zip_no_share_no_delivery_no_distribution"
