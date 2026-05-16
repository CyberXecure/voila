# Voila! Language Pack Packaging Script Integration Checklist

Milestone: v0.2.30-public-beta-language-pack-packaging-script-integration-plan
Status: integration planning checklist
Scope: documentation only; no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This checklist defines the go/no-go requirements before actual language-pack packaging script integration.

## Go criteria

Actual packaging script integration can begin only if:

- main branch is clean
- no unrelated PRs are open
- packaging inspection passes
- packaging readiness dry-run passes without samples
- packaging readiness dry-run passes with samples
- language pack validator passes
- runtime tests pass
- minimal runtime tests pass
- UI smoke test passes
- core runtime smoke test passes
- language pack file smoke test passes
- build-portable-runtime.ps1 insertion point is documented
- test-standalone-runtime.ps1 insertion point is documented

## No-go criteria

Do not integrate packaging scripts if:

- working tree is dirty
- checks fail
- required core packs are missing
- schema is missing
- staged AppDir path is unclear
- extracted AppRoot path is unclear
- changes would modify v0.2.0-public-beta release assets
- changes would mix packaging with runtime or UI localization
- changes would require LICENSE updates

## Required validation before future implementation

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

Optional:

node --check .\services\api\static\ocr_review_monaco.js

## Future build script checklist

When build-portable-runtime.ps1 is changed later, verify:

- language-packs/core remains in AppDir before ZIP
- language-packs/schema remains in AppDir before ZIP
- inspect-language-pack-packaging.ps1 passes against AppDir
- cleanup does not remove language-packs
- final ZIP includes required language-pack files
- ZIP creation still succeeds

## Future standalone test checklist

When test-standalone-runtime.ps1 is changed later, verify:

- requiredFiles includes language-pack core/schema files
- inspection runs against extracted AppRoot
- missing language-pack files fail clearly
- health check still passes
- LanguageTool check still passes
- Tesseract check still passes
- stop flow still closes ports

## Rollback policy

Future script integration must be reversible in one PR.

Rollback should not require:

- database migration
- user settings migration
- release asset mutation
- license changes
- remote service changes

## Decision for this milestone

For v0.2.30-public-beta-language-pack-packaging-script-integration-plan, this checklist is documentation only.

No release scripts should be changed.
