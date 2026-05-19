# Voila! UI Remaining Labels Plan Checklist

Milestone: v0.2.58-public-beta-language-pack-ui-remaining-labels-plan
Status: planning checklist
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Baseline reviewed

- [x] v0.2.50 minimal UI integration completed
- [x] v0.2.53 UI expansion completed
- [x] v0.2.56 UI next-batch integration completed
- [x] v0.2.57 UI next-batch docs completed
- [x] current smoke helpers reviewed

## Scan lessons documented

- [x] broad scan terms can produce false positives
- [x] Back can match CSS background
- [x] generated/log/debug text should be separated from UI labels
- [x] long helper text should not be forced into short ui.* keys
- [x] Choose a PDF helper text should not be replaced with ui.choose_file

## Remaining categories planned

- [x] short UI labels
- [x] existing translated legacy keys
- [x] long helper text
- [x] generated content / document content
- [x] debug / error / developer text
- [x] status messages

## Future key groups planned

- [x] short navigation labels
- [x] longer helper/message keys
- [x] status keys

## Future implementation rules

- [x] inspect exact context before patching
- [x] classify each occurrence before replacing
- [x] reuse existing keys only when semantically exact
- [x] add missing keys in a dedicated planning milestone
- [x] add smoke tests for each implementation batch
- [x] avoid broad UI rewrite
- [x] avoid language selector work
- [x] avoid schema changes in this milestone

## Deferred

- [ ] full UI localization
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching
- [ ] remaining-label implementation
- [ ] new helper/message/status key implementation

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

This milestone plans the remaining UI label classification only.

Implementation should happen in a later milestone.
