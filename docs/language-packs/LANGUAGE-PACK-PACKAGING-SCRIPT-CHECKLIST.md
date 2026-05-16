# Voila! Language Pack Packaging Script Plan Checklist

Milestone: v0.2.28-public-beta-language-pack-packaging-script-plan
Status: packaging script planning checklist
Scope: documentation only; no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This checklist defines the conditions before changing release scripts for language-pack packaging.

## Go criteria for a future script change

A future packaging script PR can begin only if:

- main branch is clean
- no unrelated PRs are open
- language pack validator passes
- runtime tests pass
- UI smoke test passes
- core runtime smoke test passes
- language pack file smoke test passes
- packaging inspection passes
- build-portable-runtime.ps1 insertion point is identified
- test-standalone-runtime.ps1 required file update is planned

## No-go criteria

Do not change packaging scripts if:

- working tree is dirty
- tests fail
- language-pack source files are missing
- packaged app root behavior is unclear
- runtime path handling is unclear
- changes would touch v0.2.0-public-beta release assets
- changes would require LICENSE updates
- changes mix packaging with UI/runtime localization

## Required current validation commands

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python -m py_compile .\services\api\i18n.py

Optional:

node --check .\services\api\static\ocr_review_monaco.js

## Future build script checklist

When build-portable-runtime.ps1 is changed later, verify:

- language-packs/core is present in staging
- language-packs/schema is present in staging
- packaged inspection passes against staging app root
- final ZIP contains required language-pack files
- cleanup does not remove language-packs
- no local developer paths are required

## Future standalone test checklist

When test-standalone-runtime.ps1 is changed later, verify:

- required language-pack files are checked
- packaged inspection runs against extracted app root
- missing language packs cause a clear failure
- smoke test still verifies health, LanguageTool, and Tesseract

## Rollback policy

Future script changes must be reversible in one PR.

Rollback should not require:

- database migration
- user settings migration
- release asset mutation
- license changes
- remote service changes

## Decision for this milestone

For v0.2.28-public-beta-language-pack-packaging-script-plan, this checklist is documentation only.

No release scripts should be changed.
