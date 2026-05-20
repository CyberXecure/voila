# Voila! UI Error / Status Deferred Plan

Milestone: v0.2.77-public-beta-language-pack-ui-error-status-deferred-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans a later deferred error/status UI integration batch.

The goal is to classify workflow/status/error route output that was intentionally deferred from the first v0.2.75 integration batch.

## Baseline

This plan builds on:

- v0.2.72 error/status core keys
- v0.2.75 first UI error/status route-output integration
- v0.2.76 UI error/status integration documentation and smoke maintenance

## Deferred candidate keys

The following keys already exist in the core language packs and were intentionally not integrated in v0.2.75:

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

## Recommended deferred batch candidates

Recommended next controlled implementation batch:

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
```

These are visible workflow/status results and can be integrated if route behavior and response status codes remain unchanged.

## Recommended later batch candidates

Keep these for a later, separate pass:

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

Reason:

```text
These are closer to upload validation, generic routing, log handling, or broader app behavior.
They should be handled after the workflow/status outputs are verified.
```

## Safety rules for future implementation

A future implementation should:

- patch exact visible route output only
- use existing `_ut(...)` helper
- preserve current fallback text
- preserve current HTTP status codes
- preserve redirects
- preserve exception behavior
- avoid generated course content
- avoid OCR output content
- avoid debug/developer text
- avoid broad UI rewrite
- keep language-pack JSON unchanged
- keep schema unchanged
- add a focused smoke helper

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-error-status-deferred-integration.py
```

It should verify that:

- selected deferred keys are used in `services/api/web_app.py`
- selected old hardcoded workflow/status snippets are removed only where intentionally replaced
- still-deferred generic/upload/log strings remain unchanged
- expected HTTP status code snippets still exist where expected
- existing error/status integration smoke still passes

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
python .\scripts\language-packs\smoke-ui-error-status-deferred-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-error-status-deferred-integration.py
```

## Recommended next milestone

```text
v0.2.78-public-beta-language-pack-ui-error-status-deferred-integration
```

Suggested next work:

- integrate only the workflow/status deferred batch
- add `smoke-ui-error-status-deferred-integration.py`
- keep `error.only_pdf_files_supported`, `error.page_not_found`, and `message.no_log_file_found_yet` deferred
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

v0.2.77 is documentation only.

It plans the next deferred workflow/status integration path without changing runtime behavior.
