# Voila! UI Error / Status Rollup Checklist

Milestone: v0.2.83-public-beta-language-pack-ui-error-status-rollup
Status: documentation checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Sequence documented

- [x] v0.2.70 UI error/status plan
- [x] v0.2.71 UI error/status core key plan
- [x] v0.2.72 UI error/status core keys
- [x] v0.2.73 UI error/status core key docs
- [x] v0.2.74 UI error/status integration plan
- [x] v0.2.75 UI error/status integration
- [x] v0.2.76 UI error/status integration docs
- [x] v0.2.77 UI error/status deferred plan
- [x] v0.2.78 UI error/status deferred integration
- [x] v0.2.79 UI error/status deferred integration docs
- [x] v0.2.80 UI error/status final deferred plan
- [x] v0.2.81 UI error/status final deferred integration
- [x] v0.2.82 UI error/status final deferred integration docs

## Integrated keys documented

- [x] error.missing_pdf_name
- [x] error.no_ocr_pages_found
- [x] message.run_ocr_first
- [x] error.course_html_not_found
- [x] error.figures_html_not_found
- [x] error.pdf_not_found
- [x] error.not_found
- [x] status.rebuild_complete
- [x] status.rebuild_failed
- [x] error.save_title_override_failed
- [x] error.save_ocr_text_failed
- [x] error.only_pdf_files_supported
- [x] error.page_not_found
- [x] message.no_log_file_found_yet

## Security documented

- [x] CodeQL reflected-XSS finding documented
- [x] `_html_escape(str(page))` fix documented
- [x] dynamic page value preservation documented

## Smoke helpers documented

- [x] test_ui_error_status_core_keys.py
- [x] smoke-ui-error-status-core-keys.py
- [x] smoke-ui-error-status-integration.py
- [x] smoke-ui-error-status-deferred-integration.py
- [x] smoke-ui-error-status-final-deferred-integration.py
- [x] smoke-ui-status-message-integration.py
- [x] smoke-ui-remaining-integration.py

## Safety documented

- [x] no UI code change in this milestone
- [x] no language-pack JSON change in this milestone
- [x] no runtime behavior change in this milestone
- [x] no schema change in this milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] no dependency change
- [x] no LICENSE change
- [x] existing v0.2.0-public-beta assets unchanged

## Deferred beyond this rollup

- [ ] full UI localization inventory
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] release upload
- [ ] public ZIP publish

## Decision

This milestone is a documentation-only rollup for the completed UI error/status language-pack sequence.
