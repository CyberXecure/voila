# Voila! UI Error / Status Integration Documentation Checklist

Milestone: v0.2.76-public-beta-language-pack-ui-error-status-integration-docs
Status: documentation checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## v0.2.75 implementation documented

- [x] services/api/web_app.py update documented
- [x] smoke-ui-error-status-integration.py documented
- [x] error.missing_pdf_name documented
- [x] error.no_ocr_pages_found documented
- [x] message.run_ocr_first documented
- [x] error.course_html_not_found documented
- [x] error.figures_html_not_found documented
- [x] error.pdf_not_found documented
- [x] error.not_found documented

## Validation documented

- [x] language-pack packaging inspection
- [x] language-pack validation
- [x] runtime tests
- [x] minimal runtime tests
- [x] UI core key tests
- [x] remaining core key tests
- [x] error/status core key tests
- [x] UI language endpoint smoke
- [x] core runtime helper smoke
- [x] language-pack file smoke
- [x] UI core key smoke
- [x] minimal UI key integration smoke
- [x] UI expansion key integration smoke
- [x] UI next batch key integration smoke
- [x] UI remaining core key smoke
- [x] UI remaining integration smoke
- [x] UI status/message integration smoke
- [x] UI error/status core key smoke
- [x] UI error/status integration smoke
- [x] Python compile

## Safety documented

- [x] no language-pack JSON change in v0.2.75
- [x] no schema change in v0.2.75
- [x] no broad UI rewrite
- [x] no language selector
- [x] no browser-locale detection
- [x] no persisted language preference
- [x] no adaptive UI switching
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] no LICENSE change

## Deferred

- [ ] status.rebuild_complete
- [ ] status.rebuild_failed
- [ ] error.save_title_override_failed
- [ ] error.save_ocr_text_failed
- [ ] error.only_pdf_files_supported
- [ ] error.page_not_found
- [ ] message.no_log_file_found_yet
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching

## Decision

This milestone documents the completed v0.2.75 UI error/status route-output integration batch.
