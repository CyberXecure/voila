# Voila Functional Audit Inventory v0.7.9

Milestone: `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution`

Baseline: `v0.7.8-owner-local-ocr-math-report-audit-trail-doc-no-build-no-distribution`

Expected protected main HEAD at milestone start: `a2ad6ba`

## Policy

This document is an owner-local functional audit inventory only.

Required policy:

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- no behavior changes

## Purpose

The purpose of v0.7.9 is to create a stable baseline map of the existing Voila application surface before deeper manual smoke evidence is collected in a later milestone.

This milestone does not add product behavior. It records what already exists and separates safe read-only audit checks from checks that may write or regenerate local artifacts.

## Inventory boundaries

The inventory is intentionally conservative. Items listed here are audit targets, not new requirements and not new features.

A listed item means: verify the current implementation surface and preserve its current behavior.

## Core application surfaces

| Area | Existing surface to inventory | Audit type | Writes local data? | Automation status in v0.7.9 |
|---|---|---:|---:|---|
| Health | `/health` | Read-only route smoke | No | Allowed if server is already running |
| Home / Library | `/` | Read-only page smoke plus visual/manual inspection | No for GET; actions may write | GET-only allowed |
| Quick tools | `/quick-tools` | Read-only page smoke | No for GET | GET-only allowed |
| PDF upload | Upload control/action from the existing UI | Manual inventory only | Yes | Do not automate in v0.7.9 |
| Generate course | Existing generate action | Manual inventory only | Yes | Do not automate in v0.7.9 |
| Regenerate course | Existing regenerate action | Manual inventory only | Yes | Do not automate in v0.7.9 |
| Open course | Existing course view action | Read-only page smoke if course already exists | No for GET | Allowed only against existing local data |
| Glossary | Existing glossary output/view/action | Read-only if artifact already exists | No for GET | Allowed only against existing local data |
| Quiz | Existing quiz output/view/action | Read-only if artifact already exists | No for GET | Allowed only against existing local data |
| Flashcards | Existing flashcards output/view/action | Read-only if artifact already exists | No for GET | Allowed only against existing local data |
| Figures gallery | Existing figures/gallery surface | Read-only if artifact already exists | No for GET | Allowed only against existing local data |
| OCR review | Existing OCR review surface | Read-only for review display; actions may write | Mixed | GET/manual only |
| Crop editor | Existing crop editor surface | Manual inventory only | May write crop/OCR-related local data | Do not automate mutating actions |
| Study mode | Existing Study surface | Manual/read-only inventory | May write attempts/progress | Do not automate mutating actions |
| Progress dashboard | Existing Progress surface | Read-only display if data already exists | No for GET | GET-only allowed |
| Exam Prep | Existing `/exam-prep` entry/surfaces | Read-only dashboard smoke; session actions may write | Mixed | GET-only/manual only |

## Owner-local OCR Math report surfaces

| Area | Existing surface | Audit type | Writes local data? | Automation status in v0.7.9 |
|---|---|---:|---:|---|
| Report hook flag | `VOILA_ENABLE_OCR_MATH_REPORT_HOOK` | Static docs/source inventory | No | Text scan only |
| JSON report artifact | `ocr_math_report.json` | Artifact inventory only | Existing file only | Do not generate |
| Markdown report artifact | `ocr_math_report.md` | Artifact inventory only | Existing file only | Do not generate |
| Viewer route | `/owner/ocr-math-report/{course_id}/view` | Read-only route/page inventory | No for GET | Allowed only if server is already running and existing report exists |
| Raw Markdown link | Existing raw report link from viewer | Read-only inventory | No | Manual only |
| v0.7.8 audit trail docs | Existing documentation | Static verification | No | Allowed |

## Expected local artifacts to map, not create

The audit may mention these known artifact families only as existing outputs. v0.7.9 must not create or regenerate them.

- `pages.json`
- `pages.md`
- `course_outline.json`
- `course_outline.md`
- `course.md`
- `course.cleaned.md`
- `glossary.json`
- `quiz.json`
- `flashcards.json`
- OCR corrections JSON files
- `ocr_math_report.json`
- `ocr_math_report.md`

## Existing route inventory approach

The v0.7.9 validation script may scan source files as plain text to list route decorators. It must not start the server, import the application, execute route handlers, upload PDFs, generate courses, or rewrite local course data.

Recommended static route scan targets:

- `services/api/web_app.py`
- any existing API/router files already present in the repository

The route scan result is informational only and must not be treated as a behavior test.

## Existing script inventory approach

The audit may list development scripts such as start/stop/check helpers. It must not execute start scripts, stop scripts, build scripts, packaging scripts, ZIP scripts, release scripts, upload scripts, or distribution helpers.

Allowed in v0.7.9:

- text read of script files
- static grep/select-string checks
- documentation consistency checks

Not allowed in v0.7.9:

- starting Voila automatically
- starting LanguageTool automatically
- running OCR automatically
- running Generate/Regenerează automatically
- building a package
- creating release assets
- publishing or uploading anything

## Risk classification

| Risk class | Meaning | v0.7.9 handling |
|---|---|---|
| Read-only GET | Page/route can be opened without changing data | Allowed only if server already runs |
| Static source/doc check | Text-only inspection | Allowed |
| Existing artifact read | Reads an artifact already present locally | Allowed |
| Local artifact writer | Creates or rewrites course/OCR/progress/session data | Manual inventory only |
| Packaging/distribution | Builds, ZIPs, uploads, releases, shares | Forbidden |

## Completion criteria

v0.7.9 inventory is complete when the repository contains:

- this inventory document
- smoke map document
- functional test checklist document
- functional audit policy document
- read-only validation script

and the validation script reports PASS without performing build, ZIP, delivery, distribution, feature change, OCR/page/course/Study/Progress rewrite, or public UI expansion.