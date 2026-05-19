# Voila! UI Error / Status Integration Plan

Milestone: v0.2.74-public-beta-language-pack-ui-error-status-integration-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the first small UI integration batch for visible error/status route output.

The goal is to use the core language-pack keys added in v0.2.72, but keep implementation deferred to a later milestone.

## Baseline

This plan builds on:

- v0.2.70 UI error/status plan
- v0.2.71 error/status core key plan
- v0.2.72 error/status core key implementation
- v0.2.73 error/status core key documentation

## Recommended first integration batch

The first implementation batch should patch only simple, static, visible route output.

Recommended keys:

```text
error.missing_pdf_name
error.no_ocr_pages_found
message.run_ocr_first
error.course_html_not_found
error.figures_html_not_found
error.pdf_not_found
error.not_found
```

## Recommended route/output targets

Recommended low-risk route output:

```text
Missing PDF name
No OCR pages found
Run OCR first
Course HTML not found
Figures HTML not found
PDF not found
Not found
```

## Suggested target areas

Likely target areas in `services/api/web_app.py`:

```text
/review-concepts missing PDF output
/review-ocr-corrected missing PDF / no OCR pages output
/course-tools missing PDF output
/view-course missing course HTML output
/view-figures missing figures HTML output
OCR correction PDF not found / Not found output
```

## Defer from first integration batch

Do not patch these in the first implementation batch:

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

Reason:

```text
These are closer to workflow operations, exception details, dynamic messages, log handling, or generated route behavior.
They should be handled in a later focused batch.
```

## Future implementation rules

A future implementation should:

- patch exact visible route output only
- use existing `_ut(...)` helper
- preserve current fallback text
- preserve current HTTP status codes
- preserve redirects
- preserve exception behavior
- avoid generated course content
- avoid OCR output content
- avoid debug/log/developer text
- avoid broad UI rewrite
- keep language-pack JSON unchanged
- keep schema unchanged
- add a focused smoke helper

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-error-status-integration.py
```

It should verify that:

- selected error/status/message keys are used in `services/api/web_app.py`
- selected old hardcoded route-output snippets are removed only where intentionally replaced
- deferred workflow/error/log strings remain unchanged
- HTTP status code snippets still exist where expected

## Recommended validation after future implementation

Run:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py
python .\scripts\language-packs\test_ui_error_status_core_keys.py

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
python .\scripts\language-packs\smoke-ui-error-status-core-keys.py
python .\scripts\language-packs\smoke-ui-error-status-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-error-status-integration.py
```

## Recommended next milestone

```text
v0.2.75-public-beta-language-pack-ui-error-status-integration
```

Suggested next work:

- integrate the first small error/status route-output batch
- add `smoke-ui-error-status-integration.py`
- keep language-pack JSON unchanged
- keep schema unchanged
- preserve route behavior and status codes

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

v0.2.74 is documentation only.

It plans the first small error/status route-output integration batch using existing core language-pack keys.
