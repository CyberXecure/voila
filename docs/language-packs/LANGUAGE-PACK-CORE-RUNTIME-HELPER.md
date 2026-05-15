# Voila! Language Pack Core Runtime Helper

Milestone: v0.2.22-public-beta-language-pack-core-runtime-helper  
Status: isolated runtime helper update  
Scope: runtime helper and tests only; no UI changes, no packaging changes, no licensing changes

## Goal

This milestone updates the isolated minimal language pack runtime helper so that it can prefer core language packs while still falling back to sample packs.

The application UI is not changed in this milestone.

## What changed

The minimal helper now supports:

- core pack loading from language-packs/core/
- sample fallback loading from language-packs/samples/
- core-first translation lookup
- sample fallback when core packs are missing
- lookup source reporting for tests
- legacy single-directory loading for older tests

## Preferred fallback order

The isolated helper now follows this order:

1. selected language from core
2. English from core
3. Romanian from core
4. selected language from samples
5. English from samples
6. Romanian from samples
7. caller-provided default text
8. key

## Files changed

- language-packs/runtime/minimal_language_runtime.py
- scripts/language-packs/test_minimal_language_runtime.py

## Files added

- docs/language-packs/LANGUAGE-PACK-CORE-RUNTIME-HELPER.md

## Non-goals

This milestone does not:

- change OCR Monaco UI behavior
- change /ui-language behavior
- switch the full application runtime to core packs
- change standalone packaging
- add a new language selector
- change PDF processing
- change OCR processing
- change export behavior
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Safety

The change is isolated to the language-pack helper and tests.

The existing samples remain available.

The helper tolerates missing core and sample directories.

Invalid packs are ignored by the safe loader.

## Validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Recommended next milestone

v0.2.23-public-beta-language-pack-core-runtime-smoke

Suggested next work:

- add a small smoke script for core-first runtime behavior
- verify core fallback explicitly from CLI
- avoid UI and packaging changes until helper behavior remains stable

## Decision for this milestone

For v0.2.22-public-beta-language-pack-core-runtime-helper, the correct action is to update the isolated helper and tests only.

Do not change UI or packaging in this milestone.
