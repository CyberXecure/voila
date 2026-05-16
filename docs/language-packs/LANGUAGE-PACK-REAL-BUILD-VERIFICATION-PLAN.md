# Voila! Language Pack Real Build Verification Plan

Milestone: v0.2.35-public-beta-language-pack-real-build-verification-plan
Status: real build verification planning
Scope: documentation only; no build execution, no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone documents the safe plan for the first real standalone ZIP build after language-pack packaging checks were added.

## Non-goals

This milestone does not:

- run build-portable-runtime.ps1
- create a new standalone ZIP
- modify build-portable-runtime.ps1
- modify test-standalone-runtime.ps1
- modify release assets
- modify runtime behavior
- modify UI behavior
- add or modify LICENSE files
- modify the existing v0.2.0-public-beta release

## Why this plan exists

Language-pack packaging checks are now integrated and documented. The next risky step is the first real ZIP build that should include:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

This plan keeps that first real build separate from runtime/UI changes.

## Pre-build requirements

Before running a real build, verify:

- main branch is clean
- no pull requests are open
- source language-pack inspection passes
- packaging readiness dry-run passes
- standalone source dry-run smoke passes
- build-output smoke safe mode skips cleanly without explicit ZIP
- language-pack validator passes
- runtime tests pass
- UI smoke test passes
- core runtime smoke test passes
- language-pack file smoke test passes
- PowerShell release scripts parse successfully

## Pre-build validation commands

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

## Real build command

The future real build should be run intentionally, not as part of this milestone.

Expected future command:

powershell -ExecutionPolicy Bypass -File .\scripts\release\build-portable-runtime.ps1

## Expected new ZIP behavior

The new ZIP should include the required language-pack files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

The build should fail before ZIP creation if required language-pack files are missing from the staged app root.

## Post-build verification order

After a real ZIP is created, verify it in this order:

1. smoke-language-pack-build-output.ps1 -ZipPath <ZIP_PATH>
2. smoke-language-pack-standalone-package.ps1 -ZipPath <ZIP_PATH>
3. test-standalone-runtime.ps1 against the ZIP
4. manual launch test only after automated checks pass

## Post-build commands

Use the real ZIP path produced by the build.

Example:

powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-build-output.ps1 -ZipPath <ZIP_PATH>
powershell -ExecutionPolicy Bypass -File .\scripts\release\smoke-language-pack-standalone-package.ps1 -ZipPath <ZIP_PATH>

Then run the existing standalone runtime test according to the release process:

powershell -ExecutionPolicy Bypass -File .\scripts\release\test-standalone-runtime.ps1

## Expected failures

Old ZIPs created before language-pack packaging are expected to fail language-pack checks.

This is normal and should not be treated as a regression.

## Release asset safety

The first real build should not overwrite or mutate existing public-beta release assets.

Recommended safety rules:

- write the new ZIP to a clearly versioned path
- keep existing v0.2.0-public-beta assets unchanged
- do not upload new assets until ZIP verification passes
- do not tag a new public release from an unverified ZIP

## Recommended future milestone

v0.2.36-public-beta-language-pack-real-build-dry-run

Suggested next work:

- run a controlled local build
- capture the produced ZIP path
- verify language-pack files inside the ZIP
- keep runtime/UI unchanged

## Decision for this milestone

For v0.2.35-public-beta-language-pack-real-build-verification-plan, the correct action is documentation only.

Do not run a real build in this milestone.
