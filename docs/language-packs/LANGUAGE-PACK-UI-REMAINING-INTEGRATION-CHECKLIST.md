# Voila! UI Remaining Integration Plan Checklist

Milestone: v0.2.64-public-beta-language-pack-ui-remaining-integration-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.62 remaining core keys implemented
- [x] v0.2.63 remaining core key docs completed
- [x] UI remaining core key tests available
- [x] UI remaining core key smoke available
- [x] low-risk UI candidate scan reviewed

## Candidate labels planned

- [x] ui.logs
- [x] ui.course_tools
- [x] ui.quick_tools
- [x] ui.review_ocr_text
- [x] ui.review_concepts
- [x] ui.review_study_concepts
- [x] ui.correct_ocr_text
- [x] ui.study_mode
- [x] ui.toggle_theme
- [x] ui.save_title_override
- [x] ui.fit_width

## Safety rules planned

- [x] patch exact visible labels only
- [x] preserve fallback text
- [x] avoid generated content
- [x] avoid debug/log text
- [x] avoid error/status headings in first batch
- [x] avoid broad UI rewrite
- [x] add focused smoke helper in future implementation

## Deferred

- [ ] implementation
- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] status/message integration batch

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

This milestone plans the first remaining UI integration batch only.

Implementation should happen in a later milestone.
