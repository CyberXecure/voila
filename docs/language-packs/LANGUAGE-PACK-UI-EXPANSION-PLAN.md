# Voila! UI Expansion Plan

Milestone: v0.2.52-public-beta-language-pack-ui-expansion-plan
Status: planning
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the second small UI language-pack integration batch after the successful v0.2.50 minimal UI key integration.

The goal is to continue reducing mixed English/Romanian UI labels without a broad UI rewrite.

## Baseline

Completed milestones:

- v0.2.47 added `ui.*` keys to Romanian and English core language packs.
- v0.2.50 integrated `ui.upload_pdf`, `ui.generate_course`, and `ui.open_course`.
- v0.2.51 documented the minimal UI integration.

## Proposed second batch

Recommended next UI labels:

```text
ui.choose_file
ui.figures
ui.study
ui.progress
ui.delete_from_library
```

## Why these labels

### ui.choose_file

Visible near upload flow. It improves the first-run upload experience.

### ui.figures

Visible in generated course actions. Safe, short, and already mapped.

### ui.study

Already used in several places through older `_ut("study", "Study")`; can be migrated carefully to `ui.study` where appropriate.

### ui.progress

Already visible and already covered by older translation paths; should be aligned with the new `ui.*` namespace later.

### ui.delete_from_library

Important user-facing destructive action. Should be localized only after confirming JavaScript fallback behavior stays safe.

## Recommended integration order

### Phase 1: inspect current locations

Find occurrences of:

```text
Choose File
Figures
Study
Progress
Delete from library
```

Likely file:

```text
services/api/web_app.py
```

### Phase 2: classify each occurrence

Before patching, classify each label as:

- visible user-facing label
- JavaScript-generated label
- navigation label
- debug/status label
- already localized by older `_ut(...)` key

### Phase 3: patch only safe labels

Recommended first patch for the next implementation milestone:

```text
Figures -> ui.figures
Study -> ui.study where already safe
Progress -> ui.progress where already safe
```

Treat `Delete from library` carefully because it is currently injected via JavaScript.

### Phase 4: add smoke helper

Add a focused smoke helper similar to:

```text
scripts/language-packs/smoke-ui-expansion-key-integration.py
```

The smoke helper should verify that intended `ui.*` snippets exist and selected old hardcoded snippets were removed only where intentionally replaced.

### Phase 5: run validation

Run all existing language-pack and UI-key checks, plus the new expansion smoke helper.

## Important safety rule

Do not attempt full UI localization in this milestone series step.

Keep the next implementation small and reversible.

## Non-goals

This milestone does not:

- modify `services/api/web_app.py`
- modify UI JavaScript
- modify language-pack JSON
- modify runtime behavior
- modify schema
- add language selector
- add browser-locale detection
- add persisted language preference
- change release assets
- create Git tag
- upload GitHub release files

## Recommended next milestone

```text
v0.2.53-public-beta-language-pack-ui-expansion
```

Suggested next work:

- inspect exact UI label locations
- integrate a small second batch
- add focused smoke coverage
- keep the change narrow

## Decision

v0.2.52 is documentation only.

It plans the next controlled UI language-pack expansion after the minimal integration succeeded.
