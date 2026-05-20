# Voila! UI Error / Status Final Deferred Plan

Milestone: v0.2.80-public-beta-language-pack-ui-error-status-final-deferred-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the final small deferred UI error/status integration batch.

The remaining targets are the last visible error/status outputs that already have core language-pack keys but were intentionally left out of v0.2.75 and v0.2.78.

## Baseline

This plan builds on:

- v0.2.72 error/status core keys
- v0.2.75 first UI error/status integration
- v0.2.78 deferred workflow/status integration
- v0.2.79 deferred integration documentation and smoke maintenance

## Final deferred candidate keys

The following keys already exist in the core language packs and remain intentionally deferred:

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

## Current literal targets

The remaining literal outputs are:

```text
Only PDF files are supported.
Page not found:
No log file found yet.
```

## Recommended final implementation batch

Recommended next controlled implementation batch:

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

## Suggested future implementation details

Use existing `_ut(...)` fallback behavior and preserve route behavior.

Suggested future replacements:

```text
Only PDF files are supported. -> _ut("error.only_pdf_files_supported", "Only PDF files are supported")
Page not found: {page} -> _ut("error.page_not_found", "Page not found") + f": {page}"
No log file found yet. -> _ut("message.no_log_file_found_yet", "No log file found yet")
```

## Safety rules for future implementation

A future implementation should:

- patch exact visible route output only
- use existing `_ut(...)` helper
- preserve current fallback text
- preserve current HTTP status codes
- preserve dynamic page value in page-not-found output
- preserve exception behavior
- preserve upload validation behavior
- preserve log route behavior
- avoid generated course content
- avoid OCR output content
- avoid debug/developer text
- avoid broad UI rewrite
- keep language-pack JSON unchanged
- keep schema unchanged
- add a focused smoke helper

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-error-status-final-deferred-integration.py
```

It should verify that:

- the final deferred keys are used in `services/api/web_app.py`
- old hardcoded final-deferred snippets are removed only where intentionally replaced
- dynamic page-not-found output still preserves the page value
- expected HTTP status code snippets remain present
- earlier error/status smoke helpers still pass

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
python .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py
```

## Recommended next milestone

```text
v0.2.81-public-beta-language-pack-ui-error-status-final-deferred-integration
```

Suggested next work:

- integrate only the final three deferred keys
- add `smoke-ui-error-status-final-deferred-integration.py`
- maintain older smoke helpers if they still expect now-localized literals
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

v0.2.80 is documentation only.

It plans the final deferred error/status integration path without changing runtime behavior.
