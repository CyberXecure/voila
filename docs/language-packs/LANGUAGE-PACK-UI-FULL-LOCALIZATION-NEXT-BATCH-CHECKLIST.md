# Voila! UI Full Localization Next Batch Plan Checklist

Milestone: v0.2.89-public-beta-language-pack-ui-full-localization-next-batch-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.88 first batch docs completed
- [x] v0.2.87 first batch smoke passed
- [x] v0.2.86 full UI core keys confirmed
- [x] v0.2.81 XSS fix confirmed
- [x] baseline validation passed
- [x] remaining UI literal scan completed

## Candidate groups reviewed

- [x] remaining HTML headings
- [x] remaining button labels
- [x] remaining link labels
- [x] remaining form labels
- [x] remaining paragraph literals
- [x] remaining title literals

## Recommended next batch documented

- [x] pagination/navigation links
- [x] remaining simple study/course/concepts links
- [x] short OCR review navigation links
- [x] small safe empty-state/help paragraphs
- [x] one static title literal

## Recommended exclusions documented

- [x] mixed HTML + paragraph error strings need careful review
- [x] debug/developer-only text excluded
- [x] generated course content excluded
- [x] OCR extracted output excluded
- [x] user-authored OCR corrections excluded
- [x] large mixed dynamic HTML blocks excluded
- [x] already-localized lines excluded
- [x] Romanian helper text deferred for separate review

## Future milestones planned

- [x] next-batch core keys milestone
- [x] next-batch integration milestone
- [x] focused next-batch smoke helper

## Safety documented

- [x] preserve URLs
- [x] preserve query strings
- [x] preserve route behavior
- [x] preserve HTTP status codes
- [x] preserve fallback text
- [x] preserve dynamic values
- [x] preserve generated content
- [x] preserve OCR output
- [x] preserve course output
- [x] preserve user-authored corrections
- [x] escape dynamic HTML values
- [x] avoid broad UI rewrite

## Deferred

- [ ] language-pack JSON additions
- [ ] UI code integration
- [ ] next-batch smoke helper implementation
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] release upload
- [ ] public ZIP publish

## Safety

- [x] no UI code change in this milestone
- [x] no language-pack JSON change in this milestone
- [x] no runtime behavior change in this milestone
- [x] no schema change in this milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] existing v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Decision

This milestone plans the next full UI localization batch only.

Implementation should happen in a later milestone.
