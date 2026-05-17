# Voila! Language Pack Release Candidate Checklist

Milestone: v0.2.37-public-beta-language-pack-release-candidate-plan
Status: release candidate checklist
Scope: documentation only; no GitHub release upload, no tag, no public asset publish, no runtime changes, no UI changes

## Pre-RC repository checks

- main is clean
- no open PRs
- no uncommitted files
- latest language-pack dry-run documentation exists
- build script parses successfully
- release smoke scripts parse successfully

## Pre-RC automated checks

- smoke-language-pack-build-output.ps1 passes against target ZIP
- smoke-language-pack-standalone-package.ps1 passes against target ZIP
- inspect-language-pack-packaging.ps1 passes
- validate-language-packs.py passes
- test_language_pack_runtime.py passes
- test_minimal_language_runtime.py passes
- smoke-ui-language-endpoint.py passes
- smoke-core-runtime-helper.py passes
- smoke-language-pack-files.py passes
- python -m py_compile services/api/i18n.py passes

## Required ZIP files

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json
- python/python.exe
- runtime/tesseract/tesseract.exe
- runtime/java/bin/java.exe
- runtime/languagetool/languagetool-server.jar
- Run-Voila.ps1
- Stop-Voila.ps1

## Manual RC checks

- ZIP extracts successfully
- Run-Voila.ps1 starts the app
- /health returns ok
- LanguageTool responds
- Tesseract lists expected OCR languages
- small PDF upload works
- OCR review page opens
- app stops cleanly
- Voila port is released
- LanguageTool port is released

## RC artifact files

- RC ZIP
- SHA256 file
- RELEASE-NOTES.md
- TEST-LOG.txt
- FINAL-CHECKLIST.md

## Do not proceed if

- the ZIP is old or accidentally selected
- SHA256 was generated before final ZIP creation
- smoke test fails
- manual test fails
- language-pack files are missing
- runtime files are missing
- working tree becomes dirty unexpectedly
- release assets would overwrite v0.2.0-public-beta

## Decision

This checklist is preparation only.

No RC asset is published in v0.2.37.
