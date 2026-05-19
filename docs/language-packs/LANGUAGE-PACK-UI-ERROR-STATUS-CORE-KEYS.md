# Voila! UI Error / Status Core Keys

Milestone: v0.2.73-public-beta-language-pack-ui-error-status-core-key-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the core language-pack key implementation completed in v0.2.72.

The implementation added planned error/status route localization keys to the Romanian and English core language packs.

## Implemented in v0.2.72

Updated files:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

Added validation helpers:

```text
scripts/language-packs/test_ui_error_status_core_keys.py
scripts/language-packs/smoke-ui-error-status-core-keys.py
```

## Added error.* keys

```text
error.missing_pdf_name
error.no_ocr_pages_found
error.course_html_not_found
error.figures_html_not_found
error.page_not_found
error.pdf_not_found
error.not_found
error.only_pdf_files_supported
error.save_title_override_failed
error.save_ocr_text_failed
```

## Added status.* keys

```text
status.rebuild_complete
status.rebuild_failed
```

## Added message.* keys

```text
message.run_ocr_first
message.no_log_file_found_yet
```

## Validation coverage

The new unit test verifies that Romanian and English packs contain all planned error/status/message keys, key sets match, values are non-empty strings, and representative Romanian and English values are correct.

The new smoke helper verifies that all required error/status/message keys exist and all required values are non-empty in both core packs.

## Validation commands

v0.2.72 passed:

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

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\test_ui_error_status_core_keys.py
python -m py_compile .\scripts\language-packs\smoke-ui-error-status-core-keys.py
```

## What was intentionally not changed

v0.2.72 did not add UI code changes, runtime behavior changes, schema changes, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Remaining work

The keys now exist in the core packs, but error/status route output is not integrated yet.

Potential future integration targets:

```text
Missing PDF name
No OCR pages found
Run OCR first
Course HTML not found
Figures HTML not found
PDF not found
Not found
```

Defer more sensitive workflow/status output:

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
v0.2.74-public-beta-language-pack-ui-error-status-integration-plan
```

Suggested next work:

- plan the first small error/status route integration batch
- keep implementation deferred
- preserve HTTP status codes
- preserve redirects and exception behavior
- avoid generated/log/debug text

## Decision

v0.2.73 documents the completed v0.2.72 error/status core key implementation.
