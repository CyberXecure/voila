# Voila! UI Remaining Core Key Plan

Milestone: v0.2.61-public-beta-language-pack-ui-remaining-core-key-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the safe future addition of the remaining UI/message/status keys to the core Romanian and English language packs.

The goal is to prepare the next implementation milestone without modifying JSON files yet.

## Baseline

This plan builds on:

- v0.2.59 remaining-label inventory
- v0.2.60 remaining key plan

## Target files for a future implementation

The future implementation should update only:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

The future tests should be added separately or in the same implementation milestone if kept small.

## Proposed key groups

The future core language-pack update should add:

```text
ui.*
message.*
status.*
```

## Future ui.* keys

Planned short UI labels:

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

## Future message.* keys

Planned helper/description text keys:

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

## Future status.* keys

Planned state/meta keys:

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

## Safety rules for future implementation

The future implementation should:

- preserve existing JSON structure
- add keys under the existing `messages` object unless a schema-backed alternative already exists
- keep Romanian and English key sets identical
- preserve existing legacy fallback keys
- avoid removing or renaming existing keys
- avoid schema changes unless validation proves they are required
- avoid UI code changes in the same milestone unless explicitly planned

## Required tests for future implementation

Future implementation should add or update tests to verify:

```text
ro/en key parity
all planned ui.* keys exist
all planned message.* keys exist
all planned status.* keys exist
unsupported language fallback still works
missing key fallback still works
```

Suggested future helper:

```text
scripts/language-packs/test_ui_remaining_core_keys.py
```

Suggested future smoke helper:

```text
scripts/language-packs/smoke-ui-remaining-core-keys.py
```

## Validation required after future implementation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python .\scripts\language-packs\smoke-ui-core-keys.py
python .\scripts\language-packs\smoke-minimal-ui-key-integration.py
python .\scripts\language-packs\smoke-ui-expansion-key-integration.py
python .\scripts\language-packs\smoke-ui-next-batch-key-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
```

If new helpers are added, run them too.

## Recommended next milestone

```text
v0.2.62-public-beta-language-pack-ui-remaining-core-keys
```

Suggested next work:

- add the planned keys to Romanian and English core language packs
- add parity tests
- add smoke test
- keep UI code unchanged
- keep schema unchanged unless validation requires otherwise

## Non-goals

This milestone does not:

- modify UI code
- modify language-pack JSON
- modify runtime behavior
- modify schema
- add a language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.61 is documentation only.

It plans the safe future core language-pack key implementation.
