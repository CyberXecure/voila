$ErrorActionPreference = "Stop"
$py = "services/api/ocr_math_visual_fallback_candidates.py"
$doc = "docs/dev/ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.md"
if (!(Test-Path $py)) { throw "Missing generator: $py" }
if (!(Test-Path $doc)) { throw "Missing doc: $doc" }
python -m py_compile $py
$docText = Get-Content $doc -Raw
$required = @("VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST_CHECK=PASS","visual_fallback_candidates.json","ocr/page_images/page_XXXX.png","No Study rewrite","No build")
foreach ($item in $required) { if ($docText -notlike "*$item*") { throw "Missing doc text: $item" } }
$pyText = Get-Content $py -Raw
$requiredPy = @("VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST","visual_fallback_candidates","ocr/page_images/page_XXXX.png","crop_status","needs_crop","study_reference_allowed","visual_fallback_candidates.json")
foreach ($item in $requiredPy) { if ($pyText -notlike "*$item*") { throw "Missing generator text: $item" } }
$changed = git diff --name-only --
$allowed = @("services/api/ocr_math_visual_fallback_candidates.py","docs/dev/ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.md","scripts/dev/check-ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.ps1")
foreach ($path in $changed) { if ($allowed -notcontains $path) { throw "Unexpected changed file: $path" } }
"VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST_CHECK=PASS"
"POLICY=no_build_no_zip_no_share_no_delivery_no_distribution"
