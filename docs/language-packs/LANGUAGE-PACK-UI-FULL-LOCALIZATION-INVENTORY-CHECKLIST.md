# Voila! UI Full Localization Inventory Checklist

Milestone: v0.2.84-public-beta-language-pack-ui-full-localization-inventory
Status: inventory checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.83 error/status rollup completed
- [x] v0.2.81 CodeQL/XSS fix confirmed
- [x] existing core language packs confirmed
- [x] existing smoke helpers confirmed
- [x] initial full UI localization candidate scan completed

## Inventory created

- [x] inventory document added
- [x] checklist document added
- [x] full UI localization separated from error/status sequence
- [x] future route-based batching recommended

## Candidate buckets planned

- [x] safe user-facing UI literals
- [x] needs context before localization
- [x] developer/debug text
- [x] generated content that should not be localized
- [x] OCR/course output that should not be localized
- [x] security-sensitive output
- [x] route/status-code-sensitive output
- [x] already localized
- [x] out of scope

## Safety rules documented

- [x] preserve fallback text
- [x] preserve route behavior
- [x] preserve HTTP status codes
- [x] preserve redirects
- [x] preserve exception behavior
- [x] preserve generated content
- [x] preserve OCR output
- [x] preserve course output
- [x] escape dynamic HTML values
- [x] avoid broad UI rewrite
- [x] add focused smoke helpers in future implementation batches

## Deferred

- [ ] language-pack JSON additions
- [ ] UI code integration
- [ ] full UI localization implementation
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

This milestone creates a documentation-only inventory for future full UI localization.
