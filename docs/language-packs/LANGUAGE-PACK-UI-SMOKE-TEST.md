# Voila! Language Pack UI Smoke Test

Milestone: v0.2.17-public-beta-language-pack-ui-smoke-test  
Status: UI language smoke test / no new UI integration  
Scope: smoke testing only, no packaging changes, no licensing changes

## Goal

This milestone adds a smoke test for the minimal UI language-pack proof added in v0.2.16.

The goal is to verify that language-pack-style UI aliases are available through the existing i18n flow before expanding UI localization.

## Non-goals

This milestone does not:

- add new UI strings
- expand UI localization
- add a language selector
- change OCR processing
- change PDF processing
- change export behavior
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-UI-SMOKE-TEST.md
- scripts/language-packs/smoke-ui-language-endpoint.py

## What the smoke test checks

The smoke test verifies that:

- services/api/i18n.py imports successfully
- all planned UI languages are available
- language-pack-style alias keys are present
- legacy fallback keys are still present
- alias values match their legacy fallback values
- important OCR Monaco UI aliases are available
- optional /ui-language endpoint response contains alias keys when the API is running

## Alias keys checked

The smoke test checks:

- ui.language
- document.language
- button.run_ocr_page
- button.check_text
- button.save
- button.prev_issue
- button.next_issue
- status.editor_loading
- status.editor_ready
- status.lt_checking
- status.lt_no_issues
- message.lt_apply_again

## Legacy fallback keys checked

The smoke test checks that these legacy keys still exist:

- ui_language
- document_language
- run_ocr_page
- check_text
- save
- prev_issue
- next_issue
- editor_loading
- editor_ready
- lt_checking
- lt_no_issues
- lt_apply_again

## Run local module smoke test

From repository root:

python .\scripts\language-packs\smoke-ui-language-endpoint.py

Expected result:

UI language smoke test passed.

## Optional endpoint smoke test

If the local API is running, also run:

python .\scripts\language-packs\smoke-ui-language-endpoint.py --url http://127.0.0.1:8787/ui-language

The exact port should match the current Voila! local runtime.

## Validation commands

Recommended full validation block:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Safety

This milestone only adds a smoke test and documentation.

It does not change the UI implementation.

## Recommended next milestone

v0.2.18-public-beta-language-pack-minimal-ui-expansion

Suggested next work:

- expand only a few additional safe UI labels
- keep legacy fallback keys
- avoid full UI localization
- avoid packaging changes
- run this smoke test before and after changes

## Decision for this milestone

For v0.2.17-public-beta-language-pack-ui-smoke-test, the correct action is to add smoke testing only.

No new application UI behavior should be added in this milestone.
