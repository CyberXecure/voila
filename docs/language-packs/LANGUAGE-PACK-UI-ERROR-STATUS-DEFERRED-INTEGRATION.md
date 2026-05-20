# Voila! UI Error / Status Deferred Integration

Milestone: v0.2.79-public-beta-language-pack-ui-error-status-deferred-integration-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the deferred UI error/status workflow/status integration completed in v0.2.78.

The implementation used existing core language-pack keys from v0.2.72 and integrated a focused workflow/status batch that had been intentionally deferred from v0.2.75.

## Implemented in v0.2.78

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-error-status-deferred-integration.py
```

Maintained smoke helpers:

```text
scripts/language-packs/smoke-ui-error-status-integration.py
scripts/language-packs/smoke-ui-status-message-integration.py
```

## Integrated deferred keys

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
```

## UI route-output covered

```text
Rebuild complete
Rebuild failed
Save title override failed
Save OCR text failed
```

## Still deferred

These keys remain intentionally deferred after v0.2.78:

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

Related literal output still remains intentionally present:

```text
Only PDF files are supported.
Page not found:
No log file found yet.
```

## Safety choices

The implementation intentionally preserved HTTP status codes, route behavior, fallback text, the existing `_ut(...)` runtime helper, existing language-pack JSON, and existing schema.

The implementation intentionally avoided generic upload validation localization, generic page-not-found localization, log/no-log localization, generated content, OCR output content, debug/developer text, and broad UI rewrite.

## Validation coverage

The new deferred smoke helper verifies that selected deferred keys are used in `services/api/web_app.py`, selected old hardcoded workflow/status snippets are no longer present, still-deferred generic/upload/log keys were not integrated too early, still-deferred literal output remains present, and expected HTTP status code snippets remain present.

The maintained smoke helpers verify that earlier error/status and status/message expectations remain compatible with the v0.2.78 localization changes.

## Validation commands

v0.2.78 passed:

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

## What was intentionally not changed

v0.2.78 did not add language-pack JSON changes, schema changes, broad UI rewrite, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Remaining work

Future batches can handle:

```text
Only PDF files are supported.
Page not found:
No log file found yet.
```

## Recommended next milestone

```text
v0.2.80-public-beta-language-pack-ui-error-status-final-deferred-plan
```

Suggested next work:

- plan the final small deferred error/status batch
- keep implementation deferred
- decide whether upload validation, page-not-found, and no-log output are safe to localize together or separately
- preserve route behavior and status codes
- avoid full UI rewrite

## Decision

v0.2.79 documents the completed v0.2.78 deferred UI error/status workflow/status integration batch.
