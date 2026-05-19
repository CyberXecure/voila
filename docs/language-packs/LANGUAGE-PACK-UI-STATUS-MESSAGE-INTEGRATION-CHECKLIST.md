# Voila! UI Status / Message Integration Plan Checklist

Milestone: v0.2.67-public-beta-language-pack-ui-status-message-integration-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.62 remaining core keys implemented
- [x] v0.2.63 remaining core key docs completed
- [x] v0.2.64 UI remaining integration plan completed
- [x] v0.2.65 UI remaining integration completed
- [x] v0.2.66 UI remaining integration docs completed

## message.* candidates planned

- [x] message.open_course_description
- [x] message.lessons_description
- [x] message.study_mode_description
- [x] message.review_ocr_text_description
- [x] message.review_concepts_description
- [x] message.edit_crops_description
- [x] message.figures_description
- [x] message.progress_description
- [x] message.return_to_library_description
- [x] message.source_mode_description

## status.* candidates planned

- [x] status.uploaded
- [x] status.not_generated_yet
- [x] status.no_suspicious_pages_detected
- [x] status.focused_concept
- [x] status.attempts
- [x] status.status
- [x] status.study_coverage
- [x] status.overall_mastery
- [x] status.concept_status

## Deferred from first implementation batch

- [x] status.missing_pdf_name
- [x] status.no_ocr_pages_found
- [x] status.rebuild_complete
- [x] status.rebuild_failed
- [x] status.save_title_override_failed
- [x] status.save_ocr_text_failed
- [x] message.apply_corrected_ocr_warning

## Safety rules planned

- [x] patch exact visible helper/status text only
- [x] preserve fallback text
- [x] avoid generated content
- [x] avoid OCR output
- [x] avoid logs
- [x] avoid debug/developer text
- [x] avoid broad UI rewrite
- [x] add focused smoke helper in future implementation

## Deferred

- [ ] implementation
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] error/status route localization

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

This milestone plans the first status/message UI integration batch only.

Implementation should happen in a later milestone.
