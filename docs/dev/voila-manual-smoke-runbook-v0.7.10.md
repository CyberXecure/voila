# Voila v0.7.10 Owner-local Manual Smoke Runbook

Milestone: `v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution`

Baseline:
- previous stable milestone: `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution`
- expected protected main HEAD before branch: `6edffbd`

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

## Purpose

This runbook defines the manual smoke session for the current Voila application state without changing behavior.

The goal is evidence collection only:
- confirm existing surfaces can be manually checked
- distinguish read-only checks from write-generating checks
- explicitly skip destructive actions
- record observations without fixes

## Execution boundary

Allowed:
- use an already existing local Voila owner environment
- open already existing routes manually
- inspect already existing pages and already generated local artifacts
- record observations in the evidence table
- run the v0.7.10 validation script, which only reads files and scans text

Not allowed:
- no build
- no ZIP
- no delivery
- no distribution
- no new public UI
- no behavior change
- no OCR/pages/course/Study/Progress rewrite
- no generated package
- no release assets
- no automatic upload/generate/regenerate test
- no delete/reset action

## Manual smoke status vocabulary

Use only these statuses in the evidence table:

| Status | Meaning |
| --- | --- |
| `PASS` | Existing surface loaded or behaved as expected during manual read-only observation |
| `WARN_OBSERVED` | Surface loaded but there is an observation worth tracking later |
| `BLOCKED_NO_LOCAL_ARTIFACT` | Check needs an existing local course/report/artifact that was not present |
| `SKIPPED_WRITE` | Check would create or rewrite local data and is intentionally skipped |
| `SKIPPED_DESTRUCTIVE` | Check would delete/reset data and is intentionally skipped |
| `NOT_RUN` | Not executed during the manual session |

## Suggested manual order

1. Confirm repository is on protected `main` after v0.7.9.
2. Start Voila only through the existing owner-local workflow if you already intended to do so.
3. Open read-only surfaces first.
4. Do not press buttons that generate, regenerate, save, delete, or reset.
5. Record results in `docs/dev/voila-manual-smoke-evidence-v0.7.10.md`.
6. Run `scripts/dev/check-voila-manual-smoke-evidence-v0.7.10.ps1`.
7. Commit only the v0.7.10 docs and validation script.

## Read-only surfaces eligible for manual observation

These checks are allowed only as manual observations of current existing behavior:

- `/health`
- `/`
- `/view-course`
- `/view-figures`
- `/progress`
- `/study`
- `/review`
- `/quick-tools`
- `/course-tools`
- `/owner/ocr-math-report/{course_id}/view`
- `/owner/ocr-math-report/{course_id}/summary.json`
- `/owner/ocr-math-report/{course_id}/ocr_math_report.md`

## Write-generating or destructive surfaces to skip

These are documented for audit coverage but must not be executed in this milestone:

- `/generate`
- `/upload`
- `/delete-course`
- `/delete-from-library`
- `/review-answer`
- `/study-answer`
- `/study-reset`
- `/review-concepts/save`
- `/review-ocr-text/save`
- `/review-ocr-text/rebuild`

## Evidence rule

If an issue is observed, record it as `WARN_OBSERVED` or `OBSERVED_ISSUE_NO_FIX` in notes.
Do not fix it in v0.7.10.
A future milestone must be explicitly created for fixes.