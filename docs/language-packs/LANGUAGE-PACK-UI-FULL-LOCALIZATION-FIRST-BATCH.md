# Voila! UI Full Localization First Batch

Milestone: v0.2.88-public-beta-language-pack-ui-full-localization-first-batch-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the first full UI localization integration batch completed in v0.2.87.

The integration used existing core language-pack keys from v0.2.86 and localized a small, controlled set of static headings, simple links, simple buttons, and one safe form label.

## Implemented in v0.2.87

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-full-localization-first-batch.py
```

Core keys used from v0.2.86:

```text
ui.heading.*
ui.button.*
ui.link.*
ui.label.*
```

## Integrated UI groups

The first batch integrated selected literals from:

```text
static headings
simple navigation/link labels
simple button labels
one safe form label
```

## Representative heading keys

```text
ui.heading.home
ui.heading.review
ui.heading.review_question
ui.heading.no_review_questions
ui.heading.review_weak_concepts
ui.heading.progress
ui.heading.progress_dashboard
ui.heading.crop_editor_not_started
ui.heading.source_page
ui.heading.editable_ocr_text
ui.heading.suspicious_pages
```

## Representative button keys

```text
ui.button.save_page_correction
ui.button.save_reviewed_page
ui.button.save_as_needs_review
ui.button.apply_corrected_ocr
```

## Representative link keys

```text
ui.link.back
ui.link.next_review
ui.link.study
ui.link.progress
ui.link.continue_study
ui.link.course_tools
ui.link.top
ui.link.bottom
ui.link.back_to_voila
ui.link.reload
ui.link.concepts
ui.link.course
ui.link.review_ocr
```

## Representative label key

```text
ui.label.correct_concept_title
```

## Safety choices

The v0.2.87 implementation intentionally preserved:

```text
fallback English text
route behavior
HTTP status codes
dynamic values
existing _ut(...) helper behavior
existing language-pack JSON
existing schema
v0.2.81 _html_escape(str(page)) reflected-XSS fix
```

The implementation intentionally avoided:

```text
broad UI rewrite
language selector
browser-locale detection
persisted language preference
adaptive UI switching
generated content changes
OCR output changes
course output changes
release upload
Git tag
public ZIP publish
LICENSE changes
```

## Security note

The v0.2.81 page-not-found fix remains the reference rule for dynamic values inserted into HTML:

```text
_html_escape(str(page))
```

Future localization work must keep escaping dynamic HTML values.

## Validation coverage

The new first-batch smoke helper verifies that selected full UI localization snippets are present in `services/api/web_app.py`, that representative old hardcoded literals are no longer present for the chosen batch, and that the v0.2.81 HTML escaping fix remains present.

## Validation commands

v0.2.87 passed:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py
python .\scripts\language-packs\test_ui_error_status_core_keys.py
python .\scripts\language-packs\test_ui_full_localization_core_keys.py
python .\scripts\language-packs\smoke-ui-full-localization-core-keys.py
python .\scripts\language-packs\smoke-ui-full-localization-first-batch.py
python .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py
python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-full-localization-first-batch.py
```

## What was intentionally not changed

v0.2.87 did not add language-pack JSON changes, schema changes, broad UI rewrites, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Recommended next milestone

```text
v0.2.89-public-beta-language-pack-ui-full-localization-next-batch-plan
```

Suggested next work:

- inspect remaining non-localized UI literals after v0.2.87
- plan the next small route-based batch
- keep planning documentation-only before adding more keys or integrations

## Decision

v0.2.88 documents the completed v0.2.87 first full UI localization integration batch.
