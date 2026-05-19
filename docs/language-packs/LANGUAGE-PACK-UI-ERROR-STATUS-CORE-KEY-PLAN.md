# Voila! UI Error / Status Core Key Plan

Milestone: v0.2.71-public-beta-language-pack-ui-error-status-core-key-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the exact future core language-pack keys for error/status route localization.

The goal is to prepare a later JSON implementation milestone without modifying the Romanian or English core language packs yet.

## Baseline

This plan builds on:

- v0.2.70 UI error/status plan
- v0.2.69 status/message integration documentation
- v0.2.68 status/message UI integration
- v0.2.62 remaining core key structure

## Future target files

A future implementation should update only:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

The future implementation should keep Romanian and English key sets identical.

## Proposed error.* keys

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

## Proposed status.* keys

```text
status.rebuild_complete
status.rebuild_failed
```

## Proposed message.* keys

```text
message.run_ocr_first
message.no_log_file_found_yet
```

## Proposed Romanian values

```text
error.missing_pdf_name = Nume PDF lipsă
error.no_ocr_pages_found = Nu au fost găsite pagini OCR
error.course_html_not_found = HTML-ul cursului nu a fost găsit
error.figures_html_not_found = HTML-ul figurilor nu a fost găsit
error.page_not_found = Pagina nu a fost găsită
error.pdf_not_found = PDF-ul nu a fost găsit
error.not_found = Nu a fost găsit
error.only_pdf_files_supported = Sunt acceptate doar fișiere PDF
error.save_title_override_failed = Salvarea titlului modificat a eșuat
error.save_ocr_text_failed = Salvarea textului OCR a eșuat

status.rebuild_complete = Reconstruire completă
status.rebuild_failed = Reconstruire eșuată

message.run_ocr_first = Rulează OCR mai întâi
message.no_log_file_found_yet = Nu a fost găsit încă niciun fișier jurnal
```

## Proposed English values

```text
error.missing_pdf_name = Missing PDF name
error.no_ocr_pages_found = No OCR pages found
error.course_html_not_found = Course HTML not found
error.figures_html_not_found = Figures HTML not found
error.page_not_found = Page not found
error.pdf_not_found = PDF not found
error.not_found = Not found
error.only_pdf_files_supported = Only PDF files are supported
error.save_title_override_failed = Save title override failed
error.save_ocr_text_failed = Save OCR text failed

status.rebuild_complete = Rebuild complete
status.rebuild_failed = Rebuild failed

message.run_ocr_first = Run OCR first
message.no_log_file_found_yet = No log file found yet
```

## Safety rules for future implementation

The future implementation should:

- add keys under the existing `messages` object
- keep Romanian and English key sets identical
- preserve all existing keys
- avoid schema changes unless validation requires them
- avoid UI code changes in the core-key implementation milestone
- add focused parity tests
- add a smoke helper for the new keys

## Suggested future tests

Suggested unit test:

```text
scripts/language-packs/test_ui_error_status_core_keys.py
```

It should verify:

```text
all planned error.* keys exist in ro/en
all planned status.* keys exist in ro/en
all planned message.* keys exist in ro/en
ro/en planned key sets match
values are non-empty strings
representative Romanian and English values are correct
```

Suggested smoke helper:

```text
scripts/language-packs/smoke-ui-error-status-core-keys.py
```

It should verify:

```text
all planned error/status/message keys exist
all values are non-empty
ro/en key coverage is identical
```

## Recommended validation after future implementation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

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

## Recommended next milestone

```text
v0.2.72-public-beta-language-pack-ui-error-status-core-keys
```

Suggested next work:

- add the planned keys to Romanian and English core packs
- add parity tests
- add smoke helper
- keep UI code unchanged
- keep schema unchanged unless validation requires otherwise

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

v0.2.71 is documentation only.

It defines the exact future core keys for controlled error/status route localization.
