# Voila! UI Remaining Core Keys

Milestone: v0.2.63-public-beta-language-pack-ui-remaining-core-key-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the core language-pack key implementation completed in v0.2.62.

The implementation added the remaining planned UI, helper/message, and status/meta keys to the Romanian and English core language packs.

## Implemented in v0.2.62

Updated files:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

Added validation helpers:

```text
scripts/language-packs/test_ui_remaining_core_keys.py
scripts/language-packs/smoke-ui-remaining-core-keys.py
```

## Added key groups

v0.2.62 added planned keys in three groups:

```text
ui.*       short visible UI labels
message.*  longer helper/description text
status.*   state, notice, and meta labels
```

## ui.* keys

The following short UI labels were added to both Romanian and English core packs:

```text
ui.back
ui.tools
ui.course
ui.lessons
ui.library
ui.logs
ui.course_tools
ui.quick_tools
ui.study_mode
ui.review_ocr_text
ui.review_concepts
ui.review_study_concepts
ui.correct_ocr_text
ui.continue_study
ui.toggle_theme
ui.save_title_override
ui.save_page_correction
ui.save_reviewed_page
ui.save_as_needs_review
ui.apply_corrected_ocr
ui.fit_width
```

## message.* keys

The following longer helper/description keys were added:

```text
message.choose_pdf_helper
message.no_pdf_files_found
message.open_course_description
message.lessons_description
message.study_mode_description
message.review_ocr_text_description
message.review_concepts_description
message.edit_crops_description
message.figures_description
message.progress_description
message.return_to_library_description
message.source_mode_description
message.apply_corrected_ocr_warning
```

## status.* keys

The following status/meta keys were added:

```text
status.uploaded
status.not_generated_yet
status.no_suspicious_pages_detected
status.focused_concept
status.attempts
status.status
status.study_coverage
status.overall_mastery
status.concept_status
status.missing_pdf_name
status.no_ocr_pages_found
status.rebuild_complete
status.rebuild_failed
status.save_title_override_failed
status.save_ocr_text_failed
```

## Validation coverage

The new unit test verifies:

- Romanian and English packs contain all planned keys
- planned Romanian and English key sets match
- planned values are non-empty strings
- representative Romanian and English values are correct

The new smoke helper verifies:

- all required remaining `ui.*`, `message.*`, and `status.*` keys exist
- all required values are non-empty in both core packs

## Validation commands

v0.2.62 passed:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py

python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python .\scripts\language-packs\smoke-ui-core-keys.py
python .\scripts\language-packs\smoke-minimal-ui-key-integration.py
python .\scripts\language-packs\smoke-ui-expansion-key-integration.py
python .\scripts\language-packs\smoke-ui-next-batch-key-integration.py
python .\scripts\language-packs\smoke-ui-remaining-core-keys.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\test_ui_remaining_core_keys.py
python -m py_compile .\scripts\language-packs\smoke-ui-remaining-core-keys.py
```

## What was intentionally not changed

v0.2.62 did not add:

- UI code changes
- runtime behavior changes
- schema changes
- language selector
- browser-locale detection
- persisted language preference
- adaptive UI switching
- GitHub release upload
- Git tag
- public ZIP publish
- LICENSE changes

## Remaining work

The keys now exist in the core packs, but not all remaining UI surfaces use them yet.

Future work should integrate them in small UI batches only.

Potential next work:

```text
ui.logs
ui.course_tools
ui.quick_tools
ui.tools
ui.course
ui.study_mode
ui.review_ocr_text
ui.review_concepts
ui.review_study_concepts
ui.correct_ocr_text
message.* card/helper descriptions
status.* notice/meta labels
```

## Recommended next milestone

```text
v0.2.64-public-beta-language-pack-ui-remaining-integration-plan
```

Suggested next work:

- plan the first small UI integration batch using the newly available keys
- keep implementation deferred
- select only low-risk visible labels
- avoid broad UI rewrite
- preserve legacy fallbacks where already used

## Decision

v0.2.63 documents the v0.2.62 remaining core key implementation.

The project now has core Romanian and English language-pack coverage for the remaining planned `ui.*`, `message.*`, and `status.*` keys.
