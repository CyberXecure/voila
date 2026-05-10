# Voila! — Usage

Voila! este o aplicație locală pentru transformarea manualelor PDF în conținut de studiu, cu suport pentru OCR review, corecții manuale și verificare LanguageTool.

## 1. Start aplicație

Pornește Voila + LanguageTool:

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

## 2. Stop aplicație

```powershell
cd D:\dev\projects\voila

.\scripts\dev\stop-voila.ps1
```

## 3. OCR Review

Deschide pagina de review OCR pentru un manual și o pagină:

```text
/review-ocr-corrected?pdf=NUME_MANUAL.pdf&page=NUMAR_PAGINA
```

Exemplu:

```text
http://127.0.0.1:8787/review-ocr-corrected?pdf=Manualul%20Instalatiilor%20Electrice.pdf&page=41
```

În OCR Review:

- editorul Monaco este folosit pentru textul OCR
- `Verifică text` rulează LanguageTool
- problemele apar subliniate în editor
- `Ctrl + .` afișează quick fixes
- `Alt + N` / `Alt + P` navighează între probleme
- `Salvează` salvează corecția paginii

## 4. OCR coverage report

Pentru a verifica ce manuale/pagini au OCR disponibil:

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\report-ocr-coverage.py
```

Raportul se generează în:

```text
data\output\_reports\ocr_coverage_report.json
data\output\_reports\ocr_coverage_report.md
```

## 5. OCR pentru o singură pagină goală

Dacă în OCR Review apare `0 chars`, rulează OCR doar pentru pagina respectivă.

Exemplu pentru manual în engleză:

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\run-ocr-page.py `
  --pdf "Pounder" `
  --page 3 `
  --lang eng `
  --psm 6 `
  --zoom 3.0
```

Exemplu pentru manual în română:

```powershell
cd D:\dev\projects\voila

.\.venv\Scripts\python.exe .\scripts\dev\run-ocr-page.py `
  --pdf "Manualul Instalatiilor Electrice" `
  --page 41 `
  --lang ron+eng `
  --psm 6 `
  --zoom 3.0
```

Textul generat este salvat în:

```text
data\output\<manual>\ocr_pages.manual.json
```

Ruta nouă de OCR Review îl folosește automat ca fallback.

## 6. Smoke test Monaco + LanguageTool

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

Dacă `LanguageTool` nu rulează, pornește aplicația cu:

```powershell
.\scripts\dev\start-voila.ps1
```

## 7. Git checkpoint

După o sesiune stabilă:

```powershell
cd D:\dev\projects\voila

git status --short

.\.venv\Scripts\python.exe -m py_compile .\services\api\web_app.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\ocr_languagetool.py
.\.venv\Scripts\python.exe -m py_compile .\services\api\ocr_best_text.py

git add .
git commit -m "chore: update Voila workflow"
```
