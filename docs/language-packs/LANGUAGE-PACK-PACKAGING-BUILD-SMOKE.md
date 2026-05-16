# Voila! Language Pack Packaging Build Smoke

Milestone: v0.2.33-public-beta-language-pack-packaging-build-smoke
Status: build output smoke wrapper
Scope: smoke helper and documentation only; no runtime changes, no UI changes, no licensing changes

## Goal

This milestone adds a safe wrapper for checking language-pack files in an existing standalone ZIP build output.

## What changed

- Adds docs/language-packs/LANGUAGE-PACK-PACKAGING-BUILD-SMOKE.md
- Adds scripts/release/smoke-language-pack-build-output.ps1

## What this milestone does not do

- does not build a standalone ZIP automatically
- does not modify build-portable-runtime.ps1
- does not modify test-standalone-runtime.ps1
- does not modify runtime behavior
- does not change UI behavior
- does not add a LICENSE
- does not modify the validated v0.2.0-public-beta release assets

## Smoke helper behavior

The helper can:

- check an explicit ZIP with -ZipPath
- check a ZIP by -VersionTag inside -ReleaseRoot
- find the latest Voila ZIP inside -ReleaseRoot
- skip cleanly when no ZIP exists if -SkipIfMissing is used

## Commands

Check latest local ZIP:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1

Check explicit ZIP:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -ZipPath D:\dev\releases\voila-some-version.zip

Check by version tag:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -VersionTag voila-v0.1.9-final-release-polish

Safe validation mode when no local ZIP may exist:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -SkipIfMissing

## Required files checked inside ZIP

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Safety

The script does not create release artifacts.

The script only inspects an existing ZIP or skips cleanly when -SkipIfMissing is used.

ZIP extraction happens in a temporary folder and is removed unless -KeepTemp is used.

## Validation

Run from repository root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -SkipIfMissing
powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -IncludeSamples
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

v0.2.34-public-beta-language-pack-packaging-build-verification-docs

## Decision for this milestone

For v0.2.33-public-beta-language-pack-packaging-build-smoke, the correct action is to add a build-output smoke wrapper only.

Do not change runtime or UI in this milestone.
