# v0.7.79 Exam Prep Romanian diacritics polish

Status: PASS_EXAM_PREP_ROMANIAN_DIACRITICS_POLISH

Marker:
VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_CHECK=PASS

Baseline:
v0.7.78 completed and merged to protected main at `73885f3`.

## Purpose

This milestone polishes Romanian diacritics in the Exam Prep UI.

The fix is source-based, not a broad HTML wrapper:

- updates the Bac Matematică M1 skill tree labels/descriptions;
- fixes visible Romanian Exam Prep copy;
- fixes a mojibake keyword set in `study_quiz_builder.py`.

## Validated UI routes

- `/exam-prep`
- `/exam-prep/skill/multimi`

## Validation

- `VOILA_V0_7_79_EXAM_PREP_ROMANIAN_DIACRITICS_BROWSER_TEXT_SMOKE=PASS`
- `ROUTES_CHECKED=2`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

Evidence:

`D:\dev\tester-runs\v0779-exam-prep-romanian-diacritics\V0.7.79-EXAM-PREP-ROMANIAN-DIACRITICS-SMOKE.json`

## Policy

UI copy / Romanian diacritics polish only.

No BKT logic changes.
No Study logic changes.
No Progress logic changes.
No OCR Math changes.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_EXAM_PREP_DIACRITICS_PASS_NOT_PACKAGED
