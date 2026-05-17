# Voila! UI Key Map Checklist

Milestone: v0.2.45-public-beta-language-pack-ui-key-map-plan
Status: planning checklist
Scope: documentation only; no runtime changes, no UI code changes, no language-pack JSON changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.43 UI language consistency policy reviewed
- [x] v0.2.44 UI label inventory reviewed
- [x] Romanian default confirmed
- [x] English fallback confirmed
- [x] adaptive/browser-locale deferred

## Proposed placement

- [x] target file: language-packs/core/ro.language-pack.json
- [x] target file: language-packs/core/en.language-pack.json
- [x] target section: messages
- [x] key style: flat ui.* keys
- [x] no new top-level schema section in this milestone

## Proposed keys

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

## Romanian defaults

- [x] ui.upload_pdf = ÃŽncarcÄƒ PDF
- [x] ui.choose_file = Alege fiÈ™ier
- [x] ui.generated = Generat
- [x] ui.source_mode = Mod sursÄƒ
- [x] ui.generate_course = GenereazÄƒ curs
- [x] ui.open_course = Deschide cursul
- [x] ui.figures = Figuri
- [x] ui.edit_crops = EditeazÄƒ decupaje
- [x] ui.study = StudiazÄƒ
- [x] ui.review_weak = RepetÄƒ punctele slabe
- [x] ui.progress = Progres
- [x] ui.logs = Jurnale
- [x] ui.delete_from_library = È˜terge din bibliotecÄƒ

## English fallbacks

- [x] ui.upload_pdf = Upload PDF
- [x] ui.choose_file = Choose File
- [x] ui.generated = Generated
- [x] ui.source_mode = Source Mode
- [x] ui.generate_course = Generate course
- [x] ui.open_course = Open course
- [x] ui.figures = Figures
- [x] ui.edit_crops = Edit crops
- [x] ui.study = Study
- [x] ui.review_weak = Review weak
- [x] ui.progress = Progress
- [x] ui.logs = Logs
- [x] ui.delete_from_library = Delete from library

## Future test requirements

- [ ] Romanian lookup test for ui.upload_pdf
- [ ] English lookup test for ui.upload_pdf
- [ ] unsupported language fallback test
- [ ] missing key behavior test
- [ ] UI smoke path for ui.* keys

## Deferred

- [ ] editing core JSON files
- [ ] UI JavaScript integration
- [ ] schema change
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference

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

This milestone defines the key map only.

Implementation should happen in later milestones.
