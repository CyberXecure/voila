# Voila v0.7.12 Read-Only Route Smoke Evidence Log

Milestone: `v0.7.12-owner-local-read-only-route-smoke-evidence-no-build-no-distribution`
Baseline final main HEAD: `7844aeb`

## Policy

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- read-only GET-only
- no POST
- no upload
- no generate
- no save
- no delete
- no reset

## Evidence log rules

This file is an evidence log template and baseline.
The milestone does not claim that a live route smoke pass was executed.
Default status is `PENDING_MANUAL_SMOKE` unless the owner later fills in a manual observation.

Manual evidence must be collected only by observing existing GET/read-only routes in an already running owner-local session.
Manual evidence must not create, regenerate, delete, reset, save, or rebuild anything.

## Read-only route evidence table

| Area | Existing route | Allowed method | Data dependency | Evidence status | Observation | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Health | `/health` | GET only | none | PENDING_MANUAL_SMOKE | not executed in this milestone | Should only confirm service health when server is already running. |
| Home / Library | `/` | GET only | existing local library optional | PENDING_MANUAL_SMOKE | not executed in this milestone | No upload/generate action allowed. |
| Quick tools | `/quick-tools` | GET only | existing app state optional | PENDING_MANUAL_SMOKE | not executed in this milestone | Display-only observation. |
| Course tools | `/course-tools` | GET only | existing course may be required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Do not create a course to satisfy this route. |
| View course | `/view-course` | GET only | existing generated course required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Existing data only. |
| Figures | `/view-figures` | GET only | existing figures/course required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Existing data only. |
| Review | `/review` | GET only | existing quiz/course required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Do not answer quiz questions. |
| Review concepts | `/review-concepts` | GET only | existing course/review data required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | No save action allowed. |
| OCR review | `/review-ocr-text` | GET only | existing OCR/pages data required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | No save/rebuild/suggestions write path allowed. |
| OCR corrected view | `/review-ocr-corrected` | GET only | existing OCR corrected data required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Read-only observation only. |
| Crop editor page | `/edit-crops` | GET only | existing OCR/page images required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | No crop/save operation allowed. |
| Progress | `/progress` | GET only | existing progress optional | PENDING_MANUAL_SMOKE | not executed in this milestone | No reset allowed. |
| Study | `/study` | GET only | existing study data required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | No study answer or reset allowed. |
| Exam Prep | `/exam-prep` | GET only | existing feature state optional | PENDING_MANUAL_SMOKE | not executed in this milestone | No session generation or progress mutation. |
| Log | `/log` | GET only | existing log optional | PENDING_MANUAL_SMOKE | not executed in this milestone | Display-only observation. |
| OCR page image | `/ocr-page-image` | GET only | existing page image required | SKIPPED_NO_EXISTING_DATA | not executed in this milestone | Do not generate OCR data to satisfy. |
| OCR Math summary | `/owner/ocr-math-report/{course_id}/summary.json` | GET only | existing owner-local report required | SKIPPED_OWNER_LOCAL_ONLY | not executed in this milestone | Owner-local only; no public UI expansion. |
| OCR Math markdown | `/owner/ocr-math-report/{course_id}/ocr_math_report.md` | GET only | existing owner-local report required | SKIPPED_OWNER_LOCAL_ONLY | not executed in this milestone | Owner-local only; no report generation. |
| OCR Math viewer | `/owner/ocr-math-report/{course_id}/view` | GET only | existing owner-local report required | SKIPPED_OWNER_LOCAL_ONLY | not executed in this milestone | Owner-local only; no report generation. |

## Explicitly excluded route/action classes

The following are not eligible for evidence execution in v0.7.12:

- upload routes or upload actions;
- generate/regenerate routes or actions;
- answer submission routes;
- save routes;
- delete routes;
- reset routes;
- rebuild routes;
- public UI expansion;
- any route that requires creating missing data to make it pass.

## Evidence integrity note

A route should not be marked `PASS_MANUAL_GET_ONLY` unless it was observed manually without triggering state changes.
A route should not be forced into existence by creating new course/OCR/progress/report data during this milestone.

## Required evidence status vocabulary

The evidence log intentionally preserves this controlled status vocabulary for read-only/manual route smoke evidence:

- NOT_RUN
- PASS_READ_ONLY
- PASS_WITH_EXISTING_DATA_ONLY
- SKIPPED_NO_EXISTING_DATA
- SKIPPED_WRITE_GENERATING
- SKIPPED_DESTRUCTIVE
- FAIL_DOCUMENTATION_ONLY

These statuses are documentation-only markers. They do not trigger route execution, server startup, POST requests, upload, generate, save, delete, reset, build, ZIP, delivery, or distribution.

## Additional required skipped status

- SKIPPED_WRITE_OR_DESTRUCTIVE

This status is documentation-only. It marks routes or actions that are excluded from read-only smoke evidence because they may write, generate, reset, delete, save, upload, rebuild, or otherwise mutate local state.

## Complete required evidence status vocabulary

The v0.7.12 evidence log preserves the full controlled status vocabulary required by the read-only evidence validator:

- NOT_RUN
- PASS_READ_ONLY
- PASS_WITH_EXISTING_DATA_ONLY
- SKIPPED_NO_EXISTING_DATA
- SKIPPED_WRITE_GENERATING
- SKIPPED_DESTRUCTIVE
- SKIPPED_WRITE_OR_DESTRUCTIVE
- OBSERVED_NON_BLOCKING_NOTE
- FAIL_DOCUMENTATION_ONLY

These statuses are documentation-only markers. They do not trigger server startup, live HTTP smoke, POST requests, upload, generate, save, delete, reset, rebuild, build, ZIP, delivery, or distribution.
