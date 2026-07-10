$ErrorActionPreference = "Stop"

$py = "services/api/ocr_math_visual_fallback_figures_bridge.py"
if (!(Test-Path $py)) { throw "Missing bridge generator: $py" }
$doc = "docs/dev/ocr-math-visual-fallback-candidates-to-figures-crop-no-build-no-zip-no-delivery.md"
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }

python -m py_compile $py

$fixture = Join-Path $env:TEMP "voila-v0.7.43-ocr-math-figures-bridge-fixture"
Remove-Item $fixture -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force (Join-Path $fixture "ocr/page_images") | Out-Null

Set-Content -Path (Join-Path $fixture "ocr/page_images/page_0001.png") -Value "fake-png-1" -Encoding UTF8
Set-Content -Path (Join-Path $fixture "ocr/page_images/page_0002.png") -Value "fake-png-2" -Encoding UTF8

$source = [ordered]@{
  marker = "VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST"
  visual_fallback_candidates = @(
    [ordered]@{
      candidate_id = "math-p001-001"
      page_number = 1
      line_number = 8
      source_file = "pages.md"
      rule_id = "OCR_MATH_SYMBOL"
      severity = "high"
      risk_level = "high"
      reason = "Math symbol may be damaged"
      original = "x -> x0"
      replacement = "x -> x_0"
      capture_source = "ocr/page_images/page_0001.png"
      capture_exists = $true
      crop_status = "needs_crop"
      figure_candidate = $true
      study_reference_allowed = $true
    },
    [ordered]@{
      candidate_id = "math-p002-002"
      page_number = 2
      line_number = 14
      source_file = "pages.md"
      rule_id = "OCR_MATH_LIMIT"
      severity = "medium"
      risk_level = "high"
      reason = "Limit expression may be damaged"
      original = "lim x"
      replacement = "lim_{x}"
      capture_source = "ocr/page_images/page_0002.png"
      capture_exists = $true
      crop_status = "needs_crop"
      figure_candidate = $true
      study_reference_allowed = $true
    }
  )
}

$source | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $fixture "visual_fallback_candidates.json") -Encoding UTF8

python $py --output-folder $fixture

$sidecarPath = Join-Path $fixture "figures_hybrid/ocr_math_visual_fallback_manifest.json"
if (!(Test-Path $sidecarPath)) { throw "Missing sidecar: $sidecarPath" }

$sidecar = Get-Content $sidecarPath -Raw | ConvertFrom-Json
if ($sidecar.marker -ne "VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR") { throw "Bad marker" }
if ($sidecar.candidate_count -ne 2) { throw "Bad candidate_count" }
if ($sidecar.candidate_count_with_existing_capture -ne 2) { throw "Bad capture count" }
if ($sidecar.crop_editor_manifest_overwritten -ne $false) { throw "Crop Editor manifest overwrite flag must be false" }
if ($sidecar.figures_gallery_overwritten -ne $false) { throw "Figures gallery overwrite flag must be false" }
if ($sidecar.figure_crops.Count -ne 2) { throw "Bad figure_crops count" }
if ($sidecar.figure_crops[0].pdf_page -ne 1) { throw "Bad first pdf_page" }
if ($sidecar.figure_crops[0].crop_method -ne "ocr_math_visual_fallback_sidecar") { throw "Bad crop_method" }
if ($sidecar.figure_crops[0].relative_path -ne "../ocr/page_images/page_0001.png") { throw "Bad relative_path" }
if ($sidecar.figure_crops[0].crop_status -ne "needs_crop") { throw "Bad crop_status" }
if ($sidecar.figure_crops[0].import_status -ne "sidecar_only_not_in_crop_editor_manifest") { throw "Bad import_status" }
if (Test-Path (Join-Path $fixture "figures_hybrid/figures_manifest.hybrid.json")) { throw "Must not create/overwrite figures_manifest.hybrid.json" }
if (Test-Path (Join-Path $fixture "figures_hybrid/figures_hybrid.html")) { throw "Must not create/overwrite figures_hybrid.html" }

git diff --name-only -- | ForEach-Object {
  if ($_ -ne "services/api/ocr_math_visual_fallback_figures_bridge.py" -and $_ -ne "scripts/dev/check-ocr-math-visual-fallback-candidates-to-figures-crop-no-build-no-zip-no-delivery.ps1" -and $_ -ne "docs/dev/ocr-math-visual-fallback-candidates-to-figures-crop-no-build-no-zip-no-delivery.md") {
    throw "Unexpected changed file: $_"
  }
}

"VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR_CHECK=PASS"
"POLICY=no_build_no_zip_no_share_no_delivery_no_distribution"
