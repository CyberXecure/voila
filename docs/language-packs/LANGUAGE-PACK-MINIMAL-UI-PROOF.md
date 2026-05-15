# Voila! Language Pack Minimal UI Proof

Milestone: v0.2.16-public-beta-language-pack-minimal-ui-proof  
Status: minimal UI proof  
Scope: very small UI integration, no language selector changes, no packaging changes, no licensing changes

## Goal

This milestone proves that Voila! can use language-pack-style translation keys in an existing UI area without replacing the full interface.

The implementation is intentionally small and reversible.

## What changed

This milestone adds language-pack-style alias keys to the existing OCR Monaco review UI translation flow.

Examples:

- button.save
- button.check_text
- button.run_ocr_page
- button.prev_issue
- button.next_issue
- ui.language
- document.language

The existing legacy keys remain available as fallback.

Examples:

- save
- check_text
- run_ocr_page
- prev_issue
- next_issue
- ui_language
- document_language

## Files changed

- services/api/static/ocr_review_monaco.js
- services/api/i18n.py
- docs/language-packs/LANGUAGE-PACK-MINIMAL-UI-PROOF.md

## Safety

This milestone does not:

- add a new language selector
- add a new endpoint
- change OCR processing
- change PDF processing
- change export behavior
- change packaging
- add dependencies
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Runtime behavior

The UI translation helper now supports:

- language-pack-style keys
- fallback to existing legacy keys
- fallback to the key itself if no translation exists

Example:

tr("button.save", "save")

This first checks:

1. button.save
2. save
3. button.save

## Why this is safe

The existing UI already uses translations loaded from /ui-language.

This milestone only adds alias keys and updates a few toolbar labels to use the new key style with legacy fallback.

If the new keys are missing, the old keys still work.

## Validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Manual UI smoke test

Open the OCR review UI and verify:

- interface language selector still appears
- document language selector still appears
- Run page OCR button still appears
- Check text button still appears
- Save button still appears
- changing UI language still updates labels
- OCR processing behavior is unchanged

## Rollback

This milestone can be reverted in one PR.

The old translation keys remain available, so rollback risk is low.

## Recommended next milestone

v0.2.17-public-beta-language-pack-ui-smoke-test

Suggested next work:

- add a small smoke checklist or script for the OCR Monaco UI
- verify /ui-language returns language-pack-style aliases
- avoid broad UI localization until this proof is stable

## Decision for this milestone

For v0.2.16-public-beta-language-pack-minimal-ui-proof, the correct action is a minimal proof only.

Do not localize the full UI in this milestone.
