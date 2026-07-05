# Voila v0.7.11 read-only route smoke map

Milestone: `v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution`

Policy:
- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- read-only
- GET-only route smoke documentation

## Scope

This map documents existing GET/read-only route smoke targets. It does not introduce new routes, change existing routes, or automate navigation.

## GET/read-only smoke map

| Area | Route | Method | Classification | Manual safe expectation |
|---|---:|---:|---|---|
| Health | `/health` | GET | READ_ONLY_GET | Returns health response or equivalent visible safe response. |
| Library/home | `/` | GET | READ_ONLY_GET | Loads existing owner-local home/library page or empty library state. |
| Quick tools | `/quick-tools` | GET | READ_ONLY_GET | Loads existing quick tools page or safe empty state. |
| Course tools | `/course-tools` | GET | DATA_DEPENDENT_GET | Loads existing tools page when local data exists, otherwise safe empty/parameter state. |
| Course view | `/view-course` | GET | DATA_DEPENDENT_GET | Opens existing course view when local course exists, otherwise expected missing-course state. |
| Figures | `/view-figures` | GET | DATA_DEPENDENT_GET | Opens existing figures page when local figures exist, otherwise safe empty state. |
| Review | `/review` | GET | DATA_DEPENDENT_GET | Opens review surface when local quiz/course artifacts exist, otherwise safe empty state. |
| Concepts review | `/review-concepts` | GET | DATA_DEPENDENT_GET | Opens existing concepts review surface or expected empty state. |
| OCR text review | `/review-ocr-text` | GET | DATA_DEPENDENT_GET | Opens existing OCR review surface or expected missing-course/empty state. |
| OCR corrected review | `/review-ocr-corrected` | GET | DATA_DEPENDENT_GET | Opens corrected OCR review when available, otherwise expected empty state. |
| Crop editor | `/edit-crops` | GET | DATA_DEPENDENT_GET | Opens existing crop editor surface if local pages exist, otherwise safe missing-data state. |
| Progress | `/progress` | GET | DATA_DEPENDENT_GET | Opens existing progress dashboard or safe no-progress state. |
| Study | `/study` | GET | DATA_DEPENDENT_GET | Opens existing study mode or safe missing-course state. |
| Exam Prep | `/exam-prep` | GET | READ_ONLY_GET | Opens existing Exam Prep entry/dashboard without changing data. |
| Log | `/log` | GET | READ_ONLY_GET | Opens existing log/debug surface if enabled by current app behavior. |
| OCR page image | `/ocr-page-image` | GET | PARAMETERIZED_GET | Requires parameters or data; expected safe missing-parameter response is acceptable. |
| OCR Math summary | `/owner/ocr-math-report/{course_id}/summary.json` | GET | PARAMETERIZED_GET | Requires course id; safe missing report response is acceptable. |
| OCR Math Markdown | `/owner/ocr-math-report/{course_id}/ocr_math_report.md` | GET | PARAMETERIZED_GET | Requires course id; safe missing report response is acceptable. |
| OCR Math viewer | `/owner/ocr-math-report/{course_id}/view` | GET | PARAMETERIZED_GET | Requires course id; safe viewer or safe 404/missing report is acceptable. |

## Excluded route/action classes

The following classes are excluded from v0.7.11 route smoke execution:
- upload actions
- generate/regenerate actions
- save actions
- delete actions
- reset actions
- answer submission actions
- rebuild actions
- any route that creates, rewrites, deletes, or mutates owner-local artifacts

These may be listed as existing functionality but must be marked `SKIPPED_WRITE` or `SKIPPED_DESTRUCTIVE`.

## Notes

A route that returns an expected missing-parameter, missing-course, missing-report, 404, or empty state can still be `PASS` or `EXPECTED_EMPTY` for this milestone if the behavior is safe and unchanged.

A route failure does not authorize a patch in v0.7.11.
