# Voila! Language Pack Packaging Script Integration Scaffold

Milestone: v0.2.31-public-beta-language-pack-packaging-script-integration-scaffold
Status: minimal release script integration
Scope: release script checks only; no runtime changes, no UI changes, no licensing changes

## Goal

This milestone adds the first minimal release-script integration for Voila! language-pack packaging checks.

## What changed

- build-portable-runtime.ps1 now runs language-pack packaging inspection against the staging app root before ZIP creation.
- test-standalone-runtime.ps1 now checks required language-pack files after ZIP extraction.
- test-standalone-runtime.ps1 now runs language-pack packaging inspection against the extracted app root.

## Required packaged files

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## What this milestone does not do

- does not change language-pack runtime behavior
- does not change UI behavior
- does not change OCR processing
- does not change PDF processing
- does not change export behavior
- does not add a language selector
- does not add a LICENSE
- does not modify the validated v0.2.0-public-beta release assets

## Safety

The build script change is a verification step before ZIP creation.

The standalone test change is a verification step after ZIP extraction.

No release artifact is created by this milestone unless the existing build script is run manually.

## Validation

Run from repository root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1 -IncludeSamples
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python -m py_compile .\services\api\i18n.py

## Recommended next milestone

v0.2.32-public-beta-language-pack-packaging-standalone-smoke

## Decision for this milestone

For v0.2.31-public-beta-language-pack-packaging-script-integration-scaffold, the correct action is minimal build/test script inspection only.

Do not change runtime or UI in this milestone.
