# Voila! Language Pack RC Build Dry Run

Milestone: v0.2.40-public-beta-language-pack-rc-build-dry-run
Status: completed local RC build dry run
Scope: local RC build validation + documentation/assets; no GitHub release upload, no Git tag, no public ZIP publish, no runtime/UI behavior change

## Goal

This milestone performs a controlled local release-candidate build for Voila! language-pack packaging.

The generated RC ZIP remains local until final approval.

## RC build result

``text
BuildTag: voila-v0240-lp-rc1-20260517-0914
ZIP:      D:\dev\releases\voila-v0240-lp-rc1-20260517-0914.zip
INFO:     D:\dev\releases\voila-v0240-lp-rc1-20260517-0914_RELEASE-INFO.txt
LOG:      D:\dev\releases\voila-v0240-lp-rc1-20260517-0914_BUILD-LOG.txt
SHA256:   33DC31243F45AD499A889A12F4140779499EFCC0C6218C5BB011920CF36679BC
``

## Verification passed

The RC ZIP passed:

- source language-pack inspection before build
- language-pack validation before build
- Python compile before build
- staging language-pack inspection before ZIP creation
- build output language-pack smoke against the RC ZIP
- standalone package language-pack smoke against the RC ZIP
- full standalone runtime smoke test
- /health returned {"status":"ok"}
- LanguageTool runtime responded
- Tesseract runtime listed expected OCR languages: eng, osd,
on,
us
- Voila port was released after stop
- LanguageTool port was released after stop

## Required language-pack files verified

The standalone RC ZIP contains:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Required runtime files verified

The standalone RC ZIP contains:

- python/python.exe
-
untime/tesseract/tesseract.exe
-
untime/java/bin/java.exe
-
untime/languagetool/languagetool-server.jar
- Run-Voila.ps1
- Stop-Voila.ps1

## Safety

This milestone did not:

- upload assets to GitHub Releases
- create a Git tag
- publish the ZIP
- overwrite existing v0.2.0-public-beta release assets
- change runtime behavior
- change UI behavior
- add or modify LICENSE files

## Decision

v0.2.40 validates that a controlled local RC build can be produced and verified.

The RC ZIP remains a local artifact only.
