# Voila! UI Error / Status Final Deferred Integration

Milestone: v0.2.82-public-beta-language-pack-ui-error-status-final-deferred-integration-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the final deferred UI error/status integration completed in v0.2.81.

The implementation used existing core language-pack keys from v0.2.72 and integrated the last small batch of visible error/status route output that had remained deferred.

## Implemented in v0.2.81

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-error-status-final-deferred-integration.py
```

Maintained existing smoke helpers so they no longer expect final-deferred literals that were intentionally localized.

## Integrated final deferred keys

```text
error.only_pdf_files_supported
error.page_not_found
message.no_log_file_found_yet
```

## UI route-output covered

```text
Only PDF files are supported.
Page not found:
No log file found yet.
```

## CodeQL / XSS fix

During the v0.2.81 pull request, CodeQL flagged a high-severity reflected XSS issue in the localized page-not-found output.

The first localized version preserved the dynamic page value but inserted it directly into HTML.

The final implementation preserves the dynamic page value safely by escaping it:

```text
_html_escape(str(page))
```

The corrected page-not-found output keeps the localized label and dynamic page value while preventing unescaped HTML injection.

## Safety choices

The implementation intentionally preserved HTTP status codes, route behavior, fallback text, the existing `_ut(...)` runtime helper, existing language-pack JSON, existing schema, dynamic page value, upload validation behavior, and log route behavior.

The implementation intentionally avoided generated content changes, OCR output content changes, debug/developer text changes, broad UI rewrite, language selector, browser-locale detection, persisted language preference, and adaptive UI switching.

## Validation coverage

The final deferred smoke helper verifies that:

- final deferred keys are used in `services/api/web_app.py`
- old hardcoded final-deferred snippets are no longer present where intentionally replaced
- dynamic page-not-found output is preserved with `_html_escape(str(page))`
- expected HTTP status code snippets remain present

Existing smoke helpers verify that earlier UI error/status integrations remain compatible with the v0.2.81 changes.

## Validation commands

v0.2.81 passed:

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

## What was intentionally not changed

v0.2.81 did not add language-pack JSON changes, schema changes, broad UI rewrite, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Current state

The planned UI error/status integration path is complete for the scoped core keys from v0.2.72.

Remaining broader localization work should be handled separately from the error/status batch series.

## Recommended next milestone

```text
v0.2.83-public-beta-language-pack-ui-error-status-rollup
```

Suggested next work:

- add a rollup document for the v0.2.70 to v0.2.82 error/status sequence
- summarize all integrated keys
- summarize smoke helpers and safety rules
- keep it documentation-only
- avoid UI code, JSON, schema, release, tag, and public ZIP changes

## Decision

v0.2.82 documents the completed v0.2.81 final deferred UI error/status integration and the CodeQL reflected-XSS fix.
