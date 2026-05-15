# Voila! Language Pack Minimal UI Expansion

Milestone: v0.2.18-public-beta-language-pack-minimal-ui-expansion  
Status: minimal UI expansion  
Scope: small OCR Monaco UI tooltip expansion, no selector changes, no packaging changes, no licensing changes

## Goal

This milestone expands the minimal language-pack UI proof with a very small set of additional UI aliases.

The goal is to prove that language-pack-style aliases can cover both visible labels and tooltip/title text while keeping legacy fallback behavior.

## What changed

This milestone adds language-pack-style tooltip aliases for the OCR Monaco review toolbar:

- tooltip.run_ocr_page
- tooltip.check_text
- tooltip.save

Each alias maps to an existing legacy key:

- run_ocr_page_title
- check_text_title
- save_title

## Files changed

- services/api/i18n.py
- services/api/static/ocr_review_monaco.js
- scripts/language-packs/smoke-ui-language-endpoint.py
- docs/language-packs/LANGUAGE-PACK-MINIMAL-UI-EXPANSION.md

## Safety

This milestone does not:

- add a new endpoint
- add a new language selector
- expand localization across the whole app
- change OCR processing
- change PDF processing
- change export behavior
- change packaging
- add dependencies
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Runtime behavior

The OCR Monaco toolbar now uses language-pack-style aliases for three tooltip strings.

Example:

tr("tooltip.save", "save_title")

Resolution order:

1. tooltip.save
2. save_title
3. tooltip.save

If the new alias is missing, the legacy fallback remains available.

## Validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Manual UI smoke test

Open the OCR Monaco review UI and verify:

- Run page OCR button still appears
- Check text button still appears
- Save button still appears
- button tooltips still appear
- interface language selector still works
- OCR behavior is unchanged

## Rollback

This change can be reverted in one PR.

Legacy fallback keys remain available.

## Recommended next milestone

v0.2.19-public-beta-language-pack-core-promotion-plan

Suggested next work:

- decide whether samples should be promoted to core language packs
- keep packaging unchanged until the core pack layout is stable
- avoid broad UI localization until smoke tests stay stable

## Decision for this milestone

For v0.2.18-public-beta-language-pack-minimal-ui-expansion, the correct action is a very small UI alias expansion only.

Do not localize the full UI in this milestone.
