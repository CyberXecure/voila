# Voila! UI Expansion Plan Checklist

Milestone: v0.2.52-public-beta-language-pack-ui-expansion-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.47 UI core keys implemented
- [x] v0.2.50 minimal UI integration completed
- [x] v0.2.51 minimal UI integration docs completed
- [x] current smoke-minimal-ui-key-integration.py reviewed
- [x] existing `ui.*` key set reviewed

## Proposed second batch

- [x] ui.choose_file considered
- [x] ui.figures considered
- [x] ui.study considered
- [x] ui.progress considered
- [x] ui.delete_from_library considered

## Implementation rules planned

- [x] inspect exact locations before patching
- [x] classify each label before replacing
- [x] keep implementation narrow
- [x] preserve fallback behavior
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
- [x] future expansion smoke helper
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

This milestone plans the next UI expansion only.

Implementation should happen in a later milestone.
