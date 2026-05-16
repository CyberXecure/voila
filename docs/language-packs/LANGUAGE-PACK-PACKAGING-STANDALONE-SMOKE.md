# Voila! Language Pack Standalone Package Smoke

Milestone: v0.2.32-public-beta-language-pack-packaging-standalone-smoke
Status: standalone package smoke helper
Scope: smoke helper and documentation only; no runtime changes, no UI changes, no licensing changes

## Goal

This milestone adds a smoke helper for checking language-pack files in a standalone package or extracted app folder.

## What changed

- Adds docs/language-packs/LANGUAGE-PACK-PACKAGING-STANDALONE-SMOKE.md
- Adds scripts/release/smoke-language-pack-standalone-package.ps1

## What this milestone does not do

- does not build a standalone ZIP automatically
- does not modify build-portable-runtime.ps1
- does not modify test-standalone-runtime.ps1
- does not modify runtime behavior
- does not change UI behavior
- does not add a LICENSE
- does not modify the validated v0.2.0-public-beta release assets

## Smoke helper modes

The script supports three safe modes:

1. Source dry-run mode when no ZIP or app root is provided
2. Extracted app folder mode with -PackagedAppRoot
3. ZIP mode with -ZipPath

## Commands

Source dry-run mode:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1

Existing extracted app folder:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -PackagedAppRoot D:\dev\release-tests\some-build\app

Existing standalone ZIP:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -ZipPath D:\dev\releases\voila-some-version.zip

## Required files checked

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Safety

The script does not create a release artifact.

The script only inspects an existing ZIP, an existing app folder, or a temporary dry-run app root.

Temporary folders are removed unless -KeepTemp is used.

## Validation

Run from repository root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1
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

v0.2.33-public-beta-language-pack-packaging-build-smoke

## Decision for this milestone

For v0.2.32-public-beta-language-pack-packaging-standalone-smoke, the correct action is to add a standalone package smoke helper only.

Do not change runtime or UI in this milestone.
