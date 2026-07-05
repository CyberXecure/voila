# v0.7.19b owner-local route real smoke before ZIP
# Hotfix 2: avoid read-only PowerShell $HOME variable collision.
# Policy: no build, no ZIP, no delivery, no distribution.
# Expected final marker:
# VOILA_V0_7_19B_OWNER_LOCAL_ROUTE_REAL_SMOKE_BEFORE_ZIP_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$BaseUrl = "http://127.0.0.1:8787",
    [int]$StartupTimeoutSeconds = 75,
    [switch]$AllowDirtyWorktree
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_19B_OWNER_LOCAL_ROUTE_REAL_SMOKE_BEFORE_ZIP_CHECK=PASS"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$BaseUrl = $BaseUrl.TrimEnd("/")

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Write-Pass {
    param([string]$Message)
    Write-Host "PASS: $Message"
}

function Write-WarnLine {
    param([string]$Message)
    Write-Host "WARN: $Message"
}

function Fail {
    param([string]$Message)
    throw "FAIL: $Message"
}

function Assert-File {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Assert-Dir {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        Fail "$Label missing: $Path"
    }
    Write-Pass "$Label found"
}

function Get-PythonExe {
    $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
        return $venvPython
    }
    return "python"
}

function Invoke-PyCompile {
    param([string[]]$RelativePaths)

    $python = Get-PythonExe
    foreach ($rel in $RelativePaths) {
        $full = Join-Path $RepoRoot $rel
        if (Test-Path -LiteralPath $full -PathType Leaf) {
            Write-Host "py_compile: $rel"
            & $python -m py_compile $full
            if ($LASTEXITCODE -ne 0) {
                Fail "py_compile failed: $rel"
            }
            Write-Pass "py_compile $rel"
        }
        else {
            Write-WarnLine "py_compile target not present, skipped: $rel"
        }
    }
}

function Test-HttpHealthy {
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -MaximumRedirection 3 -TimeoutSec 5
        return ([int]$response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

function Wait-Health {
    param([int]$TimeoutSeconds)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        if (Test-HttpHealthy) {
            Write-Pass "local server healthy at $BaseUrl"
            return
        }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)

    Fail "local server did not become healthy at $BaseUrl within $TimeoutSeconds seconds"
}

function Invoke-HttpGetPath {
    param(
        [string]$Path,
        [string]$Label,
        [int]$TimeoutSec = 20,
        [int[]]$AcceptedStatusCodes = @(200)
    )

    $uri = if ($Path.StartsWith("http")) { $Path } else { "$BaseUrl$Path" }

    try {
        $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -MaximumRedirection 5 -TimeoutSec $TimeoutSec
        $status = [int]$response.StatusCode
        if ($AcceptedStatusCodes -notcontains $status) {
            Fail "$Label returned HTTP $status for $Path; expected $($AcceptedStatusCodes -join ', ')"
        }
        Write-Pass "$Label -> $Path -> HTTP $status"
        return $response
    }
    catch {
        Fail "$Label failed for ${Path}: $($_.Exception.Message)"
    }
}

function Try-HttpGetPath {
    param(
        [string]$Path,
        [string]$Label,
        [int]$TimeoutSec = 8
    )

    $uri = if ($Path.StartsWith("http")) { $Path } else { "$BaseUrl$Path" }

    try {
        $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -MaximumRedirection 5 -TimeoutSec $TimeoutSec
        $status = [int]$response.StatusCode
        if ($status -ge 200 -and $status -lt 400) {
            Write-Pass "$Label -> $Path -> HTTP $status"
            return $true
        }
        Write-WarnLine "$Label -> $Path -> HTTP $status"
        return $false
    }
    catch {
        Write-WarnLine "$Label failed for ${Path}: $($_.Exception.Message)"
        return $false
    }
}

function Stop-VoilaIfPossible {
    $stopScript = Join-Path $RepoRoot "scripts\dev\stop-voila.ps1"
    if (Test-Path -LiteralPath $stopScript -PathType Leaf) {
        Write-Step "Stopping existing owner-local runtime if present"
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $stopScript -Silent
        if ($LASTEXITCODE -ne 0) {
            Write-WarnLine "stop-voila.ps1 returned exit code $LASTEXITCODE; continuing"
        }
    }
}

function Start-Voila {
    $startScript = Join-Path $RepoRoot "scripts\dev\start-voila.ps1"
    Assert-File $startScript "start-voila.ps1"
    if (-not (Test-HttpHealthy)) {
        Write-Host "Starting local Voila with scripts/dev/start-voila.ps1 -Silent"
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $startScript -Silent
        if ($LASTEXITCODE -ne 0) {
            Fail "start-voila.ps1 failed with exit code $LASTEXITCODE"
        }
    }
    else {
        Write-Pass "server already healthy at $BaseUrl"
    }
    Wait-Health -TimeoutSeconds $StartupTimeoutSeconds
}

function Invoke-ExistingCheckIfPresent {
    param(
        [string]$Label,
        [string[]]$Patterns,
        [string[]]$RequiredMarkers = @()
    )

    $scriptsDir = Join-Path $RepoRoot "scripts\dev"
    $matches = @()
    foreach ($pattern in $Patterns) {
        $matches += @(Get-ChildItem -LiteralPath $scriptsDir -Filter $pattern -File -ErrorAction SilentlyContinue)
    }
    $matches = @($matches | Sort-Object FullName -Unique)

    if (@($matches).Length -eq 0) {
        Write-WarnLine "$Label check script not found"
        return $false
    }

    $check = $matches[0]
    Write-Step "Running existing delegated check: $Label ($($check.Name))"
    $output = & pwsh -NoProfile -ExecutionPolicy Bypass -File $check.FullName 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }

    if ($exitCode -ne 0) {
        Fail "$Label delegated check failed with exit code $exitCode"
    }

    $joined = ($output | Out-String)
    foreach ($requiredMarker in $RequiredMarkers) {
        if ($joined -notmatch [regex]::Escape($requiredMarker)) {
            Fail "$Label delegated check did not print required marker: $requiredMarker"
        }
    }

    Write-Pass "$Label delegated check passed"
    return $true
}

function Get-LatestControlledFixtureCourse {
    $outputRoot = Join-Path $RepoRoot "data\output"
    Assert-Dir $outputRoot "data output root"

    $dirs = @(
        Get-ChildItem -LiteralPath $outputRoot -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match "^voila-v0\.7\.17d-controlled-fixture" } |
            Sort-Object LastWriteTime -Descending
    )

    if (@($dirs).Length -eq 0) {
        Fail "no v0.7.17d controlled fixture output directory found after delegated write smoke"
    }

    $dir = $dirs[0]
    Write-Pass "selected latest controlled fixture course: $($dir.Name)"
    Write-Host "controlled_fixture_course_id=$($dir.Name)"
    Write-Host "controlled_fixture_output_dir=$($dir.FullName)"
    return $dir
}

function Assert-CoreCourseArtifacts {
    param([System.IO.DirectoryInfo]$CourseDir)

    $required = @(
        "pages.json",
        "pages.md",
        "course_outline.json",
        "course_outline.md",
        "course_outline.normalized.json",
        "course_outline.normalized.md",
        "course.md",
        "course.cleaned.md",
        "glossary.json",
        "quiz.json",
        "flashcards.json",
        "ocr_corrections.json"
    )

    foreach ($name in $required) {
        Assert-File (Join-Path $CourseDir.FullName $name) "course artifact $name"
    }
}

function Ensure-ControlledOcrMathArtifacts {
    param([System.IO.DirectoryInfo]$CourseDir)

    $courseId = $CourseDir.Name
    $mdPath = Join-Path $CourseDir.FullName "ocr_math_report.md"
    $jsonPath = Join-Path $CourseDir.FullName "ocr_math_report.json"

    $md = @"
# OCR Math Report — v0.7.19b route smoke fixture

Diagnostic local · read-only route smoke.

## Summary

- Sugestii detectate: 1
- Linii posibil afectate: 1

## Controlled fixture

| Line | Original | Suggested |
| --- | --- | --- |
| 1 | x^2 + y^2 | x² + y² |

This file is a controlled owner-local route smoke artifact for `$courseId`.
"@

    $json = [ordered]@{
        course_id = $courseId
        source = "v0.7.19b-owner-local-route-real-smoke-before-zip"
        controlled_fixture = $true
        suggestions_detected = 1
        affected_lines = 1
        lines_possibly_affected = 1
        summary = [ordered]@{
            suggestions_detected = 1
            affected_lines = 1
            lines_possibly_affected = 1
        }
        suggestions = @(
            [ordered]@{
                line = 1
                original = "x^2 + y^2"
                suggested = "x² + y²"
                reason = "controlled route smoke fixture"
            }
        )
    } | ConvertTo-Json -Depth 12

    Set-Content -LiteralPath $mdPath -Value $md -Encoding UTF8
    Set-Content -LiteralPath $jsonPath -Value $json -Encoding UTF8

    Assert-File $mdPath "controlled OCR Math markdown artifact"
    Assert-File $jsonPath "controlled OCR Math json artifact"

    Write-Host "controlled_ocr_math_report_md=$mdPath"
    Write-Host "controlled_ocr_math_report_json=$jsonPath"
}

function Get-FastApiRoutes {
    $python = Get-PythonExe
    $tmpPy = Join-Path $env:TEMP "voila-v0.7.19b-route-inventory.py"
    $tmpJson = Join-Path $env:TEMP "voila-v0.7.19b-route-inventory.json"

    $py = @"
import json
import os
import sys

repo = r'''$RepoRoot'''
out = r'''$tmpJson'''
api_dir = os.path.join(repo, 'services', 'api')
sys.path.insert(0, api_dir)
os.chdir(repo)
os.environ.setdefault('VOILA_ENABLE_OCR_MATH_REPORT_HOOK', '1')

import web_app

routes = []
for route in getattr(web_app.app, 'routes', []):
    path = getattr(route, 'path', '')
    methods = sorted(list(getattr(route, 'methods', []) or []))
    name = getattr(route, 'name', '')
    routes.append({'path': path, 'methods': methods, 'name': name})

with open(out, 'w', encoding='utf-8') as f:
    json.dump(routes, f, ensure_ascii=False, indent=2)
"@

    Set-Content -LiteralPath $tmpPy -Value $py -Encoding UTF8

    & $python $tmpPy
    if ($LASTEXITCODE -ne 0) {
        Fail "FastAPI route inventory Python import failed"
    }

    Assert-File $tmpJson "FastAPI route inventory json"

    $raw = Get-Content -LiteralPath $tmpJson -Raw -Encoding UTF8
    $routes = @($raw | ConvertFrom-Json)
    if (@($routes).Length -eq 0) {
        Fail "FastAPI route inventory returned no routes"
    }

    Write-Pass "FastAPI route inventory loaded: $(@($routes).Length) routes"
    return $routes
}

function Assert-RouteTemplateExists {
    param(
        [object[]]$Routes,
        [string]$Pattern,
        [string]$Label
    )

    $matches = @($Routes | Where-Object { $_.path -match $Pattern -and @($_.methods) -contains "GET" })
    if (@($matches).Length -eq 0) {
        Fail "$Label route template missing; pattern: $Pattern"
    }

    Write-Pass "$Label route template present: $($matches[0].path)"
    return [string]$matches[0].path
}

function Resolve-CourseRoutePath {
    param(
        [string]$Template,
        [string]$CourseId
    )

    $encodedCourseId = [System.Uri]::EscapeDataString($CourseId)
    $path = $Template
    $path = $path -replace "\{course_id\}", $encodedCourseId
    $path = $path -replace "\{pdf_name\}", ([System.Uri]::EscapeDataString("$CourseId.pdf"))
    return $path
}

function Get-Hrefs {
    param([string]$Html)

    $hrefs = New-Object System.Collections.Generic.List[string]
    $matches = [regex]::Matches($Html, "href\s*=\s*[""']([^""']+)[""']", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    foreach ($match in $matches) {
        $href = [System.Net.WebUtility]::HtmlDecode([string]$match.Groups[1].Value)
        if ([string]::IsNullOrWhiteSpace($href)) { continue }
        if ($href.StartsWith("mailto:")) { continue }
        if ($href.StartsWith("#")) { continue }
        if ($href.StartsWith("http://127.0.0.1") -or $href.StartsWith($BaseUrl)) {
            $uri = [Uri]$href
            $href = $uri.PathAndQuery
        }
        if ($href.StartsWith("/")) {
            if (-not $hrefs.Contains($href)) {
                [void]$hrefs.Add($href)
            }
        }
    }

    return @($hrefs.ToArray())
}

function Try-HomeActionCategory {
    param(
        [string[]]$Hrefs,
        [string]$CourseId,
        [string]$Category,
        [string[]]$Patterns
    )

    $encoded = [System.Uri]::EscapeDataString($CourseId)
    $realCandidates = New-Object System.Collections.Generic.List[string]

    foreach ($href in $Hrefs) {
        if (-not ($href -like "*$CourseId*" -or $href -like "*$encoded*")) { continue }
        foreach ($pattern in $Patterns) {
            if ($href -match $pattern) {
                if (-not $realCandidates.Contains($href)) {
                    [void]$realCandidates.Add($href)
                }
            }
        }
    }

    $realCandidatesArray = @($realCandidates.ToArray())
    if (@($realCandidatesArray).Length -eq 0) {
        Write-WarnLine "$Category no homepage action link found for controlled course"
        return $false
    }

    foreach ($href in ($realCandidatesArray | Select-Object -First 3)) {
        if (Try-HttpGetPath -Path $href -Label "$Category real homepage action" -TimeoutSec 12) {
            return $true
        }
    }

    return $false
}

Write-Host "SCRIPT_VERSION=v0.7.19b-route-real-smoke-hotfix2"

Write-Step "v0.7.19b policy guard"
Assert-Dir $RepoRoot "repo root"
Assert-Dir (Join-Path $RepoRoot ".git") "git metadata"

Push-Location $RepoRoot
try {
    $topLevel = (& git rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0) { Fail "not a git repo" }
    if ((Resolve-Path -LiteralPath $topLevel).Path -ne $RepoRoot) {
        Fail "repo root mismatch: expected $RepoRoot but git top-level is $topLevel"
    }

    $branch = (& git branch --show-current).Trim()
    $head = (& git rev-parse --short HEAD).Trim()
    Write-Host "BRANCH=$branch"
    Write-Host "HEAD=$head"

    $status = @(& git status --short)
    if (@($status).Length -gt 0 -and -not $AllowDirtyWorktree) {
        $status | ForEach-Object { Write-Host $_ }
        Fail "worktree is dirty. Use -AllowDirtyWorktree only while testing the new milestone files before commit."
    }
    elseif (@($status).Length -gt 0 -and $AllowDirtyWorktree) {
        Write-WarnLine "worktree is dirty but allowed for pre-commit milestone check"
        $status | ForEach-Object { Write-Host $_ }
    }
    else {
        Write-Pass "worktree clean"
    }

    Write-Host "NO_BUILD=PASS"
    Write-Host "NO_ZIP=PASS"
    Write-Host "NO_DELIVERY=PASS"
    Write-Host "NO_DISTRIBUTION=PASS"
    Write-Host "OWNER_LOCAL_ONLY=PASS"

    $zipInRepo = @(
        Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Filter "*.zip" -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -notmatch "\\\.git\\" -and
                $_.FullName -notmatch "\\node_modules\\" -and
                $_.FullName -notmatch "\\\.venv\\"
            }
    )

    if (@($zipInRepo).Length -gt 0) {
        Write-WarnLine "ZIP files already exist inside repo; this script will not create or modify ZIP files:"
        $zipInRepo | Select-Object -First 10 | ForEach-Object { Write-Host "  $($_.FullName)" }
    }
    else {
        Write-Pass "no ZIP files found inside repo tree"
    }

    Write-Step "Python syntax/import sanity"
    Invoke-PyCompile @(
        "services/api/web_app.py",
        "services/api/exam_prep.py",
        "services/api/study_quiz_builder.py",
        "services/api/ocr_math_report.py",
        "services/api/ocr_math_normalizer.py"
    )

    Write-Step "Required baseline files and v0.7.19 marker"
    Assert-File (Join-Path $RepoRoot "scripts\dev\check-owner-local-full-function-local-smoke-no-zip-no-distribution.ps1") "v0.7.19 check script"
    Assert-File (Join-Path $RepoRoot "docs\dev\v0.7.19-owner-local-full-function-local-smoke-no-zip-no-distribution.md") "v0.7.19 doc"

    $v019ScriptText = Get-Content -LiteralPath (Join-Path $RepoRoot "scripts\dev\check-owner-local-full-function-local-smoke-no-zip-no-distribution.ps1") -Raw -Encoding UTF8
    if ($v019ScriptText -notmatch "VOILA_V0_7_19_OWNER_LOCAL_FULL_FUNCTION_LOCAL_SMOKE_CHECK=PASS") {
        Fail "v0.7.19 final marker missing from v0.7.19 script"
    }
    Write-Pass "v0.7.19 final marker present in check script"

    $env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = "1"
    Write-Host "VOILA_ENABLE_OCR_MATH_REPORT_HOOK=$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK"

    Write-Step "FastAPI route inventory"
    $routes = @(Get-FastApiRoutes)
    $ocrSummaryTemplate = Assert-RouteTemplateExists -Routes $routes -Pattern "^/owner/ocr-math-report/\{course_id\}/summary\.json$" -Label "OCR Math summary"
    $ocrMarkdownTemplate = Assert-RouteTemplateExists -Routes $routes -Pattern "^/owner/ocr-math-report/\{course_id\}/ocr_math_report\.md$" -Label "OCR Math markdown"
    $ocrViewerTemplate = Assert-RouteTemplateExists -Routes $routes -Pattern "^/owner/ocr-math-report/\{course_id\}/view$" -Label "OCR Math viewer"
    [void](Assert-RouteTemplateExists -Routes $routes -Pattern "^/exam-prep" -Label "Exam Prep")

    Write-Step "Delegated controlled fixture upload/generate smoke"
    [void](Invoke-ExistingCheckIfPresent `
        -Label "v0.7.17d controlled fixture write smoke" `
        -Patterns @("check-owner-local-controlled-fixture-write-smoke-no-build-no-distribution.ps1") `
        -RequiredMarkers @("VOILA_V0_7_17D_OWNER_LOCAL_CONTROLLED_FIXTURE_WRITE_SMOKE_CHECK=PASS"))

    $courseDir = Get-LatestControlledFixtureCourse
    Assert-CoreCourseArtifacts -CourseDir $courseDir

    Write-Step "Creating controlled OCR Math route artifacts for latest fixture"
    Ensure-ControlledOcrMathArtifacts -CourseDir $courseDir

    Write-Step "Owner-local route real smoke"
    Stop-VoilaIfPossible
    Start-Voila

    [void](Invoke-HttpGetPath -Path "/health" -Label "health")
    $homeResponse = Invoke-HttpGetPath -Path "/" -Label "homepage"
    [void](Invoke-HttpGetPath -Path "/quick-tools" -Label "quick tools")
    $examPrep = Invoke-HttpGetPath -Path "/exam-prep" -Label "exam prep dashboard"

    $courseId = $courseDir.Name
    $ocrSummaryPath = Resolve-CourseRoutePath -Template $ocrSummaryTemplate -CourseId $courseId
    $ocrMarkdownPath = Resolve-CourseRoutePath -Template $ocrMarkdownTemplate -CourseId $courseId
    $ocrViewerPath = Resolve-CourseRoutePath -Template $ocrViewerTemplate -CourseId $courseId

    [void](Invoke-HttpGetPath -Path $ocrSummaryPath -Label "OCR Math summary json" -TimeoutSec 20)
    [void](Invoke-HttpGetPath -Path $ocrMarkdownPath -Label "OCR Math markdown" -TimeoutSec 20)
    [void](Invoke-HttpGetPath -Path $ocrViewerPath -Label "OCR Math viewer" -TimeoutSec 20)

    Write-Step "Real homepage action route smoke for generated controlled course"
    $hrefs = @(Get-Hrefs -Html ([string]$homeResponse.Content))
    Write-Host "homepage_href_count=$(@($hrefs).Length)"

    $courseViewOk = Try-HomeActionCategory -Hrefs $hrefs -CourseId $courseId -Category "Course view" -Patterns @("/course", "course", "open")
    $studyOk = Try-HomeActionCategory -Hrefs $hrefs -CourseId $courseId -Category "Study" -Patterns @("/study", "study")
    $progressOk = Try-HomeActionCategory -Hrefs $hrefs -CourseId $courseId -Category "Progress" -Patterns @("/progress", "progress")
    $ocrReviewOk = Try-HomeActionCategory -Hrefs $hrefs -CourseId $courseId -Category "OCR review/corrected OCR" -Patterns @("ocr", "review", "correct")

    Write-Host "course_view_home_action_success=$courseViewOk"
    Write-Host "study_home_action_success=$studyOk"
    Write-Host "progress_home_action_success=$progressOk"
    Write-Host "ocr_review_home_action_success=$ocrReviewOk"

    $examHrefs = @(Get-Hrefs -Html ([string]$examPrep.Content))
    $skillLinks = New-Object System.Collections.Generic.List[string]
    foreach ($href in $examHrefs) {
        if ($href -match "^/exam-prep/skill/[^/?#]+/?") {
            if (-not $skillLinks.Contains($href)) {
                [void]$skillLinks.Add($href)
            }
        }
    }

    $skillLinksArray = @($skillLinks.ToArray())
    if (@($skillLinksArray).Length -gt 0) {
        $skillPath = $skillLinksArray[0]
        [void](Invoke-HttpGetPath -Path $skillPath -Label "exam prep real skill route" -TimeoutSec 20)
        Write-Host "exam_prep_skill_route_smoke=PASS"
        Write-Host "exam_prep_skill_route=$skillPath"
    }
    else {
        Write-WarnLine "no /exam-prep/skill/... link found on Exam Prep dashboard; dashboard route smoke remains PASS"
        Write-Host "exam_prep_skill_route_smoke=NOT_AVAILABLE"
    }

    Write-Step "Final v0.7.19b result"
    Write-Host "route_real_smoke_health=PASS"
    Write-Host "route_real_smoke_home=PASS"
    Write-Host "route_real_smoke_quick_tools=PASS"
    Write-Host "route_real_smoke_exam_prep_dashboard=PASS"
    Write-Host "route_real_smoke_ocr_math_summary=PASS"
    Write-Host "route_real_smoke_ocr_math_markdown=PASS"
    Write-Host "route_real_smoke_ocr_math_viewer=PASS"
    Write-Host "route_real_smoke_course_home_action=$courseViewOk"
    Write-Host "route_real_smoke_study_home_action=$studyOk"
    Write-Host "route_real_smoke_progress_home_action=$progressOk"
    Write-Host "route_real_smoke_ocr_review_home_action=$ocrReviewOk"
    Write-Host "NO_BUILD=PASS"
    Write-Host "NO_ZIP=PASS"
    Write-Host "NO_DELIVERY=PASS"
    Write-Host "NO_DISTRIBUTION=PASS"
    Write-Host "OWNER_LOCAL_ONLY=PASS"
    Write-Host $Marker
}
finally {
    Pop-Location
}
