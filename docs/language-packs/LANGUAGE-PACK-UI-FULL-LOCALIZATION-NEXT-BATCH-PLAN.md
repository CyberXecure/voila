# Voila! UI Full Localization Next Batch Plan

Milestone: v0.2.89-public-beta-language-pack-ui-full-localization-next-batch-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the next small full UI localization batch after the first integration batch completed in v0.2.87 and documented in v0.2.88.

The goal is to inspect remaining user-facing UI literals and select a safe follow-up batch without changing code in this milestone.

## Baseline

This plan builds on:

```text
v0.2.86 full UI localization core keys
v0.2.87 first full UI localization integration batch
v0.2.88 first batch documentation
v0.2.81 reflected-XSS fix using _html_escape(str(page))
```

## Remaining candidate scan

Scan target:

```text
services/api/web_app.py
```

The scan skipped lines already using `_ut(...)` or `_t(...)`.

Observed remaining candidates:

```text
remaining HTML headings: 1
remaining button labels: 0
remaining link labels: 10
remaining form labels: 0
remaining paragraph literals: 10
remaining title literals: 1
```

## Recommended next batch

Recommended next batch focus:

```text
pagination/navigation links
remaining simple study/course/concepts links
short OCR review navigation links
small safe empty-state/help paragraphs
one static title literal
```

This should remain a small route-based batch.

## Candidate link literals

Representative remaining link candidates:

```text
Study
← Previous
Next →
← Prev
Back to OCR Review
Concepts
```

These are generally safe if integrated with existing `_ut(...)` calls while preserving the URLs and dynamic query values.

## Candidate paragraph literals

Representative paragraph candidates:

```text
Your local PDF learning studio
Generate a study quiz first.
Port 8790 is not responding. Start it manually:
No study questions found. Generate Study first.
Concept title cannot be empty.
The correction was not saved because the server raised an exception.
OCR text corrections were applied to course and study.
No PDFs found.
```

The Romanian OCR helper text should be reviewed carefully before localization because it is already non-English and may need a separate decision.

## Candidate title literal

Representative title candidate:

```text
Correct OCR · Voila!
```

This is a good candidate for a `ui.title.*` or `ui.heading.*` style key, depending on how title keys are grouped.

## Recommended exclusions from next batch

Do not include in the next implementation batch unless reviewed separately:

```text
mixed HTML + paragraph response strings with error semantics
debug/developer-only text
generated course content
OCR extracted output
user-authored OCR corrections
large mixed dynamic HTML blocks
already-localized lines
Romanian helper text until naming/translation strategy is confirmed
```

## Suggested future core keys milestone

Recommended next implementation-prep milestone:

```text
v0.2.90-public-beta-language-pack-ui-full-localization-next-batch-core-keys
```

Suggested key groups:

```text
ui.link.*
ui.message.*
ui.title.*
```

Possible candidate keys:

```text
ui.link.previous
ui.link.prev
ui.link.next
ui.link.back_to_ocr_review

ui.message.local_pdf_learning_studio
ui.message.generate_study_quiz_first
ui.message.crop_editor_port_not_responding
ui.message.no_study_questions_found
ui.message.concept_title_cannot_be_empty
ui.message.correction_not_saved_exception
ui.message.ocr_corrections_applied
ui.message.no_pdfs_found

ui.title.correct_ocr
```

Exact key names may be adjusted during the core-key milestone.

## Suggested future integration milestone

Recommended later milestone:

```text
v0.2.91-public-beta-language-pack-ui-full-localization-next-batch
```

It should:

- use only keys added in the next core-key milestone
- preserve fallback English text
- preserve route behavior
- preserve HTTP status codes
- preserve dynamic values
- escape dynamic values inserted into HTML
- add a focused smoke helper
- avoid broad UI rewrite

Suggested smoke helper:

```text
scripts/language-packs/smoke-ui-full-localization-next-batch.py
```

## Safety rules

Future implementation must preserve:

```text
URLs
query strings
route behavior
HTTP status codes
fallback text
dynamic values
existing _ut(...) helper behavior
generated content
OCR output
course output
user-authored corrections
```

Future implementation must avoid:

```text
broad UI rewrites
language selector changes
browser-locale detection
persisted language preference changes
adaptive UI switching
release upload
Git tag
public ZIP publish
LICENSE changes
```

## Security note

The v0.2.81 page-not-found fix remains the reference for dynamic values inserted into HTML:

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

v0.2.89 is documentation only.

It plans the next full UI localization batch and keeps implementation deferred to later milestones.
