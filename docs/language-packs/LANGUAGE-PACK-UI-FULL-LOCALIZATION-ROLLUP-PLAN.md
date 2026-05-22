# Voila! UI Full Localization Rollup Plan

Milestone: v0.2.94-public-beta-language-pack-ui-full-localization-rollup-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone decides the next direction for the full UI localization workstream after the first two integration batches and the remaining-inventory milestone.

The decision is intentionally documentation-only: either close the current full UI localization sequence with a rollup, or do one final small batch only if the remaining literals are clearly user-facing and low risk.

## Baseline

This rollup plan builds on:

```text
v0.2.84 full UI localization inventory
v0.2.85 first batch plan
v0.2.86 first batch core keys
v0.2.87 first batch integration
v0.2.88 first batch docs
v0.2.89 next batch plan
v0.2.90 next-batch core keys
v0.2.91 next batch integration
v0.2.92 next batch docs
v0.2.93 remaining inventory
v0.2.81 reflected-XSS fix using _html_escape(str(page))
```

## Current status

The major safe full UI localization groups have been integrated:

```text
static headings
simple navigation links
simple button labels
safe form labels
pagination/navigation links
short UI messages
empty-state/help messages
one static title literal
```

The remaining surface should now be treated as a review problem, not a bulk-localization problem.

## Decision recommendation

Recommended path:

```text
close the current full UI localization implementation sequence with a rollup
```

Reasoning:

```text
the largest safe literal groups are already localized
remaining candidates are likely mixed, dynamic, developer-facing, generated, or lower-value
future changes should be handled as small opportunistic patches, not broad batches
```

## Optional final batch criteria

Only create one final small implementation batch if all of these are true:

```text
the candidate is clearly user-facing
the candidate is not generated course/OCR/user-authored content
the candidate does not change route behavior or HTTP status semantics
the candidate does not require broad HTML restructuring
dynamic HTML values are explicitly escaped
the key name is obvious and stable
a focused smoke helper can verify it
```

## Recommended next milestone

Recommended next milestone:

```text
v0.2.95-public-beta-language-pack-ui-full-localization-rollup
```

That milestone should document the whole full UI localization sequence from v0.2.84 through v0.2.94.

## Deferred optional path

If a final small implementation batch is chosen instead, use this shape:

```text
v0.2.95-public-beta-language-pack-ui-full-localization-final-batch-plan
v0.2.96-public-beta-language-pack-ui-full-localization-final-batch-core-keys
v0.2.97-public-beta-language-pack-ui-full-localization-final-batch
v0.2.98-public-beta-language-pack-ui-full-localization-final-batch-docs
```

This optional path should only be used if the remaining-inventory scan identifies high-value, low-risk user-facing literals.

## Safety rules

Future implementation must preserve:

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

v0.2.94 is documentation only.

It recommends closing the current full UI localization implementation sequence with a rollup, unless a later review finds one final small, clearly user-facing, low-risk batch.
