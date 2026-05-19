# Voila! UI Error / Status Core Key Plan Checklist

Milestone: v0.2.71-public-beta-language-pack-ui-error-status-core-key-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.70 UI error/status plan completed
- [x] v0.2.69 status/message integration docs completed
- [x] v0.2.68 status/message UI integration completed
- [x] core Romanian language pack identified
- [x] core English language pack identified
- [x] error/status key gaps inspected

## Future target files planned

- [x] language-packs/core/ro.language-pack.json
- [x] language-packs/core/en.language-pack.json

## Future error.* keys planned

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

## Future status.* keys planned

- [x] status.rebuild_complete
- [x] status.rebuild_failed

## Future message.* keys planned

- [x] message.run_ocr_first
- [x] message.no_log_file_found_yet

## Future tests planned

- [x] ro/en key parity
- [x] error.* key presence
- [x] status.* key presence
- [x] message.* key presence
- [x] non-empty values
- [x] representative value checks
- [x] smoke helper

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

## Deferred

- [ ] core JSON key implementation
- [ ] parity tests implementation
- [ ] smoke helper implementation
- [ ] UI error/status integration
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching

## Decision

This milestone plans the exact error/status core keys only.

Implementation should happen in a later milestone.
