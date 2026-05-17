# Voila! Language Pack RC Build Plan

Milestone: v0.2.39-public-beta-language-pack-rc-build-plan
Status: RC build planning
Scope: documentation only; no GitHub release upload, no tag, no public ZIP publish, no runtime changes, no UI changes

## Goal

This document defines the safe plan for creating a controlled release-candidate build for Voila! language-pack packaging.

The goal is to move from the validated local dry-run ZIP to a clearly named RC ZIP that can be verified before any public release action.

## Validated baseline

Current validated local ZIP baseline:

``text
ZIP:    D:\dev\releases\voila-v0236-lpbuild-20260516-1844.zip
SHA256: D63C223CC233438D29176F43E9BA166F5659B04FA2CD11904E72E4A28092CAD3
``

This ZIP passed:

- build-output language-pack smoke
- standalone package language-pack smoke
- full standalone runtime smoke
- source language-pack inspection
- language-pack validation
- runtime tests
- UI smoke
- core runtime helper smoke
- language-pack file smoke
- Python compile
- PowerShell parse check

## RC build objective

The future RC build should produce a clearly named local artifact that can be reviewed before any upload or tag.

Recommended build tag pattern:

``text
voila-v0240-lp-rc1-YYYYMMDD-HHMM
``

Recommended output location:

``text
D:\dev\releases\
``

## Required pre-build state

Before running a future RC build:

- main must be clean
- no PRs should be open
- no uncommitted files should exist
- RC asset templates must exist
- release scripts must parse successfully
- source language-pack validation must pass
- baseline ZIP validation should still pass

## Future RC build command

The future RC build should be run intentionally with a short tag to avoid Windows path-length issues:

``powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\build-portable-runtime.ps1
  -VersionTag "<RC_BUILD_TAG>"
  -ReleaseRoot "D:\dev\releases"
``

## Required post-build checks

After the future RC ZIP is created, run:

``powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -ZipPath "<RC_ZIP_PATH>"
powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -ZipPath "<RC_ZIP_PATH>"
powershell -ExecutionPolicy Bypass -File .\scripts\release\test-standalone-runtime.ps1 -VersionTag "<RC_BUILD_TAG>" -ReleaseRoot "D:\dev\releases"
``

## Required ZIP contents

The RC ZIP must include:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json
- python/python.exe
- runtime/tesseract/tesseract.exe
- runtime/java/bin/java.exe
- runtime/languagetool/languagetool-server.jar
- Run-Voila.ps1
- Stop-Voila.ps1

## RC asset preparation

After the future RC build passes validation:

- generate SHA256 after final ZIP creation
- update RC SHA256 file
- update RC test log
- update RC final checklist
- update RC release notes

## Safety rules

This milestone must not:

- upload assets to GitHub Releases
- create a Git tag
- publish the ZIP
- overwrite v0.2.0-public-beta assets
- change runtime behavior
- change UI behavior
- add or modify LICENSE files

## Decision

RC build execution must stay controlled and local until final approval.

No public release action is allowed from this planning document alone.
