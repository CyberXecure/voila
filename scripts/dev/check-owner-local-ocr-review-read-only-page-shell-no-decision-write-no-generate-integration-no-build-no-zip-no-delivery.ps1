$ErrorActionPreference = "Stop"

$webApp = "services/api/web_app.py"
$doc = "docs/dev/owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery.md"
$v0770Doc = "docs/dev/owner-local-ocr-review-guided-ui-contract-no-implementation-no-generate-integration-no-build-no-zip-no-delivery.md"
$htmlSmoke = "D:\dev\tester-runs\voila-v0.7.71-owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery\owner-ocr-review-read-only-route-smoke.html"

if (!(Test-Path $webApp)) { throw "Missing web_app.py" }
if (!(Test-Path $doc)) { throw "Missing v0.7.71 doc: $doc" }
if (!(Test-Path $v0770Doc)) { throw "Missing v0.7.70 baseline doc: $v0770Doc" }
if (!(Test-Path $htmlSmoke)) { throw "Missing v0.7.71 route smoke HTML evidence: $htmlSmoke" }

python -m py_compile $webApp

$text = Get-Content $webApp -Raw
$start = $text.IndexOf("# VOILA_V0_7_71_OWNER_LOCAL_OCR_REVIEW_READ_ONLY_PAGE_SHELL_START")
$end = $text.IndexOf("# VOILA_V0_7_71_OWNER_LOCAL_OCR_REVIEW_READ_ONLY_PAGE_SHELL_END")
if ($start -lt 0 -or $end -lt 0) { throw "Missing v0.7.71 markers in web_app.py" }

$block = $text.Substring($start, $end - $start)

foreach ($item in @(
  "/owner/ocr-review/{course_id}",
  "_voila_owner_ocr_review_read_only_shell",
  "ocr_review_queue.json",
  "ocr_review_decisions.json",
  "generation_should_wait_for_review",
  "all_required_decisions_resolved",
  "pending_decision_count",
  "resolved_decision_count",
  "data-testid=`"owner-ocr-review-read-only-shell`"",
  "Read-only v0.7.71",
  "nu există butoane de salvare",
  "nu se aplică patch",
  "nu cheamă /generate",
  "Pagina este read-only și nu creează artifacte lipsă"
)) {
  if ($block -notlike "*$item*") { throw "web_app.py v0.7.71 block missing expected text: $item" }
}

foreach ($bad in @(
  "@app.post",
  "write_text(",
  "open(",
  "Set-Content",
  "apply_decision_patch",
  "write_applied_decisions",
  "write_document_learning_pack",
  "write_ocr_review_decisions",
  "write_resolved_fixture",
  "RedirectResponse("
)) {
  if ($block -like "*$bad*") { throw "Forbidden write/integration text in v0.7.71 block: $bad" }
}

$html = Get-Content $htmlSmoke -Raw
foreach ($item in @(
  "data-testid=`"owner-ocr-review-read-only-shell`"",
  "Review items<strong>20</strong>",
  "Decizii total<strong>20</strong>",
  "Pending<strong>20</strong>",
  "Rezolvate<strong>0</strong>",
  "generation_should_wait_for_review=<code>True</code>",
  "all_required_decisions_resolved=<code>False</code>",
  "Această pagină este doar pentru citire în v0.7.71",
  "nu aplică patch",
  "nu cheamă /generate",
  "R001",
  "R020",
  "Decizie curentă:"
)) {
  if ($html -notlike "*$item*") { throw "HTML route smoke missing expected text: $item" }
}

$docText = Get-Content $doc -Raw
$docCheckText = $docText.Replace('`', '')
foreach ($item in @(
  "VOILA_V0_7_71_OCR_REVIEW_READ_ONLY_PAGE_SHELL_CHECK=PASS",
  "PASS_READ_ONLY_PAGE_SHELL",
  "/owner/ocr-review/{course_id}",
  "ocr_review_queue.json",
  "ocr_review_decisions.json",
  "VOILA_V0_7_71_DIRECT_ROUTE_SMOKE=PASS",
  "HTTP_STATUS=200",
  "REVIEW_ITEM_COUNT=20",
  "DECISION_COUNT=20",
  "PENDING_DECISION_COUNT=20",
  "RESOLVED_DECISION_COUNT=0",
  "GENERATION_SHOULD_WAIT_FOR_REVIEW=True",
  "ALL_REQUIRED_DECISIONS_RESOLVED=False",
  "READ_ONLY_NO_DECISION_WRITE=PASS",
  "It has no decision buttons.",
  "It has no forms.",
  "It has no POST route.",
  "It does not write ocr_review_decisions.json.",
  "It does not create ocr_review_decisions.applied.json.",
  "It does not call ocr_review_decision_apply.py.",
  "It does not rebuild document_learning_pack.json.",
  "Read-only page shell only.",
  "No decision write.",
  "No decision patch apply.",
  "No learning pack rebuild.",
  "No route POST.",
  "No /generate route change.",
  "No real user review performed.",
  "No build.",
  "No ZIP.",
  "No share.",
  "No delivery.",
  "No distribution.",
  "Tester readiness remains BLOCKED"
)) {
  if ($docCheckText -notlike "*$item*") { throw "Doc missing expected v0.7.71 text: $item" }
}

$statusLines = git status --short -uall
$allowed = @(
  "services/api/web_app.py",
  "docs/dev/owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery.md",
  "scripts/dev/check-owner-local-ocr-review-read-only-page-shell-no-decision-write-no-generate-integration-no-build-no-zip-no-delivery.ps1"
)

foreach ($line in $statusLines) {
  if ([string]::IsNullOrWhiteSpace($line)) { continue }
  $path = $line.Substring(3)
  if ($allowed -notcontains $path) {
    throw "Unexpected changed/untracked file in v0.7.71: $line"
  }
}

"VOILA_V0_7_71_OCR_REVIEW_READ_ONLY_PAGE_SHELL_CHECK=PASS"
"OCR_REVIEW_READ_ONLY_ROUTE=/owner/ocr-review/{course_id}"
"DIRECT_ROUTE_SMOKE=PASS"
"HTTP_STATUS=200"
"REAL_COURSE_REVIEW_ITEM_COUNT=20"
"REAL_COURSE_DECISION_COUNT=20"
"PENDING_DECISION_COUNT=20"
"RESOLVED_DECISION_COUNT=0"
"GENERATION_SHOULD_WAIT_FOR_REVIEW=True"
"ALL_REQUIRED_DECISIONS_RESOLVED=False"
"READ_ONLY_NO_DECISION_WRITE=PASS"
"DECISION_APPLY=NOT_CALLED"
"DOCUMENT_LEARNING_PACK_REBUILD=NOT_CALLED"
"GENERATE_INTEGRATION=NOT_CHANGED"
"ROUTE_POST=NOT_ADDED"
"TESTER_READINESS=BLOCKED"
"POLICY=owner_local_ocr_review_read_only_page_shell_only_no_decision_write_no_apply_patch_no_learning_pack_rebuild_no_generate_integration_no_build_no_zip_no_share_no_delivery_no_distribution"
