# Voila! UI Error / Status Plan Checklist

Milestone: v0.2.70-public-beta-language-pack-ui-error-status-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.62 remaining core keys implemented
- [x] v0.2.65 remaining UI integration completed
- [x] v0.2.68 status/message UI integration completed
- [x] v0.2.69 status/message integration docs completed
- [x] error/status route candidate scan reviewed

## Candidate groups planned

- [x] error.* route error labels
- [x] status.* operation status labels
- [x] message.* helper/error explanations

## Future error.* candidates planned

- [x] error.missing_pdf_name
- [x] error.no_ocr_pages_found
- [x] error.course_html_not_found
- [x] error.figures_html_not_found
- [x] error.page_not_found
- [x] error.pdf_not_found
- [x] error.not_found
- [x] error.only_pdf_files_supported
- [x] error.save_title_override_failed
- [x] error.save_ocr_text_failed

## Future status.* candidates planned

- [x] status.rebuild_complete
- [x] status.rebuild_failed

## Future message.* candidates planned

- [x] message.run_ocr_first
- [x] message.no_log_file_found_yet

## Safety rules planned

- [x] preserve HTTP status codes
- [x] preserve exception behavior
- [x] preserve redirects
- [x] preserve fallback text
- [x] avoid generated content
- [x] avoid OCR output
- [x] avoid debug/log text
- [x] avoid broad UI rewrite
- [x] add focused smoke helper in future implementation

## Deferred

- [ ] core JSON key implementation
- [ ] parity tests
- [ ] smoke helper
- [ ] UI implementation
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

This milestone plans the error/status localization path only.

Implementation should happen in later milestones.
