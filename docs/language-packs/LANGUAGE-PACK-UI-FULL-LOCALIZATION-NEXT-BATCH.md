# Voila! UI Full Localization Next Batch

Milestone: v0.2.92-public-beta-language-pack-ui-full-localization-next-batch-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the next full UI localization integration batch completed in v0.2.91.

The integration used existing core language-pack keys from v0.2.90 and localized a small, controlled set of remaining links, short UI messages, and one page title.

## Implemented in v0.2.91

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-full-localization-next-batch.py
```

Core keys used from v0.2.90:

```text
ui.link.*
ui.message.*
ui.title.*
```

## Integrated UI groups

The next batch integrated selected literals from:

```text
pagination/navigation links
remaining simple study/course/concepts links
short OCR review navigation links
small safe empty-state/help paragraphs
one static title literal
```

## Representative link keys

```text
ui.link.previous
ui.link.prev
ui.link.next
ui.link.back_to_ocr_review
ui.link.study
ui.link.concepts
```

## Representative message keys

```text
ui.message.local_pdf_learning_studio
ui.message.generate_study_quiz_first
ui.message.crop_editor_port_not_responding
ui.message.no_study_questions_found
ui.message.concept_title_cannot_be_empty
ui.message.correction_not_saved_exception
ui.message.ocr_corrections_applied
ui.message.no_pdfs_found
```

## Representative title key

```text
ui.title.correct_ocr
```

## Safety choices

The v0.2.91 implementation intentionally preserved:

```text
fallback English text
route behavior
HTTP status codes
URLs
query strings
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

Future localization work must continue to escape dynamic HTML values.

## Validation coverage

The next-batch smoke helper verifies that selected full UI localization snippets are present in `services/api/web_app.py`, that representative old hardcoded literals are no longer present for the chosen batch, and that the v0.2.81 HTML escaping fix remains present.

## Validation commands

v0.2.91 passed:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py
python .\scripts\language-packs\test_ui_error_status_core_keys.py
python .\scripts\language-packs\test_ui_full_localization_core_keys.py
python .\scripts\language-packs\test_ui_full_localization_next_batch_core_keys.py
python .\scripts\language-packs\smoke-ui-full-localization-core-keys.py
python .\scripts\language-packs\smoke-ui-full-localization-first-batch.py
python .\scripts\language-packs\smoke-ui-full-localization-next-batch-core-keys.py
python .\scripts\language-packs\smoke-ui-full-localization-next-batch.py
python .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py
python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-full-localization-next-batch.py
```

## What was intentionally not changed

v0.2.91 did not add:

- language-pack JSON changes
- schema changes
- broad UI rewrites
- language selector
- browser-locale detection
- persisted language preference
- adaptive UI switching
- GitHub release upload
- Git tag
- public ZIP publish
- LICENSE changes

## Recommended next milestone

```text
v0.2.93-public-beta-language-pack-ui-full-localization-remaining-inventory
```

Suggested next work:

- inspect remaining non-localized UI literals after v0.2.91
- separate true user-facing text from mixed dynamic/developer/debug text
- plan only a small follow-up batch if useful
- keep planning documentation-only before adding more keys or integrations

## Decision

v0.2.92 documents the completed v0.2.91 next full UI localization integration batch.
