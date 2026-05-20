# Voila! UI Error / Status Integration

Milestone: v0.2.76-public-beta-language-pack-ui-error-status-integration-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the UI error/status route-output integration completed in v0.2.75.

The implementation used existing core language-pack keys from v0.2.72 and integrated the first small batch of low-risk visible route output.

## Implemented in v0.2.75

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-error-status-integration.py
```

## Integrated keys

v0.2.75 integrated the following existing core keys:

```text
error.missing_pdf_name
error.no_ocr_pages_found
message.run_ocr_first
error.course_html_not_found
error.figures_html_not_found
error.pdf_not_found
error.not_found
```

## UI route-output covered

The implementation covered low-risk visible route output:

```text
Missing PDF name
No OCR pages found
Run OCR first
Course HTML not found
Figures HTML not found
PDF not found
Not found
```

## Safety choices

The implementation intentionally preserved HTTP status codes, route behavior, fallback text, the existing `_ut(...)` runtime helper, existing language-pack JSON, and existing schema.

The implementation intentionally avoided:

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
generated content
OCR output content
debug/log/developer text
broad UI rewrite
```

## Validation coverage

The new smoke helper verifies that selected error/status/message keys are used in `services/api/web_app.py`, selected old hardcoded route-output snippets are no longer present where intentionally replaced, deferred workflow/error/log keys were not integrated too early, and expected HTTP status code snippets remain present.

## Validation commands

v0.2.75 passed:

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

## What was intentionally not changed

v0.2.75 did not add language-pack JSON changes, schema changes, broad UI rewrite, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Remaining work

The UI is still not fully localized.

Future error/status batches can handle deferred workflow/status output, including:

```text
Rebuild complete
Rebuild failed
Save title override failed
Save OCR text failed
Only PDF files are supported
Page not found
No log file found yet
```

## Recommended next milestone

```text
v0.2.77-public-beta-language-pack-ui-error-status-deferred-plan
```

Suggested next work:

- plan a small deferred error/status batch
- keep implementation deferred
- preserve route behavior and status codes
- avoid generated/log/debug text
- avoid full UI rewrite

## Decision

v0.2.76 documents the completed v0.2.75 UI error/status route-output integration batch.
