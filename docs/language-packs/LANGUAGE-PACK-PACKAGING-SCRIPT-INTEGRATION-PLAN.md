# Voila! Language Pack Packaging Script Integration Plan

Milestone: v0.2.30-public-beta-language-pack-packaging-script-integration-plan
Status: integration planning only
Scope: documentation only; no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone defines the exact future integration plan for language-pack packaging in Voila! release scripts.

## Non-goals

This milestone does not:

- modify scripts/release/build-portable-runtime.ps1
- modify scripts/release/test-standalone-runtime.ps1
- modify scripts/release/inspect-language-pack-packaging.ps1
- modify scripts/release/test-language-pack-packaging-readiness.ps1
- copy language packs into real release artifacts
- modify ZIP output
- modify runtime startup scripts
- modify application runtime behavior
- modify UI behavior
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Current readiness state

Current checks already exist:

- scripts/release/inspect-language-pack-packaging.ps1
- scripts/release/test-language-pack-packaging-readiness.ps1
- scripts/language-packs/smoke-language-pack-files.py

Current required source files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

Current optional source files:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json
- language-packs/runtime/minimal_language_runtime.py

## Future build-portable-runtime.ps1 integration

Future integration should happen in scripts/release/build-portable-runtime.ps1 only after the project is copied into the staging app directory.

Recommended future insertion point:

- after ProjectRoot is copied into AppDir
- after local-only/generated folders are cleaned
- before final ZIP cleanup
- before Compress-Archive

Recommended future checks:

- verify language-packs/core exists under AppDir
- verify language-packs/schema exists under AppDir
- run inspect-language-pack-packaging.ps1 against AppDir
- fail clearly before ZIP creation if required language-pack files are missing

Recommended future behavior:

- keep core packs in packaged output
- keep schema in packaged output
- decide separately whether samples stay in packaged output
- do not rely on D:\dev\projects\voila at runtime

## Future test-standalone-runtime.ps1 integration

Future integration should update scripts/release/test-standalone-runtime.ps1 after ZIP extraction.

Recommended future insertion point:

- after Expand-Archive
- after AppRoot is set
- inside or near requiredFiles validation
- before starting Voila

Recommended future required files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

Recommended future check:

powershell -ExecutionPolicy Bypass -File <repo>\\scripts\\release\\inspect-language-pack-packaging.ps1 -PackagedAppRoot <extracted-app-root>

## Future staged-app verification

A future implementation PR should prove that this command works against a real staged app root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1 -PackagedAppRoot <STAGED_APP_ROOT>

## Safety requirements

Future implementation must preserve:

- existing Python runtime packaging
- existing Tesseract runtime packaging
- existing Java runtime packaging
- existing LanguageTool runtime packaging
- existing shortcut scripts
- existing standalone smoke behavior
- existing v0.2.0-public-beta release artifacts

## Future implementation shape

Recommended next implementation should be small:

1. add packaged language-pack inspection to build-portable-runtime.ps1
2. add required language-pack files to test-standalone-runtime.ps1
3. run packaged inspection after ZIP extraction
4. avoid runtime/UI changes in the same PR

## Recommended next milestone

v0.2.31-public-beta-language-pack-packaging-script-integration-scaffold

Suggested next work:

- add the smallest build/test script integration
- do not change language-pack runtime behavior
- do not expand UI localization
- do not alter release assets manually

## Decision for this milestone

For v0.2.30-public-beta-language-pack-packaging-script-integration-plan, the correct action is documentation only.

No release scripts should be changed.
