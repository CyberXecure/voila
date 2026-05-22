# Voila! UI Full Localization Remaining Inventory Checklist

Milestone: v0.2.93-public-beta-language-pack-ui-full-localization-remaining-inventory
Status: inventory checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.92 next batch docs completed
- [x] v0.2.91 next batch smoke passed
- [x] v0.2.90 next-batch core keys confirmed
- [x] v0.2.88 first batch docs completed
- [x] v0.2.87 first batch smoke passed
- [x] v0.2.81 XSS fix confirmed
- [x] baseline validation passed
- [x] remaining UI literal inventory scan completed

## Candidate buckets documented

- [x] small user-facing literals still worth localizing
- [x] mixed HTML response strings that need careful review
- [x] developer/debug/status text that can remain English
- [x] generated content or OCR/course output that should not be localized
- [x] already localized lines
- [x] security-sensitive lines requiring explicit escaping review
- [x] out of scope for the current full UI sequence

## Caution areas documented

- [x] mixed HTML + response strings
- [x] error responses with status-code semantics
- [x] debug/developer-only strings
- [x] generated course content
- [x] OCR extracted text
- [x] user-authored OCR corrections
- [x] large dynamic HTML blocks
- [x] Romanian helper text requiring naming/translation strategy

## Future decision documented

- [x] rollup-plan milestone recommended
- [x] option to close the full UI sequence documented
- [x] option for one final small remaining-literals batch documented

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

## Deferred

- [ ] final full UI localization rollup plan
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

This milestone inventories remaining full UI localization literals after v0.2.91.

Implementation, if any, is deferred.
