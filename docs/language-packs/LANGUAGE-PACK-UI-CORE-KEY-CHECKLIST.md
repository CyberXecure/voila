# Voila! UI Core Key Checklist

Milestone: v0.2.46-public-beta-language-pack-ui-core-key-plan
Status: planning checklist
Scope: documentation only; no core JSON changes, no runtime changes, no UI code changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.43 UI language consistency policy reviewed
- [x] v0.2.44 UI label inventory reviewed
- [x] v0.2.45 UI key map reviewed
- [x] Romanian default confirmed
- [x] English fallback confirmed
- [x] target section confirmed: messages

## Target files for later implementation

- [x] language-packs/core/ro.language-pack.json
- [x] language-packs/core/en.language-pack.json
- [x] no schema change planned
- [x] no UI JavaScript change planned
- [x] no runtime code change planned

## Keys planned

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

## Test requirements planned

- [x] Romanian lookup test for ui.upload_pdf
- [x] English lookup test for ui.upload_pdf
- [x] Romanian lookup test for ui.delete_from_library
- [x] English lookup test for ui.delete_from_library
- [x] unsupported language fallback test
- [x] missing key behavior must remain unchanged
- [x] core runtime smoke should cover at least one ui.* key

## Deferred

- [ ] editing core JSON files
- [ ] UI JavaScript integration
- [ ] schema change
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive switching
- [ ] public release asset update

## Safety

- [x] no runtime behavior change
- [x] no UI code change
- [x] no language-pack JSON change
- [x] no schema change
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Decision

This milestone plans the core language-pack key edit only.

Implementation should happen in a later milestone.
