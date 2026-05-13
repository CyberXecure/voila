$ErrorActionPreference = "Continue"

$ProjectRoot = "D:\dev\projects\voila"
$ReportPath = Join-Path $ProjectRoot "audit\v0.1.4-language-runtime-audit.txt"

New-Item -ItemType Directory -Force (Split-Path -Parent $ReportPath) | Out-Null

function Write-Section {
    param([string]$Title)

    ""
    "============================================================"
    $Title
    "============================================================"
}

$lines = @()

$lines += Write-Section "Voila v0.1.4 Language Runtime Audit"
$lines += "Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")"
$lines += "ProjectRoot: $ProjectRoot"
$lines += ""

Push-Location $ProjectRoot

try {
    $lines += Write-Section "Git"
    $lines += "Branch: $(git branch --show-current)"
    $lines += "Status:"
    $status = git status --short
    if ($status) {
        $lines += $status
    }
    else {
        $lines += "clean"
    }

    $lines += ""
    $lines += "Tags:"
    $lines += git tag --list "v0.1.*"

    $lines += Write-Section "Requirements / Python dependencies"
    $req = Join-Path $ProjectRoot "services\api\requirements.txt"
    if (Test-Path $req) {
        $lines += "requirements.txt:"
        $lines += Get-Content $req
    }
    else {
        $lines += "requirements.txt not found"
    }

    $lines += Write-Section "LanguageTool references in source"

    $sourceFiles = Get-ChildItem $ProjectRoot -Recurse -File -Force |
        Where-Object {
            $_.FullName -notmatch "\\.git\\" -and
            $_.FullName -notmatch "\\.release-cache\\" -and
            $_.FullName -notmatch "\\.venv\\" -and
            $_.FullName -notmatch "\\venv\\" -and
            $_.FullName -notmatch "\\env\\" -and
            $_.FullName -notmatch "\\data\\" -and
            $_.FullName -notmatch "\\audit\\" -and
            $_.FullName -notmatch "\\python\\" -and
            $_.FullName -notmatch "\\__pycache__\\" -and
            $_.Extension -in @(".py", ".ps1", ".md", ".txt", ".js", ".css", ".html", ".json")
        }

    $matches = $sourceFiles |
        Select-String -Pattern "LanguageTool","languagetool","language_tool","/v2/check","LT_SERVER","JAVA_HOME","java.exe" -ErrorAction SilentlyContinue

    if ($matches) {
        foreach ($m in $matches) {
            $rel = $m.Path.Replace($ProjectRoot + "\", "")
            $lines += "${rel}:$($m.LineNumber): $($m.Line.Trim())"
        }
    }
    else {
        $lines += "No LanguageTool references found in source."
    }

    $lines += Write-Section "Java detection"

    $javaCandidates = @()

    $javaCmd = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($javaCmd) {
        $javaCandidates += $javaCmd.Source
    }

    $knownJavaRoots = @(
        "C:\Program Files\Eclipse Adoptium",
        "C:\Program Files\Java",
        "C:\Program Files\Microsoft",
        "C:\Program Files\Zulu",
        "C:\Program Files\Amazon Corretto",
        "$env:LOCALAPPDATA\Programs"
    )

    foreach ($root in $knownJavaRoots) {
        if (Test-Path $root) {
            $javaCandidates += Get-ChildItem $root -Recurse -Filter "java.exe" -File -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
        }
    }

    $javaCandidates = $javaCandidates | Select-Object -Unique

    if ($javaCandidates) {
        foreach ($java in $javaCandidates) {
            $lines += ""
            $lines += "JAVA: $java"
            try {
                $lines += (& $java -version 2>&1 | Out-String).Trim()
            }
            catch {
                $lines += "Could not run java -version: $($_.Exception.Message)"
            }
        }
    }
    else {
        $lines += "No java.exe found."
    }

    $lines += Write-Section "LanguageTool jar detection"

    $ltRoots = @(
        "$ProjectRoot\runtime",
        "$ProjectRoot\.languagetool",
        "$ProjectRoot\tools",
        "D:\dev\tools",
        "D:\dev\downloads",
        "$env:USERPROFILE\Downloads",
        "$env:LOCALAPPDATA\Programs",
        "C:\Program Files"
    ) | Select-Object -Unique

    $ltJars = @()

    foreach ($root in $ltRoots) {
        if (Test-Path $root) {
            $ltJars += Get-ChildItem $root -Recurse -Filter "languagetool-server.jar" -File -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty FullName
        }
    }

    $ltJars = $ltJars | Select-Object -Unique

    if ($ltJars) {
        foreach ($jar in $ltJars) {
            $dir = Split-Path -Parent $jar
            $lines += ""
            $lines += "LanguageTool server jar: $jar"
            $lines += "Folder: $dir"

            $nearby = Get-ChildItem $dir -File -ErrorAction SilentlyContinue |
                Select-Object Name, @{Name="SizeMB";Expression={[Math]::Round($_.Length / 1MB, 2)}} |
                Format-Table -AutoSize |
                Out-String

            $lines += $nearby.Trim()
        }
    }
    else {
        $lines += "No languagetool-server.jar found in common folders."
    }

    $lines += Write-Section "Recommended v0.1.4 approach"
    $lines += "- Include Java locally under app\runtime\java"
    $lines += "- Include LanguageTool locally under app\runtime\languagetool"
    $lines += "- Start LanguageTool server locally from Run-Voila.ps1 if jars exist"
    $lines += "- Set local env vars only; do not modify global PATH"
    $lines += "- Test with Java removed from PATH"
    $lines += "- Do not include n-gram data in v0.1.4"
}
finally {
    Pop-Location
}

$lines | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "Audit creat:"
Write-Host $ReportPath
Write-Host ""
Get-Content $ReportPath


