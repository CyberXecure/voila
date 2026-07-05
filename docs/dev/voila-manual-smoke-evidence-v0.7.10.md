# Voila v0.7.10 Owner-local Manual Smoke Evidence

Milestone: `v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution`

Policy:
- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no feature changes
- no behavior changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion

## Evidence scope

This file is the manual evidence baseline for current Voila behavior.
It does not prove correctness through automated runtime tests.
It documents what can be safely checked manually and records the current session status.

## Manual session metadata

| Field | Value |
| --- | --- |
| Baseline milestone | `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution` |
| Baseline main HEAD before v0.7.10 | `6edffbd` |
| Evidence milestone | `v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution` |
| Session type | Owner-local manual smoke evidence |
| Build performed | NO |
| ZIP created | NO |
| Delivery performed | NO |
| Distribution performed | NO |
| Behavior changes included | NO |
| Fixes included | NO |

## Manual smoke evidence table

| Area | Existing route/action | Risk class | Manual observation instruction | Expected existing result | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Health | `/health` | read-only | Open health endpoint manually | Existing health response is visible | `PENDING_MANUAL` | No mutation |
| Home/library | `/` | read-only | Open homepage/library manually | Existing library UI loads | `PENDING_MANUAL` | No upload/generate |
| Upload | `/upload` | write-generating | Do not upload | Action skipped | `SKIPPED_WRITE` | Avoid creating local artifacts |
| Generate/regenerate | `/generate` | write-generating | Do not generate or regenerate | Action skipped | `SKIPPED_WRITE` | Avoid rewriting course outputs |
| Delete course | `/delete-course` | destructive | Do not delete | Action skipped | `SKIPPED_DESTRUCTIVE` | Avoid local data loss |
| Delete from library | `/delete-from-library` | destructive | Do not delete | Action skipped | `SKIPPED_DESTRUCTIVE` | Avoid local data loss |
| Course view | `/view-course` | read-only | Open existing course if available | Existing course page loads | `PENDING_MANUAL` | Existing artifact only |
| Figures view | `/view-figures` | read-only | Open existing figures page if available | Existing figures page loads | `PENDING_MANUAL` | Existing artifact only |
| Review | `/review` | read-only plus optional write actions | Open review page only | Existing review surface loads | `PENDING_MANUAL` | Do not submit answer |
| Review answer | `/review-answer` | write-generating | Do not submit answer | Action skipped | `SKIPPED_WRITE` | Avoid local progress mutation |
| Progress | `/progress` | read-only | Open progress page manually | Existing progress dashboard loads | `PENDING_MANUAL` | No reset |
| Study | `/study` | read-only plus optional write actions | Open study page only | Existing study surface loads | `PENDING_MANUAL` | Do not answer |
| Study answer | `/study-answer` | write-generating | Do not submit answer | Action skipped | `SKIPPED_WRITE` | Avoid local progress mutation |
| Study reset | `/study-reset` | destructive | Do not reset | Action skipped | `SKIPPED_DESTRUCTIVE` | Avoid data reset |
| Log | `/log` | read-only | Open log view manually if available | Existing log view loads | `PENDING_MANUAL` | Do not alter logs |
| Crop editor | `/edit-crops` | read-only plus optional write actions | Open crop editor only | Existing crop editor surface loads | `PENDING_MANUAL` | No save/write action |
| Concept review | `/review-concepts` | read-only plus optional write actions | Open concept review page only | Existing concept review surface loads | `PENDING_MANUAL` | Save skipped |
| Concept save | `/review-concepts/save` | write-generating | Do not save | Action skipped | `SKIPPED_WRITE` | Avoid changing local artifacts |
| OCR text review | `/review-ocr-text` | read-only plus optional write actions | Open OCR text review page only | Existing OCR review surface loads | `PENDING_MANUAL` | Save/rebuild skipped |
| OCR text save | `/review-ocr-text/save` | write-generating | Do not save | Action skipped | `SKIPPED_WRITE` | Avoid changing OCR artifacts |
| OCR text rebuild | `/review-ocr-text/rebuild` | write-generating | Do not rebuild | Action skipped | `SKIPPED_WRITE` | Avoid rebuilding OCR text |
| OCR suggestions | `/review-ocr-text/suggestions` | read-only | Open suggestions endpoint/page if available | Existing suggestions surface responds | `PENDING_MANUAL` | No save |
| OCR page image | `/ocr-page-image` | read-only | Open for existing page if available | Existing page image renders | `PENDING_MANUAL` | Existing local artifact only |
| OCR corrected review | `/review-ocr-corrected` | read-only | Open corrected OCR view if available | Existing corrected OCR view loads | `PENDING_MANUAL` | No save |
| Exam Prep | `/exam-prep` | read-only | Open Exam Prep entry page manually | Existing Exam Prep entry surface loads | `PENDING_MANUAL` | No feature changes |
| Owner OCR Math summary | `/owner/ocr-math-report/{course_id}/summary.json` | read-only owner-local | Open for existing course with report | Existing JSON summary is readable | `PENDING_MANUAL` | Existing report only |
| Owner OCR Math markdown | `/owner/ocr-math-report/{course_id}/ocr_math_report.md` | read-only owner-local | Open for existing course with report | Existing markdown report is readable | `PENDING_MANUAL` | Existing report only |
| Owner OCR Math viewer | `/owner/ocr-math-report/{course_id}/view` | read-only owner-local | Open viewer for existing course with report | Existing viewer renders report | `PENDING_MANUAL` | Existing report only |

## Observed issues

| Area | Observation | Impact | Fix included in v0.7.10? | Notes |
| --- | --- | --- | --- | --- |
| N/A | No manual observation recorded yet | N/A | NO | This milestone is evidence scaffolding only until owner fills the table |

## Final evidence summary

| Field | Value |
| --- | --- |
| Manual smoke session completed? | `PENDING_OWNER_MANUAL_SESSION` |
| Read-only surfaces checked? | `PENDING_OWNER_MANUAL_SESSION` |
| Write-generating actions executed? | NO |
| Destructive actions executed? | NO |
| Fixes included? | NO |
| Build/ZIP/delivery/distribution performed? | NO |