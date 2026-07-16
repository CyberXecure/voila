$ErrorActionPreference = "Stop"

Write-Host "v0.7.78 check: start"

$web = "services/api/web_app.py"
$doc = "docs/dev/owner-local-restore-ocr-math-report-hook-in-generate-no-build-no-zip-no-delivery.md"
$smoke = "D:\dev\tester-runs\v0778-restore-ocr-math-report-hook\V0.7.78-OCR-MATH-REPORT-HOOK-SMOKE.json"
$outDir = "D:\dev\projects\voila\data\output\03-pag-30-34-vectori-trigonometrie"
$md = Join-Path $outDir "ocr_math_report.md"
$json = Join-Path $outDir "ocr_math_report.json"

foreach ($p in @($web,$doc,$smoke,$md,$json)) {
  if (!(Test-Path $p)) { throw "Missing required file/evidence: $p" }
}

python -m py_compile $web services/api/ocr_math_report_hook.py services/api/ocr_math_report.py

$webText = Get-Content $web -Raw
foreach ($item in @(
  "build OCR Math report if enabled",
  "ocr_math_report_hook.py",
  "--output-folder",
  "--pdf-name",
  "--enable",
  "VOILA_ENABLE_OCR_MATH_REPORT_HOOK",
  "v0.7.78-generate-for-pdf"
)) {
  if ($webText -notlike "*$item*") { throw "web_app missing expected text: $item" }
}

$report = Get-Content $json -Raw | ConvertFrom-Json
if ($null -eq $report.total_suggestions) { throw "ocr_math_report.json missing total_suggestions" }
if ($null -eq $report.changed_line_count) { throw "ocr_math_report.json missing changed_line_count" }

$mdText = Get-Content $md -Raw
if ($mdText -notlike "*Voila OCR Math Diagnostic Report*") {
  throw "ocr_math_report.md missing title"
}

$smokeData = Get-Content $smoke -Raw | ConvertFrom-Json
if ($smokeData.VOILA_V0_7_78_OCR_MATH_REPORT_HOOK_IN_GENERATE_SMOKE -ne "PASS") { throw "smoke marker mismatch" }
if ($smokeData.OCR_MATH_REPORT_GENERATED -ne $true) { throw "OCR_MATH_REPORT_GENERATED mismatch" }
if ($smokeData.GENERATE_FOR_PDF_HOOK_RESTORED -ne $true) { throw "GENERATE_FOR_PDF_HOOK_RESTORED mismatch" }
if ($smokeData.BUILD_PERFORMED -ne $false) { throw "BUILD_PERFORMED mismatch" }
if ($smokeData.ZIP_CREATED -ne $false) { throw "ZIP_CREATED mismatch" }
if ($smokeData.SHARE_CREATED -ne $false) { throw "SHARE_CREATED mismatch" }
if ($smokeData.DELIVERY_PERFORMED -ne $false) { throw "DELIVERY_PERFORMED mismatch" }

$docText = (Get-Content $doc -Raw).Replace('`','')
foreach ($item in @(
  "VOILA_V0_7_78_OCR_MATH_REPORT_HOOK_IN_GENERATE_CHECK=PASS",
  "PASS_OCR_MATH_REPORT_HOOK_RESTORED_IN_GENERATE",
  "VOILA_V0_7_78_OCR_MATH_REPORT_HOOK_IN_GENERATE_SMOKE=PASS",
  "OCR_MATH_REPORT_GENERATED=True",
  "GENERATE_FOR_PDF_HOOK_RESTORED=True",
  "BUILD_PERFORMED=False",
  "ZIP_CREATED=False",
  "SHARE_CREATED=False",
  "DELIVERY_PERFORMED=False",
  "TESTER_READINESS=LOCAL_OCR_MATH_HOOK_PASS_NOT_PACKAGED"
)) {
  if ($docText -notlike "*$item*") { throw "Doc missing expected text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/owner-local-restore-ocr-math-report-hook-in-generate-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-restore-ocr-math-report-hook-in-generate-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) { throw "Unexpected changed/untracked file: $line" }
}

"VOILA_V0_7_78_OCR_MATH_REPORT_HOOK_IN_GENERATE_CHECK=PASS"
"OCR_MATH_REPORT_GENERATED=True"
"GENERATE_FOR_PDF_HOOK_RESTORED=True"
"BUILD_PERFORMED=False"
"ZIP_CREATED=False"
"SHARE_CREATED=False"
"DELIVERY_PERFORMED=False"
"TESTER_READINESS=LOCAL_OCR_MATH_HOOK_PASS_NOT_PACKAGED"
"POLICY=owner_local_restore_ocr_math_report_hook_in_generate_no_build_no_zip_no_share_no_delivery_no_distribution"
