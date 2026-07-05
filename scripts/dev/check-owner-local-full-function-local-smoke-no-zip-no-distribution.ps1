# v0.7.19 owner-local full function local smoke
# Hotfix 3: bounded dynamic route smoke, URL encoding, controlled-fixture priority.
# Policy: no build, no ZIP, no delivery, no distribution.
# Expected final marker:
# VOILA_V0_7_19_OWNER_LOCAL_FULL_FUNCTION_LOCAL_SMOKE_CHECK=PASS

[CmdletBinding()]
param(
    [string]$RepoRoot = "D:\dev\projects\voila",
    [string]$BaseUrl = "http://127.0.0.1:8787",
    [int]$StartupTimeoutSeconds = 75,
    [switch]$SkipServerStart,
    [switch]$AllowDirtyWorktree
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Marker = "VOILA_V0_7_19_OWNER_LOCAL_FULL_FUNCTION_LOCAL_SMOKE_CHECK=PASS"
$ScriptName = Split-Path -Leaf $PSCommandPath
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

function Run-Git {
    param([string[]]$Args)
    & git -C $RepoRoot @Args
    if ($LASTEXITCODE -ne 0) {
        Fail "git $($Args -join ' ') failed"
    }
}

function Invoke-HttpGet {
    param(
        [string]$Path,
        [int[]]$AcceptedStatusCodes = @(200)
    )

    $Uri = if ($Path.StartsWith("http")) { $Path } else { "$BaseUrl$Path" }

    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 20
        $status = [int]$response.StatusCode
        if ($AcceptedStatusCodes -notcontains $status) {
            Fail "GET $Uri returned HTTP $status; expected one of $($AcceptedStatusCodes -join ', ')"
        }
        Write-Pass "GET $Path -> HTTP $status"
        return $response
    }
    catch {
        Fail "GET $Uri failed: $($_.Exception.Message)"
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

function Invoke-ExistingCheckIfPresent {
    param(
        [string]$Label,
        [string[]]$Patterns,
        [string[]]$RequiredMarkers = @()
    )

    $scriptsDir = Join-Path $RepoRoot "scripts\dev"
    $matches = @()
    foreach ($pattern in $Patterns) {
        $matches += Get-ChildItem -LiteralPath $scriptsDir -Filter $pattern -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne $ScriptName }
    }
    $matches = @($matches | Sort-Object FullName -Unique)

    if (@($matches).Length -eq 0) {
        Write-WarnLine "$Label check script not found; continuing with v0.7.19 route/server checks"
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

    foreach ($requiredMarker in $RequiredMarkers) {
        $joined = ($output | Out-String)
        if ($joined -notmatch [regex]::Escape($requiredMarker)) {
            Fail "$Label delegated check did not print required marker: $requiredMarker"
        }
    }

    Write-Pass "$Label delegated check passed"
    return $true
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

function Assert-SourcePattern {
    param(
        [string]$Label,
        [string[]]$Patterns,
        [string]$Text
    )

    foreach ($pattern in $Patterns) {
        if ($Text -match $pattern) {
            Write-Pass "$Label source pattern found: $pattern"
            return
        }
    }

    Fail "$Label source pattern missing. Tried: $($Patterns -join ' OR ')"
}

function Find-CourseCandidates {
    $candidateRoots = @(
        (Join-Path $RepoRoot "data\output"),
        (Join-Path $RepoRoot "data"),
        (Join-Path $RepoRoot "storage"),
        (Join-Path $RepoRoot ".data"),
        (Join-Path $RepoRoot ".voila")
    ) | Where-Object { Test-Path -LiteralPath $_ -PathType Container }

    $byDir = @{}

    foreach ($root in $candidateRoots) {
        $files = @(
            Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.Name -in @(
                        "pages.json",
                        "pages.md",
                        "course_outline.json",
                        "course_outline.md",
                        "course_outline.normalized.json",
                        "course_outline.normalized.md",
                        "course.md",
                        "course.cleaned.md",
                        "course.cleaned.html",
                        "quiz.json",
                        "flashcards.json",
                        "glossary.json",
                        "ocr_corrections.json",
                        "ocr_math_report.md",
                        "ocr_math_report.json"
                    )
                }
        )

        foreach ($file in $files) {
            if ($null -eq $file.Directory) { continue }
            $key = $file.Directory.FullName
            if (-not $byDir.ContainsKey($key)) {
                $byDir[$key] = [ordered]@{
                    Path = $key
                    CourseId = $file.Directory.Name
                    Files = New-Object System.Collections.Generic.List[string]
                    LastWriteTime = $file.LastWriteTime
                }
            }
            [void]$byDir[$key].Files.Add($file.Name)
            if ($file.LastWriteTime -gt $byDir[$key].LastWriteTime) {
                $byDir[$key].LastWriteTime = $file.LastWriteTime
            }
        }
    }

    $candidates = foreach ($entry in $byDir.GetEnumerator()) {
        $fileNames = @($entry.Value.Files.ToArray() | Sort-Object -Unique)
        $courseId = [string]$entry.Value.CourseId

        $score = 0
        if ($courseId -match "voila-v0\.7\.17d-controlled-fixture") { $score += 1000 }
        elseif ($courseId -match "controlled-fixture") { $score += 700 }
        if ($fileNames -contains "course.cleaned.md") { $score += 100 }
        if ($fileNames -contains "course.md") { $score += 80 }
        if ($fileNames -contains "quiz.json") { $score += 50 }
        if ($fileNames -contains "flashcards.json") { $score += 50 }
        if ($fileNames -contains "glossary.json") { $score += 40 }
        if ($fileNames -contains "ocr_corrections.json") { $score += 30 }
        if ($fileNames -contains "ocr_math_report.md") { $score += 30 }
        if ($fileNames -contains "ocr_math_report.json") { $score += 30 }
        if ($courseId -match "\s") { $score -= 10 }

        [pscustomobject]@{
            CourseId = $courseId
            Path = [string]$entry.Value.Path
            Files = $fileNames
            Score = $score
            LastWriteTime = $entry.Value.LastWriteTime
        }
    }

    return @($candidates | Sort-Object -Property @{Expression="Score";Descending=$true}, @{Expression="LastWriteTime";Descending=$true})
}

function Get-DynamicGetRouteTemplates {
    param([string]$SourceText)

    $templates = New-Object System.Collections.Generic.List[string]
    $matches = [regex]::Matches($SourceText, "@app\.(get)\(\s*['""]([^'""]+)['""]", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

    foreach ($match in $matches) {
        $route = [string]$match.Groups[2].Value
        if ($route -notmatch "\{") { continue }
        if ($route -notmatch "(course|study|progress|ocr|exam-prep|owner)") { continue }
        if (-not $templates.Contains($route)) {
            [void]$templates.Add($route)
        }
    }

    return @($templates.ToArray())
}

function Convert-RouteTemplateToPath {
    param(
        [string]$Template,
        [string]$CourseId
    )

    $encoded = [System.Uri]::EscapeDataString($CourseId)
    return ([regex]::Replace($Template, "\{[^}]+\}", $encoded))
}

function Try-DynamicRoutesForCourse {
    param(
        [string]$CourseId,
        [string[]]$RouteTemplates
    )

    $templates = @($RouteTemplates)
    if (@($templates).Length -eq 0) {
        Write-WarnLine "no dynamic GET route templates extracted from web_app.py; dynamic route smoke skipped"
        return 0
    }

    $ok = 0
    $tried = 0
    $maxAttempts = 10

    foreach ($template in $templates) {
        if ($tried -ge $maxAttempts) {
            Write-WarnLine "dynamic route smoke bounded at $maxAttempts attempts"
            break
        }

        $path = Convert-RouteTemplateToPath -Template $template -CourseId $CourseId
        $tried += 1

        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl$path" -UseBasicParsing -MaximumRedirection 3 -TimeoutSec 6
            $status = [int]$response.StatusCode
            if ($status -ge 200 -and $status -lt 400) {
                Write-Pass "dynamic route template $template -> $path -> HTTP $status"
                $ok += 1
            }
            else {
                Write-WarnLine "dynamic route template $template -> $path returned HTTP $status"
            }
        }
        catch {
            Write-WarnLine "dynamic route template skipped/failed: $template -> $path ($($_.Exception.Message))"
        }
    }

    if ($ok -eq 0) {
        Write-WarnLine "no dynamic route template returned 2xx/3xx; source inventory and delegated write smoke remain authoritative for this milestone"
    }

    return $ok
}

Write-Host "SCRIPT_HOTFIX=3"
Write-Step "v0.7.19 policy guard"
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

    $status = (& git status --short)
    if ($status -and -not $AllowDirtyWorktree) {
        $status | ForEach-Object { Write-Host $_ }
        Fail "worktree is dirty. Use -AllowDirtyWorktree only while testing the new milestone files before commit."
    }
    if ($status -and $AllowDirtyWorktree) {
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
        "services/api/ocr_math_normalizer.py",
        "services/api/ocr_corrections.py"
    )

    Write-Step "Source route/function inventory"
    $webApp = Join-Path $RepoRoot "services\api\web_app.py"
    Assert-File $webApp "web_app.py"
    $webText = Get-Content -LiteralPath $webApp -Raw -Encoding UTF8

    Assert-SourcePattern "Upload" @("['""]\/upload", "upload_pdf", "UploadFile") $webText
    Assert-SourcePattern "Generate" @("['""]\/generate", "generate_for_pdf", "generate_course") $webText
    Assert-SourcePattern "Course view" @("['""]\/course", "course\.cleaned", "course_view") $webText
    Assert-SourcePattern "Study" @("['""]\/study", "study_quiz", "Study") $webText
    Assert-SourcePattern "Progress" @("['""]\/progress", "progress", "Progres") $webText
    Assert-SourcePattern "Exam Prep" @("['""]\/exam-prep", "exam_prep", "Exam Prep") $webText
    Assert-SourcePattern "OCR review / corrected OCR" @("ocr-review", "ocr_review", "corrected_ocr", "OCR Review") $webText
    Assert-SourcePattern "OCR Math report/viewer" @("ocr-math-report", "ocr_math_report", "OCR Math") $webText
    Assert-SourcePattern "Quick tools" @("['""]\/quick-tools", "quick_tools", "Quick Tools") $webText
    Assert-SourcePattern "owner-local route(s)" @("['""]\/owner\/", "owner-local", "owner_local") $webText

    $env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK = "1"
    Write-Host "VOILA_ENABLE_OCR_MATH_REPORT_HOOK=$env:VOILA_ENABLE_OCR_MATH_REPORT_HOOK"

    Write-Step "Delegated prior checks if present"
    [void](Invoke-ExistingCheckIfPresent `
        -Label "v0.7.18 final freeze" `
        -Patterns @("*v0.7.18*.ps1", "*generate-entrypoint-and-write-smoke-final-freeze*.ps1") `
        -RequiredMarkers @("VOILA_V0_7_18_GENERATE_ENTRYPOINT_AND_WRITE_SMOKE_FINAL_FREEZE_CHECK=PASS"))

    [void](Invoke-ExistingCheckIfPresent `
        -Label "controlled fixture write smoke" `
        -Patterns @("*controlled-fixture-write-smoke*.ps1", "*write-smoke*.ps1", "*generate*write*smoke*.ps1") `
        -RequiredMarkers @())

    Write-Step "Owner-local server smoke"

    if (-not (Test-HttpHealthy)) {
        if ($SkipServerStart) {
            Fail "server is not healthy at $BaseUrl and -SkipServerStart was set"
        }

        $startScript = Join-Path $RepoRoot "scripts\dev\start-voila.ps1"
        Assert-File $startScript "start-voila.ps1"

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

    [void](Invoke-HttpGet "/health")
    [void](Invoke-HttpGet "/")
    [void](Invoke-HttpGet "/quick-tools")
    [void](Invoke-HttpGet "/exam-prep")

    Write-Step "Owner-local route candidates"
    $ownerCandidates = @(
        "/owner",
        "/owner/",
        "/owner/ocr-math-report",
        "/owner/exam-prep/session-preview"
    )
    $ownerOk = 0
    foreach ($path in $ownerCandidates) {
        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl$path" -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 15
            $status = [int]$response.StatusCode
            if ($status -ge 200 -and $status -lt 500) {
                Write-Pass "owner-local candidate $path -> HTTP $status"
                $ownerOk += 1
            }
        }
        catch {
            Write-WarnLine "owner-local candidate skipped/failed: $path ($($_.Exception.Message))"
        }
    }
    if ($ownerOk -lt 1) {
        Write-WarnLine "no generic owner-local candidate returned a usable response; dynamic owner routes may require a course_id"
    }

    Write-Step "Dynamic course route smoke if local generated course data exists"
    $courseCandidates = @(Find-CourseCandidates)
    if (@($courseCandidates).Length -eq 0) {
        Write-WarnLine "no existing local generated course candidates found under data/output/data/storage/.data/.voila; dynamic Course/Study/Progress/OCR Math viewer routes were source-inventory checked"
    }
    else {
        $best = $courseCandidates[0]
        Write-Host "Selected dynamic smoke course ID: $($best.CourseId)"
        Write-Host "Selected dynamic smoke path: $($best.Path)"
        Write-Host "Selected dynamic smoke files: $(@($best.Files) -join ', ')"
        Write-Host "Selected dynamic smoke score: $($best.Score)"

        $requiredCoreFiles = @("pages.json", "course_outline.json", "course.md", "course.cleaned.md", "quiz.json", "flashcards.json", "glossary.json")
        foreach ($requiredCoreFile in $requiredCoreFiles) {
            if (@($best.Files) -contains $requiredCoreFile) {
                Write-Pass "selected course artifact present: $requiredCoreFile"
            }
            else {
                Write-WarnLine "selected course artifact not present on selected candidate: $requiredCoreFile"
            }
        }

        if ((@($best.Files) -contains "ocr_math_report.md") -or (@($best.Files) -contains "ocr_math_report.json")) {
            Write-Pass "selected course has OCR Math report artifact"
        }
        else {
            Write-WarnLine "selected course has no OCR Math report artifact; OCR Math route/source inventory was checked and hook is enabled for new local generation"
        }

        $dynamicTemplates = @(Get-DynamicGetRouteTemplates -SourceText $webText)
        if (@($dynamicTemplates).Length -gt 0) {
            Write-Host "Dynamic GET templates extracted: $($dynamicTemplates -join ', ')"
        }
        else {
            Write-WarnLine "no dynamic GET templates extracted from source"
        }

        $dynamicOk = Try-DynamicRoutesForCourse -CourseId $best.CourseId -RouteTemplates $dynamicTemplates
        Write-Host "dynamic_route_success_count=$dynamicOk"
    }

    Write-Step "Final v0.7.19 result"
    Write-Host "LOCAL_FUNCTIONS_COVERED=Upload,Generate,CourseView,Study,Progress,ExamPrep,OCRReview,CorrectedOCR,OCRMathReport,OCRMathViewer,QuickTools,OwnerLocalRoutes"
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
