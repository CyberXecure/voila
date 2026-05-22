# Voila! UI Full Localization Batch Plan

Milestone: v0.2.85-public-beta-language-pack-ui-full-localization-batch-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the first concrete full UI localization batch after the v0.2.84 inventory.

The goal is to select a small, safe, route-based group of visible UI literals for a future implementation milestone, without changing runtime behavior in this milestone.

## Baseline

This plan builds on:

```text
v0.2.83 error/status rollup
v0.2.84 full UI localization inventory
v0.2.81 CodeQL reflected-XSS fix using _html_escape(str(page))
```

The scoped UI error/status sequence is complete. This plan starts broader full UI localization planning.

## Initial scan summary

The first-batch scan targeted:

```text
services/api/web_app.py
```

Candidate groups found:

```text
static headings
button labels
link labels
form labels
```

Observed candidate counts from the initial scan:

```text
static headings: 12
button labels: 4
link labels: 32
form labels: 1
table headers: 0
option labels: 0
```

## Recommended first full UI localization batch

Recommended first batch:

```text
static headings
simple navigation/link labels
simple button labels
one safe form label
```

Recommended target area:

```text
services/api/web_app.py
```

Recommended first implementation style:

```text
small route-based patch
existing _ut(...) helper
fallback text preserved
no route behavior changes
no status code changes
focused smoke helper
```

## Candidate examples

Representative headings:

```text
Voila!
Voila! Review
Review question
No review questions available
Voila! Review weak concepts
Voila! Progress
Voila! Progress Dashboard
Crop Editor did not start
Source page
Editable OCR text
Suspicious pages
```

Representative button labels:

```text
Save page correction
Save reviewed page
Save as needs review
Apply corrected OCR to pages.json
```

Representative link labels:

```text
Back
Next review
Study
Progress
Continue Study
Course tools
Top
Bottom
Back to Voila
Reload
Concepts
Course
Review OCR
```

Representative form label:

```text
Correct concept title
```

## Recommended exclusions from first batch

Do not include in the first batch:

```text
generated course content
OCR extracted output
user-authored OCR corrections
debug/developer-only text
exception trace text
large HTML blocks with mixed dynamic content
security-sensitive output unless explicitly escaped
already-localized error/status output
```

## Suggested future core keys milestone

Recommended next milestone:

```text
v0.2.86-public-beta-language-pack-ui-full-localization-core-keys
```

It should add core language-pack keys for the selected first batch only.

Suggested key groups:

```text
ui.heading.*
ui.button.*
ui.link.*
ui.label.*
```

Example future keys:

```text
ui.heading.home
ui.heading.review
ui.heading.review_question
ui.heading.no_review_questions
ui.heading.review_weak_concepts
ui.heading.progress
ui.heading.progress_dashboard
ui.heading.crop_editor_not_started
ui.heading.source_page
ui.heading.editable_ocr_text
ui.heading.suspicious_pages

ui.button.save_page_correction
ui.button.save_reviewed_page
ui.button.save_as_needs_review
ui.button.apply_corrected_ocr

ui.link.back
ui.link.next_review
ui.link.study
ui.link.progress
ui.link.continue_study
ui.link.course_tools
ui.link.top
ui.link.bottom
ui.link.back_to_voila
ui.link.reload
ui.link.concepts
ui.link.course
ui.link.review_ocr

ui.label.correct_concept_title
```

Exact key names may be adjusted during the core-key milestone.

## Suggested future integration milestone

Recommended later implementation milestone:

```text
v0.2.87-public-beta-language-pack-ui-full-localization-first-batch
```

It should:

- integrate only the first selected keys
- use `_ut(...)`
- preserve fallback English text
- preserve dynamic values
- escape dynamic values inserted into HTML
- add a focused smoke helper
- avoid broad UI rewrite

Suggested smoke helper:

```text
scripts/language-packs/smoke-ui-full-localization-first-batch.py
```

## Safety rules

Future implementation must:

- preserve fallback text
- preserve HTTP status codes
- preserve redirects
- preserve route behavior
- preserve generated content
- preserve OCR output
- preserve course output
- preserve user-authored corrections
- escape dynamic HTML values
- avoid changing CSS/JS behavior while localizing labels
- keep language-pack JSON additions small and reviewed
- keep integration patches route-scoped

## Security note

The v0.2.81 `page_not_found` fix is the reference rule for dynamic HTML values:

```text
_html_escape(str(page))
```

Any dynamic value inserted into HTML during future localization must be escaped.

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

v0.2.85 is documentation only.

It selects and plans the first safe full UI localization batch, with implementation deferred to later milestones.
