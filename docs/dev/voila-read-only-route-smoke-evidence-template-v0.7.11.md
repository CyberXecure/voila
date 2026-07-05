# Voila v0.7.11 read-only route smoke evidence template

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

## Evidence status

This file is a template/baseline for manual owner-local evidence. It does not claim that a live manual smoke session has been completed unless entries are filled by the owner.

## Manual evidence table

| ID | Route | Method | Classification | Preconditions | Expected safe outcome | Actual observed outcome | Result | Evidence note | Follow-up |
|---:|---|---:|---|---|---|---|---|---|---|
| 01 | `/health` | GET | READ_ONLY_GET | App already running locally | Health response | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 02 | `/` | GET | READ_ONLY_GET | App already running locally | Home/library or empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 03 | `/quick-tools` | GET | READ_ONLY_GET | App already running locally | Existing quick tools page | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 04 | `/course-tools` | GET | DATA_DEPENDENT_GET | Existing local course may be required | Existing tools page or safe empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 05 | `/view-course` | GET | DATA_DEPENDENT_GET | Existing local course may be required | Course view or safe missing-course state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 06 | `/view-figures` | GET | DATA_DEPENDENT_GET | Existing local figures may be required | Figures view or safe empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 07 | `/review` | GET | DATA_DEPENDENT_GET | Existing local quiz/course may be required | Review page or safe empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 08 | `/review-concepts` | GET | DATA_DEPENDENT_GET | Existing local concepts may be required | Concepts review or safe empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 09 | `/review-ocr-text` | GET | DATA_DEPENDENT_GET | Existing local OCR pages may be required | OCR review or safe missing-data state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 10 | `/review-ocr-corrected` | GET | DATA_DEPENDENT_GET | Existing corrected OCR may be required | Corrected OCR view or safe empty state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 11 | `/edit-crops` | GET | DATA_DEPENDENT_GET | Existing local pages/images may be required | Crop editor or safe missing-data state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 12 | `/progress` | GET | DATA_DEPENDENT_GET | Existing local progress may be required | Progress dashboard or safe no-progress state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 13 | `/study` | GET | DATA_DEPENDENT_GET | Existing local course may be required | Study page or safe missing-course state | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 14 | `/exam-prep` | GET | READ_ONLY_GET | App already running locally | Exam Prep page | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 15 | `/log` | GET | READ_ONLY_GET | App already running locally | Log/debug surface if available | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 16 | `/ocr-page-image` | GET | PARAMETERIZED_GET | Query parameters/data may be required | Image or safe missing-parameter response | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 17 | `/owner/ocr-math-report/{course_id}/summary.json` | GET | PARAMETERIZED_GET | Existing course id may be required | JSON summary or safe missing-report response | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 18 | `/owner/ocr-math-report/{course_id}/ocr_math_report.md` | GET | PARAMETERIZED_GET | Existing course id may be required | Markdown report or safe missing-report response | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |
| 19 | `/owner/ocr-math-report/{course_id}/view` | GET | PARAMETERIZED_GET | Existing course id may be required | Viewer page or safe missing-report response | Not run in this doc baseline | PENDING_MANUAL | Documentation-only baseline | None |

## Explicitly skipped write/destructive actions

| Action class | Examples | Result | Reason |
|---|---|---|---|
| Upload | existing upload action | SKIPPED_WRITE | Can create local artifacts. |
| Generate/regenerate | existing generation action | SKIPPED_WRITE | Can create or rewrite course artifacts. |
| Save | existing save actions | SKIPPED_WRITE | Can mutate owner-local artifacts. |
| Delete | existing delete actions | SKIPPED_DESTRUCTIVE | Can remove owner-local data. |
| Reset | existing reset actions | SKIPPED_DESTRUCTIVE | Can clear owner-local progress/state. |
| Rebuild | existing rebuild actions | SKIPPED_WRITE | Can rewrite OCR/course-related artifacts. |
| Answer submission | existing answer/review/study submission actions | SKIPPED_WRITE | Can update owner-local progress or attempts. |

## Result vocabulary

Allowed values:
- `PENDING_MANUAL`
- `PASS`
- `EXPECTED_EMPTY`
- `EXPECTED_404`
- `SKIPPED_NO_SAMPLE`
- `SKIPPED_WRITE`
- `SKIPPED_DESTRUCTIVE`
- `BLOCKED`

Any `BLOCKED` or unexpected result remains evidence only and must not be fixed inside v0.7.11.
