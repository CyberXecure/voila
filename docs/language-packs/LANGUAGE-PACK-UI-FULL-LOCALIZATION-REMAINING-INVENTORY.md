# Voila! UI Full Localization Remaining Inventory

Milestone: v0.2.93-public-beta-language-pack-ui-full-localization-remaining-inventory
Status: inventory
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone inventories remaining UI literals after the v0.2.87 first full UI localization batch and the v0.2.91 next full UI localization batch.

The goal is to decide whether more full UI localization batches are worth doing, or whether the current full UI localization sequence should move toward a rollup.

## Baseline

This inventory builds on:

```text
v0.2.86 full UI localization core keys
v0.2.87 first full UI localization integration
v0.2.88 first batch documentation
v0.2.89 next batch plan
v0.2.90 next-batch core keys
v0.2.91 next full UI localization integration
v0.2.92 next batch documentation
v0.2.81 reflected-XSS fix using _html_escape(str(page))
```

## Inventory target

```text
services/api/web_app.py
```

The scan skips lines already using `_ut(...)` or `_t(...)`.

## Remaining candidate categories

The remaining candidates should be classified into these buckets:

```text
small user-facing literals still worth localizing
mixed HTML response strings that need careful review
developer/debug/status text that can remain English
generated content or OCR/course output that should not be localized
already localized lines
security-sensitive lines requiring explicit escaping review
out of scope for the current full UI sequence
```

## Likely remaining user-facing candidates

The remaining UI surface is expected to be much smaller than before v0.2.87 and v0.2.91.

Likely candidates may include:

```text
small residual route messages
simple remaining links not already covered by ui.link.*
short empty states or helper paragraphs
isolated title/headline strings
```

These should only be integrated if they are clearly user-facing and low risk.

## Caution areas

The next review should be cautious with:

```text
mixed HTML + response strings
error responses with status-code semantics
debug/developer-only strings
generated course content
OCR extracted text
user-authored OCR corrections
large dynamic HTML blocks
Romanian helper text that may need naming/translation strategy
```

## Recommended next action

Recommended next milestone:

```text
v0.2.94-public-beta-language-pack-ui-full-localization-rollup-plan
```

The rollup plan should decide between:

```text
close the full UI localization sequence with a rollup
or
add one final small remaining-literals core-key/integration batch
```

## Safety rules

Any future implementation must preserve:

```text
fallback English text
route behavior
HTTP status codes
URLs
query strings
dynamic values
existing _ut(...) helper behavior
generated content
OCR output
course output
user-authored corrections
v0.2.81 _html_escape(str(page)) reflected-XSS fix
```

Any dynamic value inserted into HTML must be escaped.

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- add a language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.93 is documentation only.

It inventories the remaining full UI localization surface after v0.2.91 and defers any final implementation or rollup decision.
