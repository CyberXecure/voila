# Voila! Language Pack RC Manual Test Checklist

Milestone: v0.2.41-public-beta-language-pack-rc-manual-test-plan
Status: manual test checklist
Scope: documentation only; no GitHub release upload, no tag, no public ZIP publish, no runtime changes, no UI changes

## RC artifact

- [ ] ZIP path confirmed: D:\dev\releases\voila-v0240-lp-rc1-20260517-0914.zip
- [ ] SHA256 confirmed: 33DC31243F45AD499A889A12F4140779499EFCC0C6218C5BB011920CF36679BC

## Clean extraction

- [ ] clean manual test folder created
- [ ] old extraction removed
- [ ] ZIP extracted successfully
- [ ] extracted folder contains app directory

## Required files

- [ ] app/Run-Voila.ps1 exists
- [ ] app/Stop-Voila.ps1 exists
- [ ] app/python/python.exe exists
- [ ] app/runtime/tesseract/tesseract.exe exists
- [ ] app/runtime/java/bin/java.exe exists
- [ ] app/runtime/languagetool/languagetool-server.jar exists
- [ ] app/language-packs/core/ro.language-pack.json exists
- [ ] app/language-packs/core/en.language-pack.json exists
- [ ] app/language-packs/schema/language-pack.schema.json exists

## Startup

- [ ] Run-Voila.ps1 starts successfully
- [ ] app does not require dev Python
- [ ] app does not require system Tesseract
- [ ] app does not require system Java
- [ ] local API starts
- [ ] LanguageTool starts

## Runtime checks

- [ ] http://127.0.0.1:8780/health returns ok
- [ ] LanguageTool responds on port 8081
- [ ] Tesseract lists eng
- [ ] Tesseract lists osd
- [ ] Tesseract lists ron
- [ ] Tesseract lists rus

## Manual user flow

- [ ] browser/app opens
- [ ] small PDF upload works
- [ ] OCR/review flow opens
- [ ] OCR text is visible
- [ ] no obvious broken navigation
- [ ] Romanian/English language-pack-backed labels are visible where expected

## Shutdown

- [ ] Stop-Voila.ps1 runs successfully
- [ ] Voila process stops
- [ ] LanguageTool process stops
- [ ] port 8780 is released
- [ ] port 8081 is released

## Safety

- [ ] no GitHub release upload
- [ ] no Git tag
- [ ] no public ZIP publish
- [ ] v0.2.0-public-beta assets unchanged
- [ ] no runtime behavior change
- [ ] no UI behavior change
- [ ] no LICENSE change

## Result

- [ ] PASS
- [ ] FAIL

## Notes

- Manual test execution is planned here, not performed by this milestone.
- Any manual-test issues should be documented in a later milestone before public release.
