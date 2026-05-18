# Voila! UI Next Batch Plan

Milestone: v0.2.55-public-beta-language-pack-ui-next-batch-plan
Status: planning
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

Plan the next small UI language-pack integration batch after v0.2.53.

The goal is to reduce hardcoded mixed English/Romanian UI labels while keeping the implementation small, reversible, and smoke-tested.

## Baseline

- v0.2.47 added `ui.*` keys to Romanian and English core packs.
- v0.2.50 integrated `ui.upload_pdf`, `ui.generate_course`, and `ui.open_course`.
- v0.2.53 integrated `ui.figures`, `ui.study`, `ui.progress`, and `ui.delete_from_library`.
- v0.2.54 documented the v0.2.53 UI expansion batch.

## Candidate keys

```text
ui.edit_crops
ui.review_weak
ui.generated
ui.source_mode
ui.choose_file
```

## Candidate assessment

- `ui.edit_crops`: likely safe if current visible labels are simple links/cards.
- `ui.review_weak`: likely safe if the visible label appears as a simple action link.
- `ui.generated`: useful for status labels, but needs careful status-text classification.
- `ui.source_mode`: inspect exact location before patching.
- `ui.choose_file`: defer unless a controlled visible hardcoded label is found.

## Recommended implementation order

```text
1. ui.edit_crops
2. ui.review_weak
3. ui.generated only if the status text is simple and safe
4. ui.source_mode only after exact location inspection
5. ui.choose_file only if a real visible hardcoded label is found
```

## Inspection rules

Before patching, inspect exact locations for:

```text
Edit crops
Review weak
Course generated
Not generated yet
Generated
Source Mode
Choose File
Choose a PDF
```

Classify each occurrence as visible UI label, status text, generated document content, debug/log text, internal data label, or already localized by `_ut(...)`.

Only visible user-facing UI labels should be patched.

## Safety rules

The next implementation milestone must:

- patch only a small number of labels
- preserve fallback behavior
- add a focused smoke helper
- avoid full UI localization
- avoid language selector work
- avoid browser-locale detection
- avoid persisted language preference
- avoid schema changes
- avoid release asset changes

## Suggested smoke helper

```text
scripts/language-packs/smoke-ui-next-batch-key-integration.py
```

It should verify intended `ui.*` snippets exist in `web_app.py`, selected old hardcoded snippets were removed only where intentionally replaced, and no broad rewrite happened.

## Validation required after implementation

Run the existing language-pack, runtime, UI smoke, and Python compile checks. If a new smoke helper is added, run it too.

## Non-goals

This milestone does not modify UI code, language-pack JSON, runtime behavior, schema, release assets, tags, public ZIPs, dependencies, or LICENSE files.

## Recommended next milestone

```text
v0.2.56-public-beta-language-pack-ui-next-batch
```

## Decision

v0.2.55 is documentation only.

It prepares the next safe UI language-pack integration batch.
