# Voila! UI Error / Status Deferred Plan Checklist

Milestone: v0.2.77-public-beta-language-pack-ui-error-status-deferred-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.72 error/status core keys implemented
- [x] v0.2.75 first UI error/status integration completed
- [x] v0.2.76 integration docs and smoke maintenance completed
- [x] deferred route-output candidates scanned

## Deferred keys reviewed

- [x] status.rebuild_complete
- [x] status.rebuild_failed
- [x] error.save_title_override_failed
- [x] error.save_ocr_text_failed
- [x] error.only_pdf_files_supported
- [x] error.page_not_found
- [x] message.no_log_file_found_yet

## Recommended next implementation batch

- [x] status.rebuild_complete
- [x] status.rebuild_failed
- [x] error.save_title_override_failed
- [x] error.save_ocr_text_failed

## Still deferred

- [x] error.only_pdf_files_supported
- [x] error.page_not_found
- [x] message.no_log_file_found_yet

## Safety rules planned

- [x] patch exact visible route output only
- [x] preserve fallback text
- [x] preserve HTTP status codes
- [x] preserve redirects
- [x] preserve exception behavior
- [x] avoid generated content
- [x] avoid OCR output content
- [x] avoid debug/developer text
- [x] avoid broad UI rewrite
- [x] add focused smoke helper in future implementation

## Deferred

- [ ] implementation
- [ ] generic upload validation localization
- [ ] generic page-not-found localization
- [ ] log/no-log localization
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching

## Safety

- [x] no UI code change in this milestone
- [x] no language-pack JSON change in this milestone
- [x] no runtime behavior change in this milestone
- [x] no schema change in this milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Decision

This milestone plans the deferred workflow/status integration path only.

Implementation should happen in a later milestone.
