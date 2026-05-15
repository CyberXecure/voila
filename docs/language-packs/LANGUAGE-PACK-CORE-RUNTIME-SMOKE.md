# Voila! Language Pack Core Runtime Smoke

Milestone: v0.2.23-public-beta-language-pack-core-runtime-smoke  
Status: core runtime smoke test  
Scope: docs and smoke script only; no UI changes, no packaging changes, no licensing changes

## Goal

This milestone adds a CLI smoke test for the core-first language pack runtime helper.

The goal is to verify that the isolated helper prefers `language-packs/core/` and safely falls back to `language-packs/samples/`.

## Files added

- docs/language-packs/LANGUAGE-PACK-CORE-RUNTIME-SMOKE.md
- scripts/language-packs/smoke-core-runtime-helper.py

## What the smoke test checks

The smoke test verifies:

- core language pack directory exists
- sample language pack directory exists
- Romanian and English core packs are loaded
- Romanian and English sample packs remain available
- `button.save` resolves from core for Romanian
- `button.save` resolves from core for English
- unsupported language falls back to English core
- placeholder replacement works from core packs
- missing keys use caller-provided default text
- missing keys without default return the key
- sample fallback works when core is unavailable
- core overrides sample when both are available

## Validation command

Run from repository root:

python .\scripts\language-packs\smoke-core-runtime-helper.py

Expected result:

Core runtime helper smoke test passed.

## Full validation block

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Safety

This milestone only adds smoke coverage.

It does not:

- change UI behavior
- change `/ui-language`
- change OCR processing
- change PDF processing
- change export behavior
- change packaging
- add dependencies
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Recommended next milestone

v0.2.24-public-beta-language-pack-core-runtime-docs

## Decision for this milestone

For v0.2.23-public-beta-language-pack-core-runtime-smoke, the correct action is to add smoke testing only.

Do not change UI or packaging in this milestone.
