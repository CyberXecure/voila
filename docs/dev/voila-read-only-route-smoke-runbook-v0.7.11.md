# Voila v0.7.11 owner-local read-only route smoke runbook

Milestone: `v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution`

Baseline:
- v0.7.10 completed on protected main.
- Final main HEAD expected at start: `ea7b6ac`.

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

## Purpose

This milestone defines a safe manual route-smoke procedure for existing Voila routes that can be inspected with read-only GET navigation.

It does not automate browser actions, does not submit forms, does not start the application, does not change data, and does not execute route requests from the validation script.

The scope is documentation and read-only static validation only.

## Allowed manual route-smoke mode

Allowed:
- Open existing GET routes manually in an already-running owner-local Voila session.
- Observe visible page load, title/header, empty-state copy, or expected error/parameter requirement.
- Record evidence in the v0.7.11 evidence template.
- Mark routes requiring a course id or local course artifact as `PARAMETERIZED`, `DATA_DEPENDENT`, or `SKIPPED_NO_SAMPLE`.
- Mark write-generating or destructive surfaces as `SKIPPED_WRITE` or `SKIPPED_DESTRUCTIVE`.

Not allowed:
- build
- ZIP
- delivery
- distribution
- public release work
- upload
- generate
- regenerate
- save
- delete
- reset
- POST route smoke
- OCR/pages/course/Study/Progress rewrite
- new routes
- UI changes
- behavior changes

## Manual smoke preconditions

Use this runbook only after the application is already running locally by the owner through the existing development workflow.

This document does not instruct starting the app, packaging the app, or preparing a tester artifact.

Suggested preconditions:
- Current git branch is main after v0.7.10 merge.
- Current main includes v0.7.9 functional audit docs.
- Current main includes v0.7.10 manual smoke evidence docs.
- Existing local data is treated as owner-local and non-distributable.
- No sample course is required for this documentation baseline.

## Route smoke classifications

- `READ_ONLY_GET`: Existing GET route that can be inspected without submitting data.
- `PARAMETERIZED_GET`: Existing GET route that requires query parameters or course id.
- `DATA_DEPENDENT_GET`: Existing GET route whose successful render depends on local owner data.
- `EXPECTED_404_OR_EMPTY_STATE`: Existing route may produce a safe not-found or empty-state response.
- `SKIPPED_WRITE`: Existing action is excluded because it can create or rewrite local artifacts.
- `SKIPPED_DESTRUCTIVE`: Existing action is excluded because it can delete/reset/overwrite local data.
- `OUT_OF_SCOPE`: Anything requiring build, ZIP, delivery, distribution, UI change, runtime change, or public expansion.

## Manual evidence rules

Each route observation should record:
- route
- method
- classification
- precondition
- expected safe outcome
- actual observed outcome
- evidence note
- result: `PASS`, `EXPECTED_EMPTY`, `EXPECTED_404`, `SKIPPED_NO_SAMPLE`, `SKIPPED_WRITE`, `SKIPPED_DESTRUCTIVE`, or `BLOCKED`
- follow-up: documentation-only note unless a separate explicitly approved behavior milestone is created

A failed observation in this milestone does not authorize fixing application behavior.
Any bug, broken link, confusing copy, or missing state must be recorded only as evidence.

## v0.7.11 route-smoke sequence

Recommended order:
1. `/health`
2. `/`
3. `/quick-tools`
4. `/course-tools`
5. `/view-course`
6. `/view-figures`
7. `/review`
8. `/review-concepts`
9. `/review-ocr-text`
10. `/review-ocr-corrected`
11. `/edit-crops`
12. `/progress`
13. `/study`
14. `/exam-prep`
15. `/log`
16. `/ocr-page-image`
17. `/owner/ocr-math-report/{course_id}/summary.json`
18. `/owner/ocr-math-report/{course_id}/ocr_math_report.md`
19. `/owner/ocr-math-report/{course_id}/view`

Parameterized/data-dependent routes may be marked safely without forcing local artifact creation.

## Completion criteria

v0.7.11 is complete when:
- this runbook exists
- the route smoke map exists
- the evidence template exists
- the policy document exists
- the check script validates required documents and static route references
- the check script does not run build, packaging, delivery, distribution, app startup, or live HTTP route tests
- final validation prints `VOILA_V0_7_11_READ_ONLY_ROUTE_SMOKE_DOC_CHECK=PASS`
