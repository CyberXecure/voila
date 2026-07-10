$ErrorActionPreference = "Stop"

$py = "services/api/ocr_math_sidecar_crop_manifest_importer.py"
$doc = "docs/dev/ocr-math-sidecar-explicit-import-to-crop-manifest-owner-local-no-build-no-zip-no-delivery.md"
if (!(Test-Path $py)) { throw "Missing importer: $py" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }

python -m py_compile $py

$fixture = Join-Path $env:TEMP "voila-v0.7.46-sidecar-import-fixture"
Remove-Item $fixture -Recurse -Force -ErrorAction SilentlyContinue

$figuresDir = Join-Path $fixture "figures_hybrid"
$cropsDir = Join-Path $figuresDir "crops"
$pageImagesDir = Join-Path $fixture "ocr/page_images"

New-Item -ItemType Directory -Force $figuresDir, $cropsDir, $pageImagesDir | Out-Null

$pngBytes = [byte[]](137,80,78,71,13,10,26,10)
[IO.File]::WriteAllBytes((Join-Path $pageImagesDir "page_0001.png"), $pngBytes)

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

$dryRunOutput = python $py --output-folder $fixture
if (($dryRunOutput | Out-String) -notlike "*apply=false*") { throw "Dry-run output missing apply=false" }
if (($dryRunOutput | Out-String) -notlike "*manifest_written=false*") { throw "Dry-run must not write manifest" }

$afterDryRun = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($afterDryRun.figure_crops.Count -ne 1) { throw "Dry-run changed manifest" }
if (Test-Path $backupPath) { throw "Dry-run must not create backup" }
if (Test-Path $importedPreviewPath) { throw "Dry-run must not copy preview" }

$applyOutput = python $py --output-folder $fixture --apply
$applyText = $applyOutput | Out-String
if ($applyText -notlike "*apply=true*") { throw "Apply output missing apply=true" }
if ($applyText -notlike "*imported_count=1*") { throw "Apply did not import one item" }
if ($applyText -notlike "*manifest_written=true*") { throw "Apply did not write manifest" }

if (!(Test-Path $backupPath)) { throw "Apply must create backup" }
if (!(Test-Path $importedPreviewPath)) { throw "Apply must copy preview into crops" }

$afterApply = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($afterApply.figure_crops.Count -ne 2) { throw "Apply should leave exactly 2 crops" }

$imported = $afterApply.figure_crops | Where-Object { $_.source_candidate_id -eq "math-p001-001" }
if (!$imported) { throw "Imported item missing source_candidate_id" }
if ($imported.crop_method -ne "ocr_math_visual_fallback_imported_from_sidecar") { throw "Bad crop_method" }
if ($imported.import_status -ne "imported_from_sidecar_pending_owner_crop") { throw "Bad import_status" }
if ($imported.crop_rect_status -ne "default_full_page_pending_owner_crop") { throw "Bad crop_rect_status" }
if ($imported.relative_path -ne "crops/ocr_math_math-p001-001.png") { throw "Bad relative_path" }
if ($afterApply.ocr_math_sidecar_import.marker -ne "VOILA_V0_7_46_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_TO_CROP_MANIFEST_OWNER_LOCAL") { throw "Missing import marker" }

$secondApplyOutput = python $py --output-folder $fixture --apply
$secondText = $secondApplyOutput | Out-String
if ($secondText -notlike "*imported_count=0*") { throw "Second apply must import zero" }
if ($secondText -notlike "*skipped_duplicate_count=1*") { throw "Second apply must skip duplicate" }

$afterSecond = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($afterSecond.figure_crops.Count -ne 2) { throw "Second apply duplicated item" }

$docText = Get-Content $doc -Raw
$requiredDoc = @("VOILA_V0_7_46_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_TO_CROP_MANIFEST_OWNER_LOCAL_CHECK=PASS","Default mode is dry-run","creates backup","skips duplicates","No build","No ZIP","No share","No delivery","No distribution")
foreach ($item in $requiredDoc) { if ($docText -notlike "*$item*") { throw "Missing doc text: $item" } }

"VOILA_V0_7_46_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_TO_CROP_MANIFEST_OWNER_LOCAL_CHECK=PASS"
"POLICY=explicit_owner_local_import_no_build_no_zip_no_share_no_delivery_no_distribution"
