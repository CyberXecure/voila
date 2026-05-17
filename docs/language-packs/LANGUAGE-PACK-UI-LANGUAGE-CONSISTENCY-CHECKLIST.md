# Voila! UI Language Consistency Checklist

Milestone: v0.2.43-public-beta-language-pack-ui-language-consistency-plan
Status: planning checklist
Scope: documentation only; no runtime changes, no UI code changes, no GitHub release upload, no tag, no public ZIP publish

## Policy decision

- [x] default UI language should be Romanian
- [x] English should remain fallback
- [x] adaptive/browser-locale behavior is deferred
- [x] mixed UI labels are documented as follow-up
- [x] mixed UI labels do not block language-pack packaging validation

## Known mixed labels

English labels observed:

- [ ] Upload PDF
- [ ] Choose File
- [ ] Upload PDF
- [ ] Generated
- [ ] Source Mode
- [ ] Generate course
- [ ] Figures
- [ ] Edit crops
- [ ] Study
- [ ] Review weak
- [ ] Progress
- [ ] Logs
- [ ] Delete from library

Romanian labels observed:

- [ ] Deschide cursul

## Future inventory checklist

- [ ] home page labels inventoried
- [ ] upload flow labels inventoried
- [ ] course/library labels inventoried
- [ ] OCR review labels inventoried
- [ ] study/review labels inventoried
- [ ] progress/log labels inventoried
- [ ] delete/action labels inventoried

## Future translation-key checklist

- [ ] each user-facing label has a stable key
- [ ] Romanian value exists for each user-facing key
- [ ] English fallback exists for each user-facing key
- [ ] missing keys fall back safely
- [ ] unsupported languages fall back to English

## Deferred features

- [ ] explicit language selector
- [ ] browser-locale detection
- [ ] persisted user language preference
- [ ] adaptive UI switching
- [ ] unsupported locale behavior

## Safety

- [x] no runtime behavior change in this milestone
- [x] no UI code change in this milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Result

- [ ] PASS
- [ ] FAIL

## Decision

This milestone establishes policy only.

Implementation should happen in later milestones.
