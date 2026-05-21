# Voila! UI Error / Status Rollup

Milestone: v0.2.83-public-beta-language-pack-ui-error-status-rollup
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone provides a rollup of the UI error/status language-pack work completed across v0.2.70 through v0.2.82.

The series planned, added, integrated, validated, and documented a controlled set of UI error/status route-output keys using the existing language-pack runtime helper.

## Sequence covered

```text
v0.2.70 UI error/status plan
v0.2.71 UI error/status core key plan
v0.2.72 UI error/status core keys
v0.2.73 UI error/status core key docs
v0.2.74 UI error/status integration plan
v0.2.75 UI error/status integration
v0.2.76 UI error/status integration docs
v0.2.77 UI error/status deferred plan
v0.2.78 UI error/status deferred integration
v0.2.79 UI error/status deferred integration docs
v0.2.80 UI error/status final deferred plan
v0.2.81 UI error/status final deferred integration
v0.2.82 UI error/status final deferred integration docs
```

## Core keys added in v0.2.72

The error/status keys were added to the core language packs before UI integration began.

```text
error.missing_pdf_name
error.no_ocr_pages_found
message.run_ocr_first
error.course_html_not_found
error.figures_html_not_found
error.pdf_not_found
error.not_found
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

## First integration batch

Implemented in v0.2.75.

```text
error.missing_pdf_name
error.no_ocr_pages_found
message.run_ocr_first
error.course_html_not_found
error.figures_html_not_found
error.pdf_not_found
error.not_found
```

Primary files:

```text
services/api/web_app.py
scripts/language-packs/smoke-ui-error-status-integration.py
```

## Deferred workflow/status integration batch

Implemented in v0.2.78.

```text
status.rebuild_complete
status.rebuild_failed
error.save_title_override_failed
error.save_ocr_text_failed
```

Primary files:

```text
services/api/web_app.py
scripts/language-packs/smoke-ui-error-status-deferred-integration.py
```

## Final deferred integration batch

Implemented in v0.2.81.

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

Primary files:

```text
services/api/web_app.py
scripts/language-packs/smoke-ui-error-status-final-deferred-integration.py
```

## CodeQL / security note

During v0.2.81, CodeQL flagged a high-severity reflected XSS issue in the localized page-not-found output because the dynamic `page` value was inserted into HTML.

The final implementation preserves the dynamic page value safely using:

```text
_html_escape(str(page))
```

This keeps the localized page-not-found label while preventing unescaped HTML injection.

## Smoke helpers

The following smoke helpers cover the UI error/status integration path:

```text
scripts/language-packs/test_ui_error_status_core_keys.py
scripts/language-packs/smoke-ui-error-status-core-keys.py
scripts/language-packs/smoke-ui-error-status-integration.py
scripts/language-packs/smoke-ui-error-status-deferred-integration.py
scripts/language-packs/smoke-ui-error-status-final-deferred-integration.py
scripts/language-packs/smoke-ui-status-message-integration.py
scripts/language-packs/smoke-ui-remaining-integration.py
```

Smoke helper maintenance was required when older helpers still expected literals that were intentionally localized in later batches.

## Safety rules followed

The series intentionally preserved:

```text
HTTP status codes
route behavior
fallback text
existing _ut(...) runtime helper
existing language-pack JSON after core-key addition
existing schema
dynamic page value
upload validation behavior
log route behavior
```

The series intentionally avoided:

```text
broad UI rewrite
generated content changes
OCR output content changes
debug/developer text changes
language selector
browser-locale detection
persisted language preference
adaptive UI switching
GitHub release upload
Git tag
public ZIP publish
LICENSE changes
```

## Validation pattern

Each implementation or documentation milestone reused the project validation pattern:

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
```

## Current state

The scoped UI error/status integration path is complete for the planned v0.2.72 core keys.

Remaining broader localization work is separate from this error/status sequence and should be handled as future planning.

## Recommended next milestone

```text
v0.2.84-public-beta-language-pack-ui-full-localization-inventory
```

Suggested next work:

- inventory remaining non-error/status UI literals
- keep it documentation-only
- avoid UI code, JSON, schema, release, tag, and public ZIP changes
- decide later whether full UI localization should proceed in small route-based batches

## Decision

v0.2.83 is a documentation-only rollup for the completed UI error/status language-pack sequence from v0.2.70 through v0.2.82.
