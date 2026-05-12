$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$OutDir = "D:\dev\releases"
$OutFile = Join-Path $OutDir "voila-runtime-audit-safe_$Stamp.txt"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Add-Line {
    param([string]$Text = "")
    Add-Content -Path $OutFile -Value $Text -Encoding UTF8
}

function Add-Section {
    param([string]$Title)
    Add-Line ""
    Add-Line "============================================================"
    Add-Line $Title
    Add-Line "============================================================"
}

function Run-Cmd {
    param(
        [string]$Title,
        [scriptblock]$Block
    )

    Add-Section $Title

    try {
        $result = & $Block 2>&1
        if ($result) {
            $result | ForEach-Object {
                Add-Line "$_"
            }
        }
        else {
            Add-Line "(no output)"
        }
    }
    catch {
        Add-Line "ERROR: $($_.Exception.Message)"
    }
}

Set-Location $ProjectRoot

if (Test-Path $OutFile) {
    Remove-Item $OutFile -Force
}

Add-Line "Voila Runtime Audit Safe"
Add-Line "Date: $(Get-Date)"
Add-Line "ProjectRoot: $ProjectRoot"

Run-Cmd "GIT STATUS" {
    git status --short
}

Run-Cmd "GIT BRANCH / TAGS" {
    git branch --show-current
    git tag --list
}

Run-Cmd "ROOT STRUCTURE" {
    Get-ChildItem $ProjectRoot -Force |
        Select-Object Mode, Length, LastWriteTime, Name |
        Format-Table -AutoSize
}

Run-Cmd "IMPORTANT FILES" {
    $files = @(
        "services\api\web_app.py",
        "services\api\lesson_tools.py",
        "services\api\study_questions.py",
        "services\api\i18n.py",
        "services\api\document_language.py",
        "services\api\static\ocr_review_monaco.js",
        "services\api\static\ocr_review_monaco.css",
        "scripts\dev\start-voila.ps1",
        "scripts\dev\stop-voila.ps1",
        "scripts\dev\install-ocr-languages.ps1",
        "docs\USAGE.md",
        "requirements.txt",
        "services\api\requirements.txt",
        "services\requirements.txt"
    )

    foreach ($file in $files) {
        $path = Join-Path $ProjectRoot $file

        if (Test-Path $path) {
            "[OK] $file"
        }
        else {
            "[MISS] $file"
        }
    }
}

Run-Cmd "PYTHON CHECK" {
    python --version
    python -c "import sys; print(sys.executable); print(sys.version)"
}

Run-Cmd "PIP CHECK" {
    python -m pip --version
}

Run-Cmd "SOURCE VENV CHECK" {
    $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        & $venvPython --version
        & $venvPython -m pip --version
    }
    else {
        "No source .venv found."
    }
}

Run-Cmd "REQUIREMENTS CANDIDATES" {
    $reqs = @(
        "requirements.txt",
        "services\api\requirements.txt",
        "services\requirements.txt"
    )

    foreach ($req in $reqs) {
        $path = Join-Path $ProjectRoot $req

        if (Test-Path $path) {
            ""
            "### $req"
            Get-Content $path
        }
        else {
            "[MISS] $req"
        }
    }
}

Run-Cmd "JAVA CHECK" {
    java -version
}

Run-Cmd "TESSERACT CHECK" {
    tesseract --version
}

Run-Cmd "TESSDATA CHECK" {
    $dirs = @(
        ".tessdata",
        "data\.tessdata",
        "services\api\.tessdata"
    )

    foreach ($dir in $dirs) {
        $path = Join-Path $ProjectRoot $dir

        if (Test-Path $path) {
            ""
            "### $dir"
            Get-ChildItem $path -File -ErrorAction SilentlyContinue |
                Select-Object Name, Length, LastWriteTime |
                Format-Table -AutoSize
        }
        else {
            "[MISS] $dir"
        }
    }
}

Run-Cmd "LANGUAGETOOL SEARCH SAFE" {
    $rootFiles = Get-ChildItem $ProjectRoot -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "languagetool|LanguageTool|LanguageToolServer|server\.jar" -or
            $_.Extension -eq ".jar"
        }

    if ($rootFiles) {
        "### Root files"
        $rootFiles | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
    }

    $candidateDirs = @(
        "tools",
        "vendor",
        "services",
        "scripts"
    )

    foreach ($relDir in $candidateDirs) {
        $dir = Join-Path $ProjectRoot $relDir

        if (Test-Path $dir) {
            ""
            "### Searching: $relDir"

            Get-ChildItem $dir -File -Recurse -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.FullName -notlike "*\.venv\*" -and
                    $_.FullName -notlike "*\node_modules\*" -and
                    $_.FullName -notlike "*\__pycache__\*" -and
                    (
                        $_.Name -match "languagetool|LanguageTool|LanguageToolServer|server\.jar" -or
                        $_.Extension -eq ".jar"
                    )
                } |
                Select-Object FullName, Length, LastWriteTime |
                Format-Table -AutoSize
        }
        else {
            "[MISS] $relDir"
        }
    }
}

Run-Cmd "OCR / PDF / DOCX IMPORT SEARCH SAFE" {
    $apiDir = Join-Path $ProjectRoot "services\api"

    if (Test-Path $apiDir) {
        Select-String `
            -Path "$apiDir\*.py" `
            -Pattern "pytesseract|tesseract|pdf|docx|fitz|pymupdf|ocr|LanguageTool|language_tool|language" `
            -CaseSensitive:$false |
            Select-Object Path, LineNumber, Line |
            Format-Table -Wrap
    }
    else {
        "Missing services\api"
    }
}

Run-Cmd "PORT CHECK 8787 / 8081" {
    foreach ($port in @(8787, 8081)) {
        $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

        if ($conn) {
            "Port $port is in use:"
            $conn | Select-Object LocalAddress, LocalPort, State, OwningProcess | Format-Table -AutoSize
        }
        else {
            "Port $port is free."
        }
    }
}

Run-Cmd "PROJECT SIZE BY TOP FOLDERS SAFE" {
    $rows = @()

    $folders = Get-ChildItem $ProjectRoot -Directory -Force |
        Where-Object {
            $_.Name -notin @(".git", ".venv", "node_modules", "__pycache__")
        }

    foreach ($folder in $folders) {
        $size = 0

        try {
            $files = Get-ChildItem $folder.FullName -Recurse -Force -File -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.FullName -notlike "*\.git\*" -and
                    $_.FullName -notlike "*\.venv\*" -and
                    $_.FullName -notlike "*\node_modules\*" -and
                    $_.FullName -notlike "*\__pycache__\*" -and
                    $_.FullName -notlike "*\data\trash\*"
                }

            $sum = $files | Measure-Object Length -Sum
            $size = $sum.Sum
        }
        catch {
            $size = 0
        }

        $rows += [PSCustomObject]@{
            Folder = $folder.FullName
            MB = [Math]::Round(($size / 1MB), 2)
        }
    }

    $rows |
        Sort-Object MB -Descending |
        Format-Table -AutoSize
}

Run-Cmd "EXCLUDED ITEMS CHECK SAFE" {
    $checkNames = @(".git", ".venv", "node_modules", "__pycache__")

    foreach ($name in $checkNames) {
        $path = Join-Path $ProjectRoot $name

        if (Test-Path $path) {
            "[FOUND ROOT] $name"
        }
        else {
            "[OK ROOT MISSING] $name"
        }
    }

    $trash = Join-Path $ProjectRoot "data\trash"

    if (Test-Path $trash) {
        "[FOUND] data\trash"
    }
    else {
        "[OK] data\trash missing"
    }
}

Add-Section "SUMMARY"
Add-Line "Audit safe completed."
Add-Line "Output file:"
Add-Line $OutFile

Write-Host ""
Write-Host "Audit safe creat:"
Write-Host $OutFile
