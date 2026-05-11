# Voila! — Usage

Voila! este o aplicație locală pentru transformarea manualelor PDF în conținut de studiu, cu suport pentru OCR review, corecții manuale, lecții, Study Mode și verificare LanguageTool.

## Start aplicație

```powershell
cd D:\dev\projects\voila

.\scripts\dev\start-voila.ps1
```

Aplicația rulează local la:

```text
http://127.0.0.1:8787/
```

LanguageTool rulează local la:

```text
http://127.0.0.1:8081/v2/check
```

## Stop aplicație

```powershell
cd D:\dev\projects\voila

.\scripts\dev\stop-voila.ps1
```

## Instalare limbi OCR

Fișierele `.traineddata` nu sunt versionate în Git. Se instalează local:

```powershell
cd D:\dev\projects\voila

.\scripts\dev\install-ocr-languages.ps1
```

Limbile suportate pentru OCR/documente:

```text
Română, English, Français, Deutsch, Русский, Italiano, Español, Português
```

## OCR Review

Deschide OCR Review pentru o pagină:

```text
/review-ocr-corrected?pdf=NUME_MANUAL.pdf&page=NUMAR_PAGINA
```

Exemplu:

```text
http://127.0.0.1:8787/review-ocr-corrected?pdf=Manualul%20Instalatiilor%20Electrice.pdf&page=41
```

În OCR Review:

- alegi limba interfeței
- alegi limba documentului
- alegi OCR normal / OCR 2 coloane / OCR 3 coloane
- `Rulează OCR pagină` generează text pentru pagina curentă
- `Verifică text` rulează LanguageTool
- sugestiile apar într-un panou dedicat
- `Salvează` păstrează corecția paginii

## OCR coverage report

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\report-ocr-coverage.py
```

Raportul se generează în:

```text
data\output\_reports\ocr_coverage_report.json
data\output\_reports\ocr_coverage_report.md
```

## OCR pentru o singură pagină

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\run-ocr-page.py `
  --pdf "Manualul Instalatiilor Electrice" `
  --page 41 `
  --lang auto `
  --psm 6 `
  --zoom 3.0 `
  --columns 3
```

Parametri utili:

```text
--lang auto        folosește limba documentului setată în aplicație
--columns 0       OCR normal
--columns 2       OCR pe 2 coloane
--columns 3       OCR pe 3 coloane
--zoom 3.0        zoom OCR uzual
--psm 6           mod Tesseract uzual pentru pagini structurate
```

## Lessons

Flux recomandat:

```text
Course Tools → Lessons → Deschide lecția → Studiază lecția
```

URL direct:

```text
/lessons?pdf=NUME_MANUAL.pdf
```

Exemplu:

```text
http://127.0.0.1:8787/lessons?pdf=Manual-de-Supravietuire.pdf
```

În Lessons poți:

- vedea lista lecțiilor
- deschide o lecție pentru citire
- porni Study Mode doar pentru lecția respectivă

## Lesson view

Deschide o lecție direct:

```text
/lesson?pdf=NUME_MANUAL.pdf&lesson_id=ID_LECTIE
```

Exemplu:

```text
http://127.0.0.1:8787/lesson?pdf=Manual-de-Supravietuire.pdf&lesson_id=L003
```

Pagina lecției afișează:

- titlul lecției
- paginile sursă, dacă sunt disponibile
- textul sursă disponibil
- buton pentru Study pe lecția respectivă

## Study Mode

Study Mode general:

```text
/study?pdf=NUME_MANUAL.pdf
```

Study pentru o lecție:

```text
/study-lesson?pdf=NUME_MANUAL.pdf&lesson_id=ID_LECTIE
```

Întrebările afișate sunt construite la runtime în funcție de limba documentului. `quiz.study.json` rămâne sursă semantică/metadate, nu sursa finală a textului afișat.

Exemplu:

```text
quiz.study.json:
What technical point does the source state about Partea IV?

Study Mode afișează:
Ce idee importantă susține sursa despre „Partea IV”?
```

## Limba interfeței vs limba documentului

Voila separă două setări:

```text
Limba interfeței:
meniuri, butoane, etichete UI

Limba documentului:
OCR, LanguageTool, întrebări de studiu
```

Exemple corecte:

```text
Interfață: Română
Document: English
LanguageTool: en-US
Întrebări: English
```

```text
Interfață: English
Document: Română
LanguageTool: ro-RO
Întrebări: Română
```

## LanguageTool

LanguageTool trebuie să ruleze local pentru verificarea textului:

```text
http://127.0.0.1:8081/v2/check
```

Test rapid:

```powershell
curl.exe -X POST `
  -d "language=ro-RO" `
  -d "text=Acesta este un text cu greseli si functionare incorecta." `
  http://127.0.0.1:8081/v2/check
```

Dacă LanguageTool nu răspunde, pornește aplicația cu:

```powershell
cd D:\dev\projects\voila

.\scripts\dev\start-voila.ps1
```

## Smoke test Monaco + LanguageTool

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\smoke-monaco-static-lt.py
```

Rezultat dorit:

```text
review status: 200
has monaco js: True
has monaco css: True
js status: 200
css status: 200
lt status: 200
```

## Verificări compile

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe -m py_compile .\services\api\web_app.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\lesson_tools.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\study_questions.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\i18n.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\document_language.py
```

## Git checkpoint

```powershell
cd D:\dev\projects\voila

git status --short

.\.venv\Scripts\python.exe -m py_compile .\services\api\web_app.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\lesson_tools.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\study_questions.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\i18n.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\document_language.py

git add .
git commit -m "chore: update Voila workflow"
```

## Backup ZIP checkpoint

```powershell
cd D:\dev\projects\voila

$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$backupRoot = "D:\dev\backups"
$stageDir = Join-Path $backupRoot "voila_checkpoint_clean_$stamp"
$zipPath = Join-Path $backupRoot "voila_checkpoint_clean_$stamp.zip"

New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null

$excludeDirs = @(
  "\.git\",
  "\.venv\",
  "\node_modules\",
  "\__pycache__\",
  "\data\trash\"
)

Get-ChildItem . -Recurse -Force -File |
  Where-Object {
    $full = $_.FullName

    foreach ($dir in $excludeDirs) {
      if ($full -like "*$dir*") {
        return $false
      }
    }

    if ($_.Name -like "*.pyc") {
      return $false
    }

    return $true
  } |
  ForEach-Object {
    $relative = Resolve-Path $_.FullName -Relative
    $relative = $relative.TrimStart(".\")
    $target = Join-Path $stageDir $relative
    $targetDir = Split-Path -Parent $target

    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    Copy-Item $_.FullName $target -Force
  }

Compress-Archive `
  -Path "$stageDir\*" `
  -DestinationPath $zipPath `
  -Force

Remove-Item $stageDir -Recurse -Force

Write-Host "Backup curat creat:"
Write-Host $zipPath
```

## Verificare ZIP checkpoint

```powershell
$latest = Get-ChildItem "D:\dev\backups" -Filter "voila_checkpoint_clean_*.zip" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($latest.FullName)

Write-Host "ZIP:" $latest.FullName
Write-Host "Entries:" $zip.Entries.Count

$important = @(
  "services/api/web_app.py",
  "services/api/lesson_tools.py",
  "services/api/study_questions.py",
  "services/api/i18n.py",
  "services/api/document_language.py",
  "services/api/static/ocr_review_monaco.js",
  "services/api/static/ocr_review_monaco.css",
  "scripts/dev/start-voila.ps1",
  "scripts/dev/stop-voila.ps1",
  "scripts/dev/install-ocr-languages.ps1",
  "docs/USAGE.md"
)

foreach ($item in $important) {
  $found = $zip.Entries | Where-Object {
    $_.FullName.Replace("\", "/") -eq $item
  } | Select-Object -First 1

  if ($found) {
    Write-Host "OK  " $item
  } else {
    Write-Host "MISS" $item
  }
}

Write-Host ""
Write-Host "=== Excluderi ==="

foreach ($pattern in @(".git/", ".venv/", "node_modules/", "__pycache__/", "data/trash/")) {
  $bad = $zip.Entries | Where-Object {
    $_.FullName.Replace("\", "/") -like "*$pattern*"
  } | Select-Object -First 3

  if ($bad) {
    Write-Host "WARN găsit:" $pattern
    $bad | ForEach-Object { Write-Host " -" $_.FullName }
  } else {
    Write-Host "OK exclus:" $pattern
  }
}

$zip.Dispose()
```

Ținta finală:

```text
OK docs/USAGE.md
OK exclus: data/trash/
working tree clean
```
