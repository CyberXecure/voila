# Voila! Minimal UI Key Integration Checklist

Milestone: v0.2.49-public-beta-language-pack-minimal-ui-key-integration-plan
Status: planning checklist
Scope: documentation only; no UI JavaScript changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.43 UI language consistency policy reviewed
- [x] v0.2.44 UI label inventory reviewed
- [x] v0.2.45 UI key map reviewed
- [x] v0.2.46 UI core key plan reviewed
- [x] v0.2.47 UI core keys implemented
- [x] v0.2.48 UI core key docs reviewed

## Existing core keys confirmed

- [x] ui.upload_pdf
- [x] ui.choose_file
- [x] ui.generated
- [x] ui.source_mode
- [x] ui.generate_course
- [x] ui.open_course
- [x] ui.figures
- [x] ui.edit_crops
- [x] ui.study
- [x] ui.review_weak
- [x] ui.progress
- [x] ui.logs
- [x] ui.delete_from_library

## First integration candidates

- [x] ui.upload_pdf
- [x] ui.generate_course
- [x] ui.open_course
- [ ] ui.delete_from_library optional

## Implementation constraints planned

- [x] integrate only 2-3 labels first
- [x] no broad UI rewrite
- [x] no language selector
- [x] no browser-locale detection
- [x] no persisted language preference
- [x] no schema change
- [x] no release asset change

## Fallback behavior planned

- [x] Romanian value should be used when Romanian is selected/default
- [x] English fallback should remain available
- [x] unsupported language should fall back to English
- [x] missing key should fall back safely
- [x] current UI behavior should not break

## Future validation planned

- [x] language-pack validation
- [x] runtime tests
- [x] minimal runtime tests
- [x] UI core key tests
- [x] UI language endpoint smoke
- [x] UI core key smoke
- [x] focused UI integration smoke
- [x] Python compile
- [x] manual UI check

## Deferred

- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] public release asset update

## Safety

- [x] no UI JavaScript change in this planning milestone
- [x] no runtime behavior change in this planning milestone
- [x] no schema change in this planning milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Result

- [ ] PASS
- [ ] FAIL

## Decision

This milestone plans minimal UI key integration only.

Implementation should happen in a later milestone.
