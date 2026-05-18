# Voila! UI Next Batch Plan Checklist

Milestone: v0.2.55-public-beta-language-pack-ui-next-batch-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.47 UI core keys implemented
- [x] v0.2.50 minimal UI integration completed
- [x] v0.2.53 UI expansion completed
- [x] v0.2.54 UI expansion docs completed
- [x] existing UI smoke helpers reviewed

## Candidate keys considered

- [x] ui.edit_crops
- [x] ui.review_weak
- [x] ui.generated
- [x] ui.source_mode
- [x] ui.choose_file

## Candidate decisions

- [x] ui.edit_crops likely safe if simple visible label
- [x] ui.review_weak likely safe if simple visible label
- [x] ui.generated requires careful status-text classification
- [x] ui.source_mode requires exact location inspection
- [x] ui.choose_file deferred unless a visible hardcoded label is found

## Implementation rules planned

- [x] inspect exact locations before patching
- [x] classify each occurrence before replacing
- [x] patch only visible user-facing labels
- [x] keep implementation narrow
- [x] preserve fallback behavior
- [x] add focused smoke helper
- [x] avoid broad UI rewrite
- [x] avoid language selector
- [x] avoid browser-locale detection
- [x] avoid schema changes

## Future validation planned

- [x] language-pack packaging inspection
- [x] language-pack validation
- [x] runtime tests
- [x] minimal runtime tests
- [x] UI core key tests
- [x] UI language endpoint smoke
- [x] core runtime helper smoke
- [x] language-pack file smoke
- [x] UI core key smoke
- [x] minimal UI key integration smoke
- [x] UI expansion key integration smoke
- [x] future next-batch smoke helper
- [x] Python compile

## Deferred

- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] public release asset update

## Safety

- [x] no UI code change in this milestone
- [x] no runtime behavior change in this milestone
- [x] no schema change in this milestone
- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no LICENSE change

## Decision

This milestone plans the next UI integration batch only.

Implementation should happen in a later milestone.
