# Voila! Language Pack Packaging Check

Milestone: v0.2.25-public-beta-language-pack-packaging-check
Status: packaging check only
Scope: docs and smoke script only; no packaging changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone documents and checks the language pack files that must be considered before future standalone packaging work.

## Non-goals

This milestone does not:

- change standalone packaging
- modify installer scripts
- modify runtime startup scripts
- change OCR processing
- change PDF processing
- change export behavior
- add a language selector
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Current files that should be considered for future packaging

Core language packs:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Sample language packs:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

Schema:

- language-packs/schema/language-pack.schema.json

Runtime helper:

- language-packs/runtime/minimal_language_runtime.py

Smoke tools:

- scripts/language-packs/validate-language-packs.py
- scripts/language-packs/test_language_pack_runtime.py
- scripts/language-packs/test_minimal_language_runtime.py
- scripts/language-packs/smoke-ui-language-endpoint.py
- scripts/language-packs/smoke-core-runtime-helper.py
- scripts/language-packs/smoke-language-pack-files.py

## Packaging risk

Future standalone packaging must not assume development-only paths.

Before packaging integration, verify:

- core packs are included
- schema is included if runtime validation needs it
- runtime helper can locate packs in packaged mode
- app still starts if language packs are missing
- app still starts if one language pack is invalid
- fallback behavior remains safe
- no internet access is required

## Smoke command

Run from repository root:

python .\scripts\language-packs\smoke-language-pack-files.py

Expected result:

Language pack file smoke test passed.

## Full validation block

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Recommended next milestone

v0.2.26-public-beta-language-pack-packaging-plan

## Decision for this milestone

For v0.2.25-public-beta-language-pack-packaging-check, the correct action is to add documentation and a file-level smoke check only.

Do not modify packaging in this milestone.
