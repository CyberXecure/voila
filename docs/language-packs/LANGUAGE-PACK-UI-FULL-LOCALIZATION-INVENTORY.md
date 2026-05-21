# Voila! UI Full Localization Inventory

Milestone: v0.2.84-public-beta-language-pack-ui-full-localization-inventory
Status: inventory
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone starts a separate full UI localization inventory after completing the scoped UI error/status language-pack sequence.

The goal is to identify likely remaining UI literals and group them into future safe batches without changing runtime behavior.

## Baseline

This inventory builds on:

```text
v0.2.72 error/status core keys
v0.2.75 first error/status integration
v0.2.78 deferred workflow/status integration
v0.2.81 final deferred integration
v0.2.83 error/status rollup
```

The UI error/status route-output sequence is considered complete for the scoped v0.2.72 keys.

## Inventory scope

This inventory is broader than the error/status sequence.

Candidate areas include:

```text
HTMLResponse output
PlainTextResponse output
JSONResponse messages
HTTPException detail text
HTML headings
buttons
labels
links
table headers
form labels
status messages
workflow messages
OCR review UI text
course generation UI text
debug or developer-facing text that may or may not be user-facing
```

## Initial scan target

Initial scan target:

```text
services/api/web_app.py
```

Future inventory passes may include:

```text
services/api/static/*.js
services/api/templates/*
services/api/*.py
scripts used by packaged runtime if user-facing
README/docs snippets only if displayed in app UI
```

## Candidate classification

Future work should classify candidates into these buckets:

```text
Safe user-facing UI literals
Needs context before localization
Developer/debug text
Generated content that should not be localized
OCR/course output that should not be localized
Security-sensitive output
Route/status-code-sensitive output
Already localized
Out of scope
```

## Recommended next inventory method

Use small route-based batches.

Recommended order:

```text
1. Static headings and labels
2. Buttons and navigation labels
3. Form labels and helper text
4. User-facing status messages
5. User-facing JSONResponse/PlainTextResponse text
6. OCR review UI text
7. Course/outline workflow UI text
```

Avoid mixing too many UI surfaces in one implementation milestone.

## Safety rules

Future implementation should:

- use existing language-pack runtime helper behavior
- preserve fallback text
- preserve route behavior
- preserve HTTP status codes
- preserve redirects
- preserve exception behavior
- preserve generated content
- preserve OCR output
- preserve course output
- escape dynamic values inserted into HTML
- add focused smoke helpers for each batch
- keep language-pack JSON changes separate from UI integration where possible
- avoid broad UI rewrites

## Security rule from v0.2.81

When dynamic values are inserted into HTML, they must be escaped.

The v0.2.81 `page_not_found` fix used:

```text
_html_escape(str(page))
```

Future localization work should follow the same rule.

## Recommended future milestones

Suggested next docs-only milestone:

```text
v0.2.85-public-beta-language-pack-ui-full-localization-batch-plan
```

Suggested later implementation approach:

```text
v0.2.86-public-beta-language-pack-ui-full-localization-core-keys
v0.2.87-public-beta-language-pack-ui-full-localization-first-batch
v0.2.88-public-beta-language-pack-ui-full-localization-first-batch-docs
```

Exact milestone names can be adjusted after the inventory is reviewed.

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- add language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.84 is documentation only.

It creates the first inventory document for full UI localization and keeps implementation deferred.
