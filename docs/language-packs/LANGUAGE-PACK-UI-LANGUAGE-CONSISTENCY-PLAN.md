# Voila! UI Language Consistency Plan

Milestone: v0.2.43-public-beta-language-pack-ui-language-consistency-plan
Status: planning
Scope: documentation only; no runtime changes, no UI code changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone defines the UI language consistency policy after the v0.2.42 manual RC dry run.

The manual RC dry run passed functionally, but the UI was observed to contain mixed English/Romanian labels.

## Decision

Recommended UI language policy:

```text
Default UI language: Romanian
Fallback language: English
Adaptive/browser-locale behavior: planned later
```

## Why Romanian default

Voila is currently being prepared and tested primarily in a Romanian-language workflow.

A Romanian default gives the product a more coherent first-run experience for the intended initial audience.

## Why English fallback

English should remain the safe fallback because:

- many existing labels are already English
- developer-facing/debug labels may remain English temporarily
- language-pack keys may be incomplete during transition
- English is useful for public beta users outside Romania

## Why adaptive language is deferred

Adaptive language detection should not be added until the app has:

- a clear language selector
- stable language-pack-backed UI keys
- documented fallback rules
- predictable behavior for browser-locale detection
- tests for Romanian, English, and unsupported locales

## Observed mixed UI examples

During the v0.2.42 manual dry run, examples included:

English labels:

- Upload PDF
- Choose File
- Upload PDF
- Generated
- Source Mode
- Generate course
- Figures
- Edit crops
- Study
- Review weak
- Progress
- Logs
- Delete from library

Romanian labels:

- Deschide cursul

## Non-blocker decision

The mixed UI labels do not block language-pack packaging validation.

They should block only a polished public release where UI consistency is expected.

## Future implementation approach

Recommended follow-up implementation should be staged:

### Phase 1: inventory visible labels

Create an inventory of visible UI labels from:

- home page
- upload flow
- course/library view
- OCR review flow
- study/review tools
- progress/logs area
- delete/actions area

### Phase 2: classify labels

Classify each label as:

- user-facing label
- technical/debug label
- file/status label
- route/tool name
- placeholder/help text
- button/action text

### Phase 3: map to language-pack keys

Each user-facing label should have a stable translation key.

Recommended key style:

```text
ui.upload_pdf
ui.choose_file
ui.generate_course
ui.figures
ui.edit_crops
ui.study
ui.review_weak
ui.progress
ui.logs
ui.delete_from_library
ui.open_course
```

### Phase 4: Romanian first pass

Set Romanian strings as the default UI target for the current beta path.

### Phase 5: English fallback pass

Confirm every Romanian key has an English fallback.

### Phase 6: selector/adaptive plan

Only after Romanian/English consistency is stable, plan:

- explicit language selector
- browser-locale detection
- persisted user preference
- fallback to English for unsupported locales

## Safety

This milestone must not:

- modify runtime behavior
- modify UI code
- upload assets to GitHub Releases
- create a Git tag
- publish the ZIP
- overwrite v0.2.0-public-beta assets
- add or modify LICENSE files

## Recommended next milestone

```text
v0.2.44-public-beta-language-pack-ui-label-inventory
```

Suggested next work:

- inventory visible mixed-language labels
- document each label and proposed key
- do not change UI behavior yet

## Decision for this milestone

v0.2.43 is documentation only.

It establishes the policy: Romanian default, English fallback, adaptive later.
