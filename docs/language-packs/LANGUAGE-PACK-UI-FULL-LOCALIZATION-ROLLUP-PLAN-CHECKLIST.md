# Voila! UI Full Localization Rollup Plan Checklist

Milestone: v0.2.94-public-beta-language-pack-ui-full-localization-rollup-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.84 inventory completed
- [x] v0.2.85 first batch plan completed
- [x] v0.2.86 first batch core keys completed
- [x] v0.2.87 first batch integration completed
- [x] v0.2.88 first batch docs completed
- [x] v0.2.89 next batch plan completed
- [x] v0.2.90 next-batch core keys completed
- [x] v0.2.91 next batch integration completed
- [x] v0.2.92 next batch docs completed
- [x] v0.2.93 remaining inventory completed
- [x] v0.2.81 XSS fix confirmed
- [x] baseline validation passed
- [x] rollup-plan scan completed

## Decision documented

- [x] recommended close-with-rollup path documented
- [x] optional final batch criteria documented
- [x] optional final batch milestone path documented
- [x] next rollup milestone recommended

## Safety documented

- [x] preserve fallback text
- [x] preserve route behavior
- [x] preserve HTTP status codes
- [x] preserve URLs and query strings
- [x] preserve dynamic values
- [x] preserve generated content
- [x] preserve OCR output
- [x] preserve course output
- [x] preserve user-authored corrections
- [x] preserve v0.2.81 `_html_escape(str(page))` XSS fix
- [x] escape dynamic HTML values
- [x] avoid broad UI rewrite

## Deferred

- [ ] full UI localization rollup
- [ ] optional final batch decision
- [ ] additional language-pack JSON additions
- [ ] additional UI integration
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

This milestone recommends closing the current full UI localization implementation sequence with a rollup, unless a final low-risk batch is explicitly justified later.
