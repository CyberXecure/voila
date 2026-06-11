# Voila Windows Package Complete Runtime Source Discovery Result

Milestone:

`	ext
v0.3.48-voila-windows-package-complete-runtime-source-discovery
`

## Purpose

Inspect the repository to discover the actual files and commands needed for a complete Windows package runtime source.

## Scope

`	ext
Documentation/discovery only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No ZIP creation.
No installer creation.
No START/STOP execution.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
`

## Source

`	ext
Branch: docs/v0.3.48-voila-windows-package-complete-runtime-source-discovery
Commit: b1b717a
`

## Summary

`	ext
Likely API entrypoint: scripts\dev\add-course-tools-navigation.py
Dependency strategy: requirements.txt detected
Frontend/static strategy: frontend/static references detected; exact packaging strategy requires review
LanguageTool strategy: LanguageTool references detected
Tesseract/OCR strategy: Tesseract/OCR references detected
`

## main.py / app.py / server.py files

`	ext
not found
`

## API entrypoint candidates

`	ext
scripts\dev\add-course-tools-navigation.py
scripts\dev\add-document-language-endpoints.py
scripts\dev\add-lessons-routes.py
scripts\dev\add-ocr-correction-workflow.py
scripts\dev\add-ocr-text-autocomplete.py
scripts\dev\add-quick-tools-route.py
scripts\dev\add-review-concepts-ui.py
scripts\dev\add-review-ocr-floating-zoom.py
scripts\dev\add-review-ocr-text-ui.py
scripts\dev\add-run-ocr-page-endpoint.py
scripts\dev\fix-edit-crops-route.py
scripts\dev\fix-languagetool-endpoint-json-safe.py
scripts\dev\fix-languagetool-request-annotation.py
scripts\dev\fix-monaco-static-includes.py
scripts\dev\fix-ocr-autocomplete-syntax.py
scripts\dev\fix-review-concepts-save.py
scripts\dev\fix-vscode-autocomplete-css-braces.py
scripts\dev\hard-fix-vscode-autocomplete-css.py
scripts\dev\install-delete-from-library.py
scripts\dev\make-ocr-suggestions-vscode-style.py
scripts\dev\patch-delete-course.py
scripts\dev\patch-delete-from-library.py
scripts\dev\patch-progress-dashboard.py
scripts\dev\patch-review-navigation-links.py
scripts\dev\patch-review-weak-concepts.py
scripts\dev\patch-study-mode.py
scripts\dev\patch-upload.py
scripts\dev\patch-web-edit-crops-autostart.py
scripts\dev\remove-floating-zoom-add-tip.py
scripts\dev\wire-monaco-ocr-static-assets.py
services\api\crop_editor_app.py
services\api\web_app.py
`

## Dependency/config files

`	ext
services\api\requirements.txt
`

## Interesting runtime directories

`	ext
assets
language-packs\runtime
scripts
scripts\runtime
services\api
services\api\static
`

## Start/runtime command references

`	ext
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:95: $hit = Select-String -Path $file.FullName -Pattern "FastAPI\(|uvicorn|@app\.|APIRouter\(" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:103: $hit = Select-String -Path $file.FullName -Pattern "uvicorn|fastapi|8787|8081|LanguageTool|languagetool|tesseract|START-VOILA|start-voila" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:121: $languageToolHits = @()
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:122: $tesseractHits = @()
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:126: $lt = Select-String -Path $file.FullName -Pattern "LanguageTool|languagetool|8081" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:129: $languageToolHits += [pscustomobject]@{ File = To-RelPath $file.FullName; Line = $h.LineNumber; Text = $h.Line.Trim() }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:133: $tes = Select-String -Path $file.FullName -Pattern "tesseract|OCR|pytesseract" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:136: $tesseractHits += [pscustomobject]@{ File = To-RelPath $file.FullName; Line = $h.LineNumber; Text = $h.Line.Trim() }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:173: $ltHitList = Format-Hits $languageToolHits 60
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:174: $tesseractHitList = Format-Hits $tesseractHits 60
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:202: $languageToolStrategy = "not determined"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:203: if ($languageToolHits.Count -gt 0) {
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:204: $languageToolStrategy = "LanguageTool references detected"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:207: $tesseractStrategy = "not determined"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:208: if ($tesseractHits.Count -gt 0) {
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:209: $tesseractStrategy = "Tesseract/OCR references detected"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:215: Write-Host "LanguageTool strategy: $languageToolStrategy"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:216: Write-Host "Tesseract strategy: $tesseractStrategy"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:265: $resultLines.Add("LanguageTool strategy: $languageToolStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:266: $resultLines.Add("Tesseract/OCR strategy: $tesseractStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:299: $resultLines.Add("## LanguageTool references")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:305: $resultLines.Add("## Tesseract/OCR references")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:308: foreach ($line in $tesseractHitList) { $resultLines.Add($line) }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:366: $copyMapLines.Add("## LanguageTool/Java")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:369: $copyMapLines.Add("Detected strategy: $languageToolStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:370: $copyMapLines.Add("Future package should define bundled vs deferred LanguageTool.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:373: $copyMapLines.Add("## Tesseract/OCR")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:376: $copyMapLines.Add("Detected strategy: $tesseractStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:383: $copyMapLines.Add("START-VOILA.bat")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:385: $copyMapLines.Add("scripts/start-voila.ps1")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:425: $validationLines.Add("[ ] LanguageTool/Java decision selected")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:426: $validationLines.Add("[ ] Tesseract/OCR decision selected")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:457: $commercialLines.Add("[ ] LanguageTool/Java decision confirmed")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:458: $commercialLines.Add("[ ] Tesseract/OCR decision confirmed")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:516: $checklistLines.Add("[ ] LanguageTool references discovered")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:517: $checklistLines.Add("[ ] Tesseract/OCR references discovered")
scripts\dev\install-ocr-languages.ps1:8: $BaseUrl = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main"
scripts\dev\start-crop-editor.ps1:27: "cd `"$ProjectRoot`"; .\.venv\Scripts\python.exe -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790 --log-level info"
scripts\dev\start-local.ps1:16: Write-Host "URL: http://127.0.0.1:8787"
scripts\dev\start-local.ps1:21: Start-Process "http://127.0.0.1:8787"
scripts\dev\start-local.ps1:24: & $Python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787
scripts\dev\start-local.ps1:36: "cd `"$ProjectRoot`"; .\.venv\Scripts\python.exe -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790 --log-level info"
scripts\dev\start-voila.ps1:12: $VoilaPort = 8787
scripts\dev\start-voila.ps1:14: $LtPort = 8081
scripts\dev\start-voila.ps1:16: $LanguageToolDir = "D:\dev\tools\LanguageTool"
scripts\dev\start-voila.ps1:17: $LanguageToolJar = Join-Path $LanguageToolDir "languagetool-server.jar"
scripts\dev\start-voila.ps1:18: $LanguageToolConfig = Join-Path $LanguageToolDir "server.properties"
scripts\dev\start-voila.ps1:53: function Test-LanguageTool {
scripts\dev\start-voila.ps1:83: & $Python -m py_compile (Join-Path $ProjectRoot "services\api\ocr_languagetool.py")
scripts\dev\start-voila.ps1:87: Write-Host "=== 2. LanguageTool ==="
scripts\dev\start-voila.ps1:89: if (Test-LanguageTool) {
scripts\dev\start-voila.ps1:90: Write-Host "OK: LanguageTool rulează deja pe http://$LtHost`:$LtPort"
scripts\dev\start-voila.ps1:96: if (!(Test-Path $LanguageToolJar)) {
scripts\dev\start-voila.ps1:97: throw "Nu găsesc LanguageTool jar: $LanguageToolJar"
scripts\dev\start-voila.ps1:100: if (!(Test-Path $LanguageToolConfig)) {
scripts\dev\start-voila.ps1:101: New-Item -ItemType File -Force -Path $LanguageToolConfig | Out-Null
scripts\dev\start-voila.ps1:104: Write-Host "Pornesc LanguageTool într-o fereastră separată..."
scripts\dev\start-voila.ps1:107: cd '$LanguageToolDir'
scripts\dev\start-voila.ps1:108: java -cp languagetool-server.jar org.languagetool.server.HTTPServer --config server.properties --port $LtPort --allow-origin
scripts\dev\start-voila.ps1:114: -WorkingDirectory $LanguageToolDir `
scripts\dev\start-voila.ps1:117: "languagetool-server.jar",
scripts\dev\start-voila.ps1:118: "org.languagetool.server.HTTPServer",
scripts\dev\start-voila.ps1:133: Write-Host "Aștept LanguageTool..."
scripts\dev\start-voila.ps1:137: if (Test-LanguageTool) {
scripts\dev\start-voila.ps1:145: Write-Host "WARN: LanguageTool nu a răspuns încă. Voila va porni, dar Verifică text poate afișa eroare."
scripts\dev\start-voila.ps1:147: Write-Host "OK: LanguageTool pornit."
scripts\dev\start-voila.ps1:161: & '$Python' -m uvicorn web_app:app --app-dir '.\services\api' --host $VoilaHost --port $VoilaPort --log-level info
scripts\dev\start-voila.ps1:170: "uvicorn",
scripts\dev\start-voila.ps1:210: Write-Host "Silent mode: LanguageTool and Voila were started in hidden background windows."
scripts\dev\start-voila.ps1:212: Write-Host "Ține deschise ferestrele PowerShell pentru LanguageTool și Voila."
scripts\dev\stop-local.ps1:3: $Port = 8787
scripts\dev\stop-voila.ps1:3: $VoilaPort = 8787
scripts\dev\stop-voila.ps1:4: $LanguageToolPort = 8081
scripts\dev\stop-voila.ps1:54: $Port -eq 8787 -and
scripts\dev\stop-voila.ps1:56: $cmd -like "*uvicorn*" -and
scripts\dev\stop-voila.ps1:60: $isLanguageTool = (
scripts\dev\stop-voila.ps1:61: $Port -eq 8081 -and
scripts\dev\stop-voila.ps1:64: $cmd -like "*languagetool-server.jar*" -or
scripts\dev\stop-voila.ps1:65: $cmd -like "*org.languagetool.server.HTTPServer*"
scripts\dev\stop-voila.ps1:69: if (!$isVoila -and !$isLanguageTool) {
`

## LanguageTool references

`	ext
README.md:221: - LanguageTool integration
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:103: $hit = Select-String -Path $file.FullName -Pattern "uvicorn|fastapi|8787|8081|LanguageTool|languagetool|tesseract|START-VOILA|start-voila" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:121: $languageToolHits = @()
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:126: $lt = Select-String -Path $file.FullName -Pattern "LanguageTool|languagetool|8081" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:129: $languageToolHits += [pscustomobject]@{ File = To-RelPath $file.FullName; Line = $h.LineNumber; Text = $h.Line.Trim() }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:173: $ltHitList = Format-Hits $languageToolHits 60
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:202: $languageToolStrategy = "not determined"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:203: if ($languageToolHits.Count -gt 0) {
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:204: $languageToolStrategy = "LanguageTool references detected"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:215: Write-Host "LanguageTool strategy: $languageToolStrategy"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:265: $resultLines.Add("LanguageTool strategy: $languageToolStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:299: $resultLines.Add("## LanguageTool references")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:366: $copyMapLines.Add("## LanguageTool/Java")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:369: $copyMapLines.Add("Detected strategy: $languageToolStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:370: $copyMapLines.Add("Future package should define bundled vs deferred LanguageTool.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:425: $validationLines.Add("[ ] LanguageTool/Java decision selected")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:457: $commercialLines.Add("[ ] LanguageTool/Java decision confirmed")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:516: $checklistLines.Add("[ ] LanguageTool references discovered")
audit\v0.1.4-language-runtime-audit.txt:34: LanguageTool references in source
audit\v0.1.4-language-runtime-audit.txt:36: docs\USAGE.md:3: Voila! este o aplicație locală pentru transformarea manualelor PDF în conținut de studiu, cu suport pentru OCR review, corecții manuale, lecții, Study Mode și verificare LanguageTool.
audit\v0.1.4-language-runtime-audit.txt:37: docs\USAGE.md:19: LanguageTool rulează local la:
audit\v0.1.4-language-runtime-audit.txt:38: docs\USAGE.md:22: http://127.0.0.1:8081/v2/check
audit\v0.1.4-language-runtime-audit.txt:39: docs\USAGE.md:69: - `Verifică text` rulează LanguageTool
audit\v0.1.4-language-runtime-audit.txt:40: docs\USAGE.md:195: OCR, LanguageTool, întrebări de studiu
audit\v0.1.4-language-runtime-audit.txt:41: docs\USAGE.md:203: LanguageTool: en-US
audit\v0.1.4-language-runtime-audit.txt:42: docs\USAGE.md:210: LanguageTool: ro-RO
audit\v0.1.4-language-runtime-audit.txt:43: docs\USAGE.md:214: ## LanguageTool
audit\v0.1.4-language-runtime-audit.txt:44: docs\USAGE.md:216: LanguageTool trebuie să ruleze local pentru verificarea textului:
audit\v0.1.4-language-runtime-audit.txt:45: docs\USAGE.md:219: http://127.0.0.1:8081/v2/check
audit\v0.1.4-language-runtime-audit.txt:46: docs\USAGE.md:228: http://127.0.0.1:8081/v2/check
audit\v0.1.4-language-runtime-audit.txt:47: docs\USAGE.md:231: Dacă LanguageTool nu răspunde, pornește aplicația cu:
audit\v0.1.4-language-runtime-audit.txt:48: docs\USAGE.md:239: ## Smoke test Monaco + LanguageTool
audit\v0.1.4-language-runtime-audit.txt:49: scripts\dev\add-document-language-module.py:17: "languagetool_lang": "auto",
audit\v0.1.4-language-runtime-audit.txt:50: scripts\dev\add-document-language-module.py:23: "languagetool_lang": "ro-RO",
audit\v0.1.4-language-runtime-audit.txt:51: scripts\dev\add-document-language-module.py:29: "languagetool_lang": "en-US",
audit\v0.1.4-language-runtime-audit.txt:52: scripts\dev\add-document-language-module.py:35: "languagetool_lang": "fr",
audit\v0.1.4-language-runtime-audit.txt:53: scripts\dev\add-document-language-module.py:41: "languagetool_lang": "de-DE",
audit\v0.1.4-language-runtime-audit.txt:54: scripts\dev\add-document-language-module.py:47: "languagetool_lang": "ru-RU",
audit\v0.1.4-language-runtime-audit.txt:55: scripts\dev\add-document-language-module.py:194: def get_languagetool_lang(project_root: Path | str, pdf_name: str, fallback_text: str = "") -> str:
audit\v0.1.4-language-runtime-audit.txt:56: scripts\dev\add-document-language-module.py:201: return SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["en"])["languagetool_lang"]
audit\v0.1.4-language-runtime-audit.txt:57: scripts\dev\add-it-es-pt-document-languages.py:10: "languagetool_lang": "ru-RU",
audit\v0.1.4-language-runtime-audit.txt:58: scripts\dev\add-it-es-pt-document-languages.py:18: "languagetool_lang": "ru-RU",
audit\v0.1.4-language-runtime-audit.txt:59: scripts\dev\add-it-es-pt-document-languages.py:24: "languagetool_lang": "it",
audit\v0.1.4-language-runtime-audit.txt:60: scripts\dev\add-it-es-pt-document-languages.py:30: "languagetool_lang": "es",
audit\v0.1.4-language-runtime-audit.txt:61: scripts\dev\add-it-es-pt-document-languages.py:36: "languagetool_lang": "pt",
audit\v0.1.4-language-runtime-audit.txt:62: scripts\dev\add-it-es-pt-monaco-languages.py:19: # Extend LanguageTool map.
audit\v0.1.4-language-runtime-audit.txt:63: scripts\dev\add-run-ocr-page-button-monaco.py:12: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:64: scripts\dev\add-run-ocr-page-button-monaco.py:25: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:65: scripts\dev\create-monaco-ocr-static-assets.py:106: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:66: scripts\dev\create-monaco-ocr-static-assets.py:199: title: "LanguageTool: " + replacement,
audit\v0.1.4-language-runtime-audit.txt:67: scripts\dev\create-monaco-ocr-static-assets.py:225: window.voilaSetLanguageToolMarkers = function (matches) {
audit\v0.1.4-language-runtime-audit.txt:68: scripts\dev\create-monaco-ocr-static-assets.py:238: message: match.message || "LanguageTool suggestion",
audit\v0.1.4-language-runtime-audit.txt:69: scripts\dev\create-monaco-ocr-static-assets.py:239: source: "LanguageTool",
audit\v0.1.4-language-runtime-audit.txt:70: scripts\dev\create-monaco-ocr-static-assets.py:244: monaco.editor.setModelMarkers(model, "languagetool", markers);
audit\v0.1.4-language-runtime-audit.txt:71: scripts\dev\create-monaco-ocr-static-assets.py:247: setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
audit\v0.1.4-language-runtime-audit.txt:72: scripts\dev\create-monaco-ocr-static-assets.py:250: "<strong>LanguageTool:</strong> " + markers.length +
audit\v0.1.4-language-runtime-audit.txt:73: scripts\dev\create-monaco-ocr-static-assets.py:256: window.voilaGoToLanguageToolIssue = function (direction) {
audit\v0.1.4-language-runtime-audit.txt:74: scripts\dev\create-monaco-ocr-static-assets.py:271: "<strong>LanguageTool:</strong> sugestia " +
audit\v0.1.4-language-runtime-audit.txt:75: scripts\dev\create-monaco-ocr-static-assets.py:279: label: "LanguageTool: Next issue",
audit\v0.1.4-language-runtime-audit.txt:76: scripts\dev\create-monaco-ocr-static-assets.py:282: window.voilaGoToLanguageToolIssue(1);
`

## Tesseract/OCR references

`	ext
BETA-TERMS.md:56: Voila may generate lessons, study questions, glossary items, OCR output, figures, summaries, or other learning artifacts.
BETA-TERMS.md:72: The project owner is not responsible for data loss, incorrect generated content, OCR errors, extraction errors, or misuse of beta builds.
LICENSE.txt:43: Voila is provided as beta software, without warranty. Generated content may contain OCR, extraction, formatting, or interpretation errors. Users are responsible for reviewing generated material before relying on it.
README.md:5: Voila! turns PDF documents into structured, study-ready courses with lessons, extracted figures, OCR review tools, study questions, and progress tracking.
README.md:23: - review and adjust OCR crops
README.md:41: - improve OCR and figure workflows
README.md:77: The crop editor helps review and adjust figure/OCR regions when a document needs cleanup.
README.md:95: Course Tools provides a central place for opening the generated course, lessons, study mode, OCR review, figures, crop editing, and progress.
README.md:111: ### OCR-assisted review
README.md:113: Voila includes OCR-related tools for PDFs where text extraction is incomplete, scanned, or imperfect.
README.md:125: Users can review and adjust crop areas to improve figure extraction and OCR-related workflows.
README.md:206: Text extraction + OCR support
README.md:220: - OCR tooling
README.md:245: ### OCR and figures
README.md:249: - improve OCR review workflow
README.md:510: Voila is beta software. Generated content may contain extraction, OCR, formatting, or interpretation errors. Always review generated course material before using it for professional, academic, or technical decisions.
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:103: $hit = Select-String -Path $file.FullName -Pattern "uvicorn|fastapi|8787|8081|LanguageTool|languagetool|tesseract|START-VOILA|start-voila" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:122: $tesseractHits = @()
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:133: $tes = Select-String -Path $file.FullName -Pattern "tesseract|OCR|pytesseract" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:136: $tesseractHits += [pscustomobject]@{ File = To-RelPath $file.FullName; Line = $h.LineNumber; Text = $h.Line.Trim() }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:174: $tesseractHitList = Format-Hits $tesseractHits 60
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:207: $tesseractStrategy = "not determined"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:208: if ($tesseractHits.Count -gt 0) {
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:209: $tesseractStrategy = "Tesseract/OCR references detected"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:216: Write-Host "Tesseract strategy: $tesseractStrategy"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:266: $resultLines.Add("Tesseract/OCR strategy: $tesseractStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:305: $resultLines.Add("## Tesseract/OCR references")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:308: foreach ($line in $tesseractHitList) { $resultLines.Add($line) }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:373: $copyMapLines.Add("## Tesseract/OCR")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:376: $copyMapLines.Add("Detected strategy: $tesseractStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:377: $copyMapLines.Add("Future package should define bundled vs deferred OCR.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:426: $validationLines.Add("[ ] Tesseract/OCR decision selected")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:458: $commercialLines.Add("[ ] Tesseract/OCR decision confirmed")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:517: $checklistLines.Add("[ ] Tesseract/OCR references discovered")
audit\v0.1.4-language-runtime-audit.txt:20: v0.1.3-ocr-runtime
audit\v0.1.4-language-runtime-audit.txt:36: docs\USAGE.md:3: Voila! este o aplicație locală pentru transformarea manualelor PDF în conținut de studiu, cu suport pentru OCR review, corecții manuale, lecții, Study Mode și verificare LanguageTool.
audit\v0.1.4-language-runtime-audit.txt:40: docs\USAGE.md:195: OCR, LanguageTool, întrebări de studiu
audit\v0.1.4-language-runtime-audit.txt:63: scripts\dev\add-run-ocr-page-button-monaco.py:12: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:64: scripts\dev\add-run-ocr-page-button-monaco.py:25: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:65: scripts\dev\create-monaco-ocr-static-assets.py:106: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:66: scripts\dev\create-monaco-ocr-static-assets.py:199: title: "LanguageTool: " + replacement,
audit\v0.1.4-language-runtime-audit.txt:67: scripts\dev\create-monaco-ocr-static-assets.py:225: window.voilaSetLanguageToolMarkers = function (matches) {
audit\v0.1.4-language-runtime-audit.txt:68: scripts\dev\create-monaco-ocr-static-assets.py:238: message: match.message || "LanguageTool suggestion",
audit\v0.1.4-language-runtime-audit.txt:69: scripts\dev\create-monaco-ocr-static-assets.py:239: source: "LanguageTool",
audit\v0.1.4-language-runtime-audit.txt:70: scripts\dev\create-monaco-ocr-static-assets.py:244: monaco.editor.setModelMarkers(model, "languagetool", markers);
audit\v0.1.4-language-runtime-audit.txt:71: scripts\dev\create-monaco-ocr-static-assets.py:247: setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
audit\v0.1.4-language-runtime-audit.txt:72: scripts\dev\create-monaco-ocr-static-assets.py:250: "<strong>LanguageTool:</strong> " + markers.length +
audit\v0.1.4-language-runtime-audit.txt:73: scripts\dev\create-monaco-ocr-static-assets.py:256: window.voilaGoToLanguageToolIssue = function (direction) {
audit\v0.1.4-language-runtime-audit.txt:74: scripts\dev\create-monaco-ocr-static-assets.py:271: "<strong>LanguageTool:</strong> sugestia " +
audit\v0.1.4-language-runtime-audit.txt:75: scripts\dev\create-monaco-ocr-static-assets.py:279: label: "LanguageTool: Next issue",
audit\v0.1.4-language-runtime-audit.txt:76: scripts\dev\create-monaco-ocr-static-assets.py:282: window.voilaGoToLanguageToolIssue(1);
audit\v0.1.4-language-runtime-audit.txt:77: scripts\dev\create-monaco-ocr-static-assets.py:288: label: "LanguageTool: Previous issue",
audit\v0.1.4-language-runtime-audit.txt:78: scripts\dev\create-monaco-ocr-static-assets.py:291: window.voilaGoToLanguageToolIssue(-1);
audit\v0.1.4-language-runtime-audit.txt:79: scripts\dev\create-monaco-ocr-static-assets.py:303: setStatus("<strong>LanguageTool:</strong> verific textul...");
audit\v0.1.4-language-runtime-audit.txt:80: scripts\dev\create-monaco-ocr-static-assets.py:306: const response = await fetch("/check-ocr-languagetool", {
audit\v0.1.4-language-runtime-audit.txt:81: scripts\dev\create-monaco-ocr-static-assets.py:318: setStatus("<strong>LanguageTool:</strong> " + (data.message || "nu rulează."));
audit\v0.1.4-language-runtime-audit.txt:82: scripts\dev\create-monaco-ocr-static-assets.py:322: window.voilaSetLanguageToolMarkers(data.matches || []);
audit\v0.1.4-language-runtime-audit.txt:83: scripts\dev\create-monaco-ocr-static-assets.py:324: setStatus("<strong>LanguageTool:</strong> eroare: " + (err.message || String(err)));
audit\v0.1.4-language-runtime-audit.txt:84: scripts\dev\create-monaco-ocr-static-assets.py:336: setStatus("<strong>Editor:</strong> Monaco activ. Ctrl+. = quick fix; Alt+N / Alt+P = navigare LanguageTool.");
audit\v0.1.4-language-runtime-audit.txt:88: scripts\dev\fix-languagetool-endpoint-json-safe.py:7: pattern = r'\n@app\.post\("/check-ocr-languagetool"\)[\s\S]*?(?=\n@app\.|\Z)'
`

## Frontend/static references

`	ext
BETA-TERMS.md:23: - redistribute Voila as your own product
BETA-TERMS.md:29: - commercially redistribute modified versions
LICENSE.txt:9: - commercial redistribution
LICENSE.txt:25: Do not redistribute Voila as your own product.
README.md:15: Voila helps you turn static PDF files into a more practical learning workflow.
README.md:174: - may focus on language-pack assets or validation
README.md:259: ### Monetization and distribution
README.md:345: This helper does not publish a GitHub release, upload assets, create an installer, sign binaries, implement payment/licensing, or provide final legal approval.
README.md:436: The validation script does not build a package, create a release, upload assets, or provide final legal approval. It is a release/package readiness check before ZIP or installer creation.
README.md:471: This script is for package preparation only. It does not rebuild Voila, create a release, upload assets, change runtime behavior, or provide final legal approval.
README.md:482: - commercial redistribution is not allowed
README.md:486: - paid hosting or software-as-a-service redistribution is not allowed
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:3: # No runtime changes, no backend changes, no frontend behavior changes,
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:50: "dist-packages",
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:90: $configFiles = $allFiles | Where-Object { $_.Name -in @("requirements.txt", "pyproject.toml", "poetry.lock", "Pipfile", "package.json", "vite.config.ts", "vite.config.js", "tsconfig.json") }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:118: $_.Name -in @("api", "backend", "service", "app", "frontend", "web", "ui", "static", "dist", "assets", "runtime", "scripts")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:123: $frontendHits = @()
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:140: $fe = Select-String -Path $file.FullName -Pattern "vite|frontend|static|dist|assets|npm run build|serve_static|StaticFiles" -SimpleMatch:$false -ErrorAction SilentlyContinue
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:143: $frontendHits += [pscustomobject]@{ File = To-RelPath $file.FullName; Line = $h.LineNumber; Text = $h.Line.Trim() }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:175: $frontendHitList = Format-Hits $frontendHits 60
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:197: $frontendStrategy = "not determined"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:198: if ($frontendHits.Count -gt 0) {
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:199: $frontendStrategy = "frontend/static references detected; exact packaging strategy requires review"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:214: Write-Host "Frontend strategy: $frontendStrategy"
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:240: $resultLines.Add("No frontend behavior changes.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:264: $resultLines.Add("Frontend/static strategy: $frontendStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:311: $resultLines.Add("## Frontend/static references")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:314: foreach ($line in $frontendHitList) { $resultLines.Add($line) }
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:359: $copyMapLines.Add("## Frontend/static")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:362: $copyMapLines.Add("Detected strategy: $frontendStrategy")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:363: $copyMapLines.Add("Future package should define whether static assets are served by backend or UI is deferred.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:424: $validationLines.Add("[ ] frontend/static strategy selected")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:456: $commercialLines.Add("[ ] frontend/static decision confirmed")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:459: $commercialLines.Add("[ ] legal/commercial distribution boundaries unchanged")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:466: $commercialLines.Add("A later START/STOP PASS and legal/commercial review are still required before external paid distribution.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:486: $checklistLines.Add("No frontend behavior changes.")
voila-v0.3.48-windows-package-complete-runtime-source-discovery.ps1:518: $checklistLines.Add("[ ] frontend/static references discovered")
audit\v0.1.4-language-runtime-audit.txt:65: scripts\dev\create-monaco-ocr-static-assets.py:106: checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
audit\v0.1.4-language-runtime-audit.txt:66: scripts\dev\create-monaco-ocr-static-assets.py:199: title: "LanguageTool: " + replacement,
audit\v0.1.4-language-runtime-audit.txt:67: scripts\dev\create-monaco-ocr-static-assets.py:225: window.voilaSetLanguageToolMarkers = function (matches) {
audit\v0.1.4-language-runtime-audit.txt:68: scripts\dev\create-monaco-ocr-static-assets.py:238: message: match.message || "LanguageTool suggestion",
audit\v0.1.4-language-runtime-audit.txt:69: scripts\dev\create-monaco-ocr-static-assets.py:239: source: "LanguageTool",
audit\v0.1.4-language-runtime-audit.txt:70: scripts\dev\create-monaco-ocr-static-assets.py:244: monaco.editor.setModelMarkers(model, "languagetool", markers);
audit\v0.1.4-language-runtime-audit.txt:71: scripts\dev\create-monaco-ocr-static-assets.py:247: setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
audit\v0.1.4-language-runtime-audit.txt:72: scripts\dev\create-monaco-ocr-static-assets.py:250: "<strong>LanguageTool:</strong> " + markers.length +
audit\v0.1.4-language-runtime-audit.txt:73: scripts\dev\create-monaco-ocr-static-assets.py:256: window.voilaGoToLanguageToolIssue = function (direction) {
audit\v0.1.4-language-runtime-audit.txt:74: scripts\dev\create-monaco-ocr-static-assets.py:271: "<strong>LanguageTool:</strong> sugestia " +
audit\v0.1.4-language-runtime-audit.txt:75: scripts\dev\create-monaco-ocr-static-assets.py:279: label: "LanguageTool: Next issue",
audit\v0.1.4-language-runtime-audit.txt:76: scripts\dev\create-monaco-ocr-static-assets.py:282: window.voilaGoToLanguageToolIssue(1);
audit\v0.1.4-language-runtime-audit.txt:77: scripts\dev\create-monaco-ocr-static-assets.py:288: label: "LanguageTool: Previous issue",
audit\v0.1.4-language-runtime-audit.txt:78: scripts\dev\create-monaco-ocr-static-assets.py:291: window.voilaGoToLanguageToolIssue(-1);
audit\v0.1.4-language-runtime-audit.txt:79: scripts\dev\create-monaco-ocr-static-assets.py:303: setStatus("<strong>LanguageTool:</strong> verific textul...");
audit\v0.1.4-language-runtime-audit.txt:80: scripts\dev\create-monaco-ocr-static-assets.py:306: const response = await fetch("/check-ocr-languagetool", {
audit\v0.1.4-language-runtime-audit.txt:81: scripts\dev\create-monaco-ocr-static-assets.py:318: setStatus("<strong>LanguageTool:</strong> " + (data.message || "nu rulează."));
audit\v0.1.4-language-runtime-audit.txt:82: scripts\dev\create-monaco-ocr-static-assets.py:322: window.voilaSetLanguageToolMarkers(data.matches || []);
audit\v0.1.4-language-runtime-audit.txt:83: scripts\dev\create-monaco-ocr-static-assets.py:324: setStatus("<strong>LanguageTool:</strong> eroare: " + (err.message || String(err)));
audit\v0.1.4-language-runtime-audit.txt:84: scripts\dev\create-monaco-ocr-static-assets.py:336: setStatus("<strong>Editor:</strong> Monaco activ. Ctrl+. = quick fix; Alt+N / Alt+P = navigare LanguageTool.");
audit\v0.1.4-language-runtime-audit.txt:141: scripts\dev\smoke-monaco-static-lt.py:25: "/check-ocr-languagetool",
audit\v0.1.4-language-runtime-audit.txt:171: scripts\dev\wire-monaco-ocr-static-assets.py:36: # 2. Add LanguageTool API endpoint.
audit\v0.1.4-language-runtime-audit.txt:172: scripts\dev\wire-monaco-ocr-static-assets.py:37: if '@app.post("/check-ocr-languagetool")' not in text:
`

## Discovery conclusion

`	ext
The complete runtime source should be based on the discovered API entrypoint and dependency/runtime strategy above.
The next milestone should turn this discovery into an explicit runtime source copy map or implementation plan.
`
