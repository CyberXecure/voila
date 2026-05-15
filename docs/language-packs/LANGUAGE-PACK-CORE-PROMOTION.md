# Voila! Language Pack Core Promotion

Milestone: v0.2.20-public-beta-language-pack-core-promotion  
Status: first core language pack promotion  
Scope: language-pack data and validator update only; no packaging changes, no selector changes, no licensing changes

## Goal

This milestone creates the first core Voila! language packs.

The first promoted core packs are:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

They are promoted from the reviewed sample packs, while samples remain unchanged.

## Non-goals

This milestone does not:

- switch the application runtime fully from samples to core
- change standalone packaging
- add a new language selector
- change OCR processing
- change PDF processing
- change export behavior
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Files added

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- docs/language-packs/LANGUAGE-PACK-CORE-PROMOTION.md

## Files changed

- scripts/language-packs/validate-language-packs.py

## Validator update

The validator now checks:

- language-packs/samples/*.language-pack.sample.json
- language-packs/core/*.language-pack.json

Core packs are optional for older branches, but when present they are validated.

## Why only ro/en

Romanian and English are promoted first because they are the base/fallback languages.

Other languages remain planned until reviewed.

## Runtime policy

This milestone does not change runtime source paths.

Runtime/source switching should be handled in a separate small milestone after core validation is stable.

## Packaging policy

This milestone does not change packaging.

Standalone inclusion of core packs must be planned and tested separately.

## Validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Rollback

This change can be reverted in one PR.

Samples remain unchanged, so the previous sample-based validation flow remains recoverable.

## Recommended next milestone

v0.2.21-public-beta-language-pack-core-runtime-plan

Suggested next work:

- plan whether runtime should read from core or samples
- add tests for core pack loading
- keep packaging unchanged until runtime source is stable

## Decision for this milestone

For v0.2.20-public-beta-language-pack-core-promotion, the correct action is to create ro/en core packs and update validation only.

Do not change packaging in this milestone.
