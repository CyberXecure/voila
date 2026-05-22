# Voila! UI Full Localization Batch Plan Checklist

Milestone: v0.2.85-public-beta-language-pack-ui-full-localization-batch-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.84 full UI localization inventory completed
- [x] v0.2.83 error/status rollup completed
- [x] v0.2.81 XSS fix confirmed
- [x] baseline language-pack checks passed
- [x] first-batch candidate scan completed

## Candidate groups reviewed

- [x] static headings
- [x] button labels
- [x] link labels
- [x] form labels
- [x] table headers
- [x] option labels

## Recommended first batch documented

- [x] static headings
- [x] simple navigation/link labels
- [x] simple button labels
- [x] one safe form label

## Exclusions documented

- [x] generated course content
- [x] OCR extracted output
- [x] user-authored OCR corrections
- [x] debug/developer-only text
- [x] exception trace text
- [x] large mixed dynamic HTML blocks
- [x] already-localized error/status output

## Future milestones planned

- [x] v0.2.86 full localization core keys
- [x] v0.2.87 full localization first batch
- [x] focused first-batch smoke helper

## Safety rules documented

- [x] preserve fallback text
- [x] preserve HTTP status codes
- [x] preserve redirects
- [x] preserve route behavior
- [x] preserve generated content
- [x] preserve OCR output
- [x] preserve course output
- [x] preserve user-authored corrections
- [x] escape dynamic HTML values
- [x] avoid broad UI rewrite

## Deferred

- [ ] language-pack JSON additions
- [ ] UI code integration
- [ ] first-batch smoke helper implementation
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

This milestone plans the first safe full UI localization batch only.

Implementation should happen in a later milestone.
