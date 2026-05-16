# Voila! Language Pack Packaging Build Verification

Milestone: v0.2.34-public-beta-language-pack-packaging-build-verification-docs
Status: build verification documentation
Scope: documentation only; no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone documents how to use the current language-pack packaging verification scripts safely during release work.

## What this milestone does not do

- does not modify build-portable-runtime.ps1
- does not modify test-standalone-runtime.ps1
- does not modify inspect-language-pack-packaging.ps1
- does not modify test-language-pack-packaging-readiness.ps1
- does not modify smoke-language-pack-standalone-package.ps1
- does not modify smoke-language-pack-build-output.ps1
- does not build a new standalone ZIP
- does not modify runtime behavior
- does not change UI behavior
- does not add a LICENSE
- does not modify validated public-beta release assets

## Script overview

### 1. inspect-language-pack-packaging.ps1

Purpose:

- verifies required language-pack files in the source tree
- optionally verifies required language-pack files in a packaged app root

Use when:

- checking source language-pack files
- checking a staged app folder
- checking an extracted standalone app folder

Command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

With packaged app root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1 -PackagedAppRoot <APP_ROOT>

Required files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

### 2. test-language-pack-packaging-readiness.ps1

Purpose:

- creates a temporary packaged-app-like folder
- copies required language-pack files into it
- runs packaging inspection against that folder

Use when:

- validating language-pack packaging readiness before changing release scripts
- checking core/schema copy assumptions without building a ZIP

Command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1

With samples:

powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1 -IncludeSamples

Important:

- this is a dry-run helper
- it does not create release artifacts
- it does not modify the real packaging flow

### 3. smoke-language-pack-standalone-package.ps1

Purpose:

- verifies language-pack files in a standalone-style package
- supports source dry-run mode
- supports extracted app folder mode
- supports existing ZIP mode

Use when:

- checking a temporary standalone-style app root
- checking an extracted standalone package
- checking an existing ZIP directly

Source dry-run command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1

With samples:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -IncludeSamples

Existing app root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -PackagedAppRoot <APP_ROOT>

Existing ZIP:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -ZipPath <ZIP_PATH>

Important:

- this script does not build a ZIP
- old ZIPs created before language-pack packaging are expected to fail

### 4. smoke-language-pack-build-output.ps1

Purpose:

- wraps smoke-language-pack-standalone-package.ps1 for build-output ZIP checks
- can check an explicit ZIP
- can check a ZIP by version tag
- can discover the latest local Voila ZIP when safe-skip mode is not used
- can skip cleanly when no explicit ZIP is provided and -SkipIfMissing is used

Use when:

- checking an existing build output ZIP
- validating release output after a standalone build
- running CI/local validation where a ZIP may not exist

Safe validation command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -SkipIfMissing

Explicit ZIP command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -ZipPath <ZIP_PATH>

Version tag command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -VersionTag <VERSION_TAG>

Important:

- with -SkipIfMissing and no explicit ZIP, the script skips cleanly
- without -SkipIfMissing, the script may discover the latest local Voila ZIP
- old ZIPs from before language-pack packaging are expected to fail

### 5. test-standalone-runtime.ps1

Purpose:

- performs broader standalone runtime smoke testing
- checks required runtime files
- starts Voila
- checks health
- checks LanguageTool
- checks Tesseract languages
- now also checks required language-pack files

Use when:

- validating a full standalone package
- testing runtime behavior after ZIP extraction
- preparing a release candidate

Important:

- this is broader than language-pack packaging smoke
- it validates runtime startup and supporting tools

### 6. build-portable-runtime.ps1

Purpose:

- builds the portable standalone runtime package
- stages the app
- prepares runtime dependencies
- creates the ZIP
- now runs language-pack packaging inspection against the staged app root before ZIP creation

Use when:

- intentionally creating a standalone ZIP

Important:

- this is the real packaging script
- do not run it casually when only documentation or smoke helpers are being changed

## Recommended verification order

Before packaging script changes:

1. inspect-language-pack-packaging.ps1
2. test-language-pack-packaging-readiness.ps1
3. test-language-pack-packaging-readiness.ps1 -IncludeSamples
4. smoke-language-pack-standalone-package.ps1
5. smoke-language-pack-standalone-package.ps1 -IncludeSamples
6. smoke-language-pack-build-output.ps1 -SkipIfMissing

After building a real standalone ZIP:

1. smoke-language-pack-build-output.ps1 -ZipPath <ZIP_PATH>
2. smoke-language-pack-standalone-package.ps1 -ZipPath <ZIP_PATH>
3. test-standalone-runtime.ps1 against the ZIP

## Expected failure cases

Expected failures:

- old ZIPs created before language-pack packaging will fail language-pack checks
- ZIPs missing language-packs/core will fail
- ZIPs missing language-packs/schema will fail
- extracted app folders without required language-pack files will fail

Expected safe skip:

- smoke-language-pack-build-output.ps1 -SkipIfMissing should skip cleanly when no explicit ZIP is provided

## Current safe baseline

The current safe baseline is:

- core Romanian and English packs exist
- schema exists
- source inspection passes
- readiness dry-run passes
- standalone package smoke passes in source dry-run mode
- build-output smoke safe mode skips cleanly when no explicit ZIP is provided
- release scripts parse successfully

## Decision for this milestone

For v0.2.34-public-beta-language-pack-packaging-build-verification-docs, the correct action is documentation only.

Do not change packaging scripts, runtime, or UI in this milestone.
