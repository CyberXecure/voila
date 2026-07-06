param(
    [switch]$SkipRuntimeSmoke
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

function Write-Pass { param([string]$Message) Write-Host "[PASS] $Message" }
function Assert-True { param([bool]$Condition, [string]$Message) if (-not $Condition) { throw "[FAIL] $Message" } Write-Pass $Message }
function Assert-Contains { param([string]$Text, [string]$Needle, [string]$Message) Assert-True ($Text.Contains($Needle)) $Message }

$Python = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
$WebAppPath = Join-Path $RepoRoot "services\api\web_app.py"
$DocPath = Join-Path $RepoRoot "docs\dev\v0.7.24-tester-ui-generation-navigation-and-ocr-math-reality-fix-no-delivery.md"

Assert-True (Test-Path $WebAppPath) "web_app.py exists"
Assert-True (Test-Path $DocPath) "v0.7.24 documentation exists"

$WebApp = Get-Content $WebAppPath -Raw -Encoding UTF8
$Doc = Get-Content $DocPath -Raw -Encoding UTF8

Assert-Contains $WebApp "def ensure_course_html_for_pdf" "HTML ensure helper exists"
Assert-Contains $WebApp "ensure_course_html_for_pdf(source_pdf)" "/generate calls HTML ensure helper"
Assert-Contains $WebApp "html_exporter.py" "HTML exporter is used"
Assert-Contains $WebApp "course_nav_injector.py" "course navigation injector is used"
Assert-Contains $WebApp "Generated · HTML pending" "homepage has truthful markdown-generated status"
Assert-Contains $WebApp "course.cleaned.md" "course.cleaned.md participates in generation detection"
Assert-Contains $WebApp '@app.get("/course-open")' "/course-open route exists"
Assert-Contains $WebApp 'href="/course-open?pdf=' "homepage/tools can open/rebuild course"
Assert-Contains $WebApp "OCR Math Diagnostic" "OCR Math Diagnostic is visible in Course Tools"
Assert-Contains $WebApp "ocr_math_report.md/json" "OCR Math missing-report explanation exists"
Assert-Contains $WebApp "voila-tester-flow-bottom-nav-v0724" "standalone bottom navigation injection exists"
Assert-Contains $WebApp "fixedCourseToolsLink" "fixed bottom nav includes Course Tools"
Assert-Contains $WebApp "fixedCourseOpenLink" "fixed bottom nav includes Open Course"
Assert-Contains $WebApp "fixedOcrReviewLink" "fixed bottom nav includes OCR Review"
Assert-Contains $WebApp "fixedExamPrepLink" "fixed bottom nav includes Exam Prep"
Assert-Contains $WebApp "Review OCR Text" "OCR Review navigation label exists"
Assert-Contains $WebApp 'href="/exam-prep"' "Exam Prep navigation exists"
Assert-Contains $WebApp 'href="/course-tools?pdf=' "Course Tools navigation exists"
Assert-Contains $Doc "NO_ZIP_NEW_UNTIL_PASS" "doc records no ZIP policy"
Assert-Contains $Doc "NO_SHARE" "doc records no share policy"
Assert-Contains $Doc "NO_DELIVERY" "doc records no delivery policy"
Assert-Contains $Doc "NO_PUBLIC_RELEASE" "doc records no public release policy"

Write-Host "`n--- Python compile ---"
& $Python -m py_compile ".\services\api\web_app.py" ".\services\api\html_exporter.py" ".\services\api\course_nav_injector.py"
Assert-True ($LASTEXITCODE -eq 0) "Python compile passed"

if (-not $SkipRuntimeSmoke) {
    Write-Host "`n--- extracted-package equivalent runtime smoke ---"
    $SmokePath = Join-Path $env:TEMP "voila-v0.7.24-extracted-package-ui-smoke.py"
    $Smoke = @"
from __future__ import annotations
import json, shutil, sys
from pathlib import Path
from urllib.parse import quote
repo = Path(sys.argv[1]).resolve()
api_dir = repo / "services" / "api"
sys.path.insert(0, str(api_dir))
from fastapi.testclient import TestClient
import web_app
pdf_name = "voila-v0.7.24-extracted-package-ui-fixture.pdf"
stem = Path(pdf_name).stem
pdf_path = web_app.INPUT_DIR / pdf_name
out_dir = web_app.OUTPUT_DIR / stem
def assert_true(condition: bool, message: str) -> None:
    if not condition: raise AssertionError(message)
    print("[PASS]", message)
def assert_contains(text: str, needle: str, message: str) -> None:
    assert_true(needle in text, message)
def write_fixture() -> None:
    web_app.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    web_app.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if out_dir.exists(): shutil.rmtree(out_dir)
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Count 0 >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "course.md").write_text("# Test course\n\n## Lesson 1\n\nGenerated Markdown exists.\n", encoding="utf-8")
    (out_dir / "course.cleaned.md").write_text("# Test course\n\n## Lesson 1\n\nGenerated Markdown exists.\n", encoding="utf-8")
    (out_dir / "pages.json").write_text(json.dumps({"pages": [{"page": 1, "text": "OCR page text"}]}, ensure_ascii=False), encoding="utf-8")
    (out_dir / "quiz.json").write_text(json.dumps({"questions": [{"question_id": "q1", "lesson_id": "L1", "question": "Question?", "answer": "Answer"}]}, ensure_ascii=False), encoding="utf-8")
    (out_dir / "flashcards.json").write_text(json.dumps([{"front": "Front", "back": "Back"}], ensure_ascii=False), encoding="utf-8")
    (out_dir / "glossary.json").write_text(json.dumps([{"term": "Term", "definition": "Definition"}], ensure_ascii=False), encoding="utf-8")
def cleanup() -> None:
    if out_dir.exists(): shutil.rmtree(out_dir)
    if pdf_path.exists(): pdf_path.unlink()
try:
    write_fixture()
    assert_true((out_dir / "course.cleaned.md").exists(), "fixture starts with course.cleaned.md")
    assert_true(not (out_dir / "course.cleaned.html").exists(), "fixture starts without course.cleaned.html")
    client = TestClient(web_app.app)
    home = client.get("/").text
    idx = home.find(pdf_name)
    assert_true(idx >= 0, "homepage includes extracted-package fixture PDF")
    card = home[idx: idx + 2600]
    assert_contains(card, "Generated · HTML pending", "homepage treats markdown-only course as generated")
    assert_contains(card, "/course-open?pdf=", "homepage exposes Open course through rebuild route")
    assert_contains(card, "/course-tools?pdf=", "homepage exposes Course Tools")
    assert_true("Not generated yet" not in card, "homepage does not show Not generated yet for markdown-only course")
    assert_true("Negenerat încă" not in card, "homepage does not show Negenerat încă for markdown-only course")
    tools = client.get("/course-tools", params={"pdf": pdf_name})
    assert_true(tools.status_code == 200, "Course Tools opens")
    assert_contains(tools.text, "OCR Math Diagnostic", "Course Tools shows OCR Math Diagnostic")
    assert_contains(tools.text, "ocr_math_report.md/json", "Course Tools explains missing OCR Math report")
    assert_contains(tools.text, "Instrumente curs", "Course Tools has top/bottom navigation")
    assert_contains(tools.text, "Deschide cursul", "Course Tools includes Open course action")
    assert_contains(tools.text, "OCR Review", "Course Tools includes OCR Review")
    assert_contains(tools.text, "Exam Prep", "Course Tools includes Exam Prep")
    report = client.get(f"/owner/ocr-math-report/{quote(stem)}/view")
    assert_true(report.status_code == 404, "OCR Math viewer truthfully reports missing report")
    assert_contains(report.text, "Raport diagnostic OCR Math indisponibil", "missing OCR Math report page explains unavailable report")
    opened = client.get("/course-open", params={"pdf": pdf_name}, follow_redirects=False)
    assert_true(opened.status_code in (302, 303, 307), "course-open redirects after rebuilding HTML")
    assert_true((out_dir / "course.cleaned.html").exists(), "course-open rebuilt course.cleaned.html")
    view = client.get("/view-course", params={"pdf": pdf_name})
    assert_true(view.status_code == 200, "view-course opens rebuilt HTML")
    assert_contains(view.text, "voila-tester-flow-bottom-nav-v0724", "course view has bottom navigation injection")
    exam = client.get("/exam-prep")
    assert_true(exam.status_code == 200, "Exam Prep opens")
    assert_contains(exam.text, "fixedExamPrepLink", "Exam Prep page includes fixed bottom nav")
finally:
    cleanup()
"@
    Set-Content -Path $SmokePath -Value $Smoke -Encoding utf8NoBOM
    & $Python $SmokePath $RepoRoot
    Assert-True ($LASTEXITCODE -eq 0) "extracted-package equivalent runtime smoke passed"
    Remove-Item $SmokePath -Force -ErrorAction SilentlyContinue
}

Write-Host "`n--- no delivery artifacts check ---"
$GitStatus = @(git status --porcelain)
$GitStatusText = [string]::Join("`n", $GitStatus)
Assert-True ($GitStatusText -notmatch '\.zip(\s|$)') "git status does not include a new ZIP"
Assert-True ($GitStatusText -notmatch 'OneDrive') "git status does not include OneDrive/share artifacts"
Assert-Contains $Doc "No tester delivery is allowed directly from v0.7.24." "doc blocks direct tester delivery"
Write-Host ""
Write-Host "VOILA_V0_7_24_TESTER_UI_GENERATION_NAVIGATION_AND_OCR_MATH_REALITY_FIX_NO_DELIVERY_CHECK=PASS"

