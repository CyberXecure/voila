# Voila! UI Error / Status Plan

Milestone: v0.2.70-public-beta-language-pack-ui-error-status-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans a small future localization batch for visible error/status route output.

The goal is to classify safe candidates before changing UI code or language-pack JSON.

## Baseline

This plan builds on:

- v0.2.62 remaining core keys
- v0.2.65 remaining UI integration
- v0.2.68 status/message UI integration
- v0.2.69 status/message integration documentation

## Candidate error/status strings

Visible route/status candidates found in `services/api/web_app.py` include:

```text
Missing PDF name
No OCR pages found
Run OCR first
Rebuild complete
Rebuild failed
Save title override failed
Save OCR text failed
Course HTML not found
Figures HTML not found
Page not found
No log file found yet
PDF not found
Not found
Only PDF files are supported
```

## Recommended future key groups

A later implementation should use small, explicit key groups:

```text
error.*    visible error headings/messages
status.*   operation status labels and results
message.*  short helper/error explanation text
```

## Recommended future error.* keys

Suggested keys for a later core JSON milestone:

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

## Recommended future status.* keys

Suggested status keys for a later core JSON milestone:

```text
status.rebuild_complete
status.rebuild_failed
```

## Recommended future message.* keys

Suggested message keys for a later core JSON milestone:

```text
message.run_ocr_first
message.no_log_file_found_yet
```

## First implementation batch recommendation

The first implementation batch should be conservative.

Recommended first batch:

```text
error.missing_pdf_name
error.no_ocr_pages_found
message.run_ocr_first
error.course_html_not_found
error.figures_html_not_found
error.pdf_not_found
error.not_found
```

Defer from first batch:

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
These are closer to workflow operations, HTTP exception details, generated routes, or dynamic text.
They should be handled after the smallest static route-output batch.
```

## Safety rules for future implementation

A future implementation should:

- patch only exact visible route output
- preserve current HTTP status codes
- preserve current exception behavior
- preserve current redirects
- preserve fallback text
- avoid generated content
- avoid OCR output
- avoid debug/log text
- avoid broad UI rewrite
- keep language-pack JSON changes separate or very small
- add focused tests/smoke helpers

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-error-status-integration.py
```

It should verify that:

- selected error/status keys are used in `services/api/web_app.py`
- selected old hardcoded snippets are removed only where intentionally replaced
- deferred strings remain unchanged
- status codes and route behavior are not modified by string localization

## Recommended implementation order

```text
1. add planned error/status/message keys to ro/en core packs
2. add parity tests for the new keys
3. add smoke helper for key presence
4. integrate the smallest safe error/status route batch
5. document the integration
```

## Recommended next milestone

```text
v0.2.71-public-beta-language-pack-ui-error-status-core-key-plan
```

Suggested next work:

- plan the exact core keys for error/status route localization
- keep UI implementation deferred
- keep scope small and safe

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

v0.2.70 is documentation only.

It plans the next controlled error/status localization path without changing runtime behavior.
