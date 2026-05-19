# Voila! UI Status / Message Integration Plan

Milestone: v0.2.67-public-beta-language-pack-ui-status-message-integration-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the next small UI integration batch for existing `message.*` and `status.*` core language-pack keys.

The goal is to identify low-risk helper text and status/meta text that can be safely integrated later without changing generated content, logs, debug output, or error handling behavior.

## Baseline

This plan builds on:

- v0.2.62 remaining core keys
- v0.2.63 remaining core key documentation
- v0.2.64 remaining UI integration plan
- v0.2.65 first remaining UI integration batch
- v0.2.66 UI remaining integration documentation

## Candidate key groups

The next integration should focus on:

```text
message.*  longer helper/card/description text
status.*   status, notice, and meta labels
```

## Recommended first message.* batch

Use only exact card/helper descriptions that are visible and stable.

Recommended candidates:

```text
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
```

## Recommended first status.* batch

Use only simple visible status/meta labels.

Recommended candidates:

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
```

## Defer from first implementation batch

The following should not be patched in the first status/message implementation batch:

```text
status.missing_pdf_name
status.no_ocr_pages_found
status.rebuild_complete
status.rebuild_failed
status.save_title_override_failed
status.save_ocr_text_failed
message.apply_corrected_ocr_warning
```

Reason:

```text
These are closer to error/status route output or potentially sensitive workflow actions.
They should be handled in a later focused error/status milestone.
```

## Safety rules for future implementation

The future implementation should:

- patch only exact visible helper/status text
- use existing `_ut(...)` helper
- preserve existing fallback text
- avoid generated course content
- avoid OCR output
- avoid logs
- avoid debug/developer text
- avoid broad UI rewrite
- keep core language-pack JSON unchanged
- keep schema unchanged
- add a focused smoke helper

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-status-message-integration.py
```

It should verify that:

- selected `message.*` keys are used in `services/api/web_app.py`
- selected `status.*` keys are used in `services/api/web_app.py`
- selected old hardcoded helper/status snippets are removed only where intentionally replaced
- deferred error/debug/log/generated text remains unchanged

## Recommended validation after future implementation

Run:

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
python .\scripts\language-packs\smoke-ui-remaining-integration.py
python .\scripts\language-packs\smoke-ui-status-message-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-status-message-integration.py
```

## Recommended next milestone

```text
v0.2.68-public-beta-language-pack-ui-status-message-integration
```

Suggested next work:

- patch the selected low-risk `message.*` helper/card descriptions
- patch the selected low-risk `status.*` meta labels
- add `smoke-ui-status-message-integration.py`
- keep language-pack JSON unchanged
- keep schema unchanged
- avoid full UI localization

## Non-goals

This milestone does not:

- modify UI code
- modify language-pack JSON
- modify runtime behavior
- modify schema
- add language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.67 is documentation only.

It plans the next small status/message UI integration batch using existing core keys.
