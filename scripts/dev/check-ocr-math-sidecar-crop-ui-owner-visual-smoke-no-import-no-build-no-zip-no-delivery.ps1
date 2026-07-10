$ErrorActionPreference = "Stop"

$prepare = "scripts/dev/prepare-ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.ps1"
$doc = "docs/dev/ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.md"
$cropEditor = "services/api/crop_editor_app.py"

if (!(Test-Path $prepare)) { throw "Missing prepare script: $prepare" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }
if (!(Test-Path $cropEditor)) { throw "Missing Crop Editor app: $cropEditor" }

python -m py_compile $cropEditor

$output = & ".\$prepare"
$text = ($output | Out-String)

$requiredOutput = @(
  "VOILA_V0_7_45_OWNER_VISUAL_SMOKE_FIXTURE_READY=PASS",
  "VISUAL_CONFIRMATION=PASS",
  "POLICY=no_import_no_build_no_zip_no_share_no_delivery_no_distribution"
)

foreach ($item in $requiredOutput) {
  if ($text -notlike "*$item*") {
    throw "Missing prepare output: $item"
  }
}

$stem = "v0745-ocr-math-sidecar-crop-ui-smoke"
$pdf = "data/input/$stem.pdf"
$out = "data/output/$stem"
$realManifestPath = "$out/figures_hybrid/figures_manifest.hybrid.json"
$sidecarPath = "$out/figures_hybrid/ocr_math_visual_fallback_manifest.json"
$cropPng = "$out/figures_hybrid/crops/figure_001.png"
$sidecarPng = "$out/ocr/page_images/page_0001.png"

foreach ($path in @($pdf, $realManifestPath, $sidecarPath, $cropPng, $sidecarPng)) {
  if (!(Test-Path $path)) {
    throw "Missing fixture file: $path"
  }
}

$realManifest = Get-Content $realManifestPath -Raw | ConvertFrom-Json
$sidecar = Get-Content $sidecarPath -Raw | ConvertFrom-Json

if ($realManifest.figure_crops.Count -ne 1) { throw "Bad real manifest crop count" }
if ($sidecar.figure_crops.Count -ne 1) { throw "Bad sidecar candidate count" }
if ($sidecar.figure_crops[0].import_status -ne "sidecar_only_not_in_crop_editor_manifest") { throw "Bad sidecar import status" }
if ($sidecar.crop_editor_manifest_overwritten -ne $false) { throw "Sidecar must record no Crop Editor manifest overwrite" }
if ($sidecar.figures_gallery_overwritten -ne $false) { throw "Sidecar must record no Figures gallery overwrite" }

$docText = Get-Content $doc -Raw
$requiredDoc = @(
  "VOILA_V0_7_45_OWNER_VISUAL_SMOKE_CHECK=PASS",
  "Manual visual result",
  "PASS",
  "No import",
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
  "scripts/dev/prepare-ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.ps1",
  "scripts/dev/check-ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.ps1",
  "docs/dev/ocr-math-sidecar-crop-ui-owner-visual-smoke-no-import-no-build-no-zip-no-delivery.md"
)

foreach ($path in $changed) {
  if ($allowed -notcontains $path) {
    throw "Unexpected changed file: $path"
  }
}

"VOILA_V0_7_45_OWNER_VISUAL_SMOKE_CHECK=PASS"
"POLICY=no_import_no_build_no_zip_no_share_no_delivery_no_distribution"
