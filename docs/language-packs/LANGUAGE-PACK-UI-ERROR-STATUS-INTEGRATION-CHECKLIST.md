# Voila! UI Error / Status Integration Plan Checklist

Milestone: v0.2.74-public-beta-language-pack-ui-error-status-integration-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.70 UI error/status plan completed
- [x] v0.2.71 error/status core key plan completed
- [x] v0.2.72 error/status core keys implemented
- [x] v0.2.73 error/status core key docs completed
- [x] route-output candidates scanned

## First batch candidates planned

- [x] error.missing_pdf_name
- [x] error.no_ocr_pages_found
- [x] message.run_ocr_first
- [x] error.course_html_not_found
- [x] error.figures_html_not_found
- [x] error.pdf_not_found
- [x] error.not_found

## Deferred from first implementation batch

- [x] status.rebuild_complete
- [x] status.rebuild_failed
- [x] error.save_title_override_failed
- [x] error.save_ocr_text_failed
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
- [x] avoid debug/log/developer text
- [x] avoid broad UI rewrite
- [x] add focused smoke helper in future implementation

## Deferred

- [ ] implementation
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] workflow/status operation localization

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

This milestone plans the first error/status route-output integration batch only.

Implementation should happen in a later milestone.
