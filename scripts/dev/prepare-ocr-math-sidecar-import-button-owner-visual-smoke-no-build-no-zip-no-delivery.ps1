$ErrorActionPreference = "Stop"

$root = (Resolve-Path ".").Path
$stem = "v0748-ocr-math-sidecar-import-button-smoke"
$pdfName = "$stem.pdf"
$inputDir = Join-Path $root "data/input"
$outputDir = Join-Path $root "data/output/$stem"
$figuresDir = Join-Path $outputDir "figures_hybrid"
$cropsDir = Join-Path $figuresDir "crops"
$pageImagesDir = Join-Path $outputDir "ocr/page_images"

New-Item -ItemType Directory -Force $inputDir, $figuresDir, $cropsDir, $pageImagesDir | Out-Null

$pdfPath = Join-Path $inputDir $pdfName
Set-Content -Path $pdfPath -Value "%PDF-1.4`n% v0.7.48 owner visual smoke placeholder`n" -Encoding ASCII

$pngWriter = @"
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(r"$root")
stem = "$stem"
out = root / "data" / "output" / stem

targets = [
    (out / "figures_hybrid" / "crops" / "figure_001.png", "Existing hybrid crop BEFORE import"),
    (out / "ocr" / "page_images" / "page_0001.png", "OCR Math sidecar candidate to import"),
]

for path, label in targets:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (900, 260), (245, 236, 217))
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 880, 240), outline=(160, 110, 65), width=4)
    draw.text((50, 90), label, fill=(35, 30, 25))
    draw.text((50, 135), "v0.7.48 import button visual smoke", fill=(80, 70, 60))
    image.save(path)
    print(f"WROTE={path}")
"@

$pngWriterPath = Join-Path $env:TEMP "voila-v0.7.48-write-valid-pngs.py"
Set-Content -Path $pngWriterPath -Value $pngWriter -Encoding UTF8
python $pngWriterPath

$realManifest = [ordered]@{
  render_zoom = 3.0
  figure_crops = @(
    [ordered]@{
      number = "1"
      caption = "Existing hybrid figure crop before v0.7.48 import"
      pdf_page = 1
      crop_method = "fixture_existing_hybrid_crop"
      relative_path = "crops/figure_001.png"
      crop_rect = @(10, 10, 120, 80)
      status = "accepted"
    }
  )
}

$realManifest | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $figuresDir "figures_manifest.hybrid.json") -Encoding UTF8

$sidecar = [ordered]@{
  marker = "VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR"
  candidate_count = 1
  candidate_count_with_existing_capture = 1
  crop_editor_manifest_overwritten = $false
  figures_gallery_overwritten = $false
  figure_crops = @(
    [ordered]@{
      number = "ocr-math-p001-001"
      caption = "OCR Math visual fallback candidate: formula / symbol import smoke"
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

$sidecar | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $figuresDir "ocr_math_visual_fallback_manifest.json") -Encoding UTF8

$importedPreview = Join-Path $figuresDir "crops/ocr_math_math-p001-001.png"
Remove-Item $importedPreview -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $figuresDir "figures_manifest.hybrid.json.v0.7.46.bak") -Force -ErrorAction SilentlyContinue

"VOILA_V0_7_48_OWNER_VISUAL_SMOKE_FIXTURE_READY=PASS"
"PDF=$pdfName"
"CROP_EDITOR_URL=http://127.0.0.1:8790/?pdf=$pdfName"
"START_CROP_EDITOR=python -m uvicorn services.api.crop_editor_app:app --host 127.0.0.1 --port 8790"
"BEFORE_EXPECTED=OCR Math sidecar section visible; Import button visible; Hybrid figure crops count visually one existing crop"
"AFTER_EXPECTED=Import PASS; imported 1; duplicates 0; manifest_written true; Hybrid figure crops includes imported OCR Math crop"
"POLICY=explicit_owner_local_import_no_auto_import_no_build_no_zip_no_share_no_delivery_no_distribution"
