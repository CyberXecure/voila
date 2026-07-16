# v0.7.87 Study status and copy consistency

Status: PASS_STUDY_STATUS_COPY_CONSISTENCY

Marker:
VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_CHECK=PASS

Baseline:
v0.7.86 completed and merged to protected main at `793bf79`.

## Purpose

This milestone fixes UI status/copy consistency after Study began using `study_items.preview.json` when Quality gate is PASS.

## Scope

Changed:

- `services/api/web_app.py`

Display/status-only changes:

- Quick Tools now marks `studiu: OK` when Study is available through:
  - `study_items.preview.json` with `quality_gate.preview_quality_status=PASS`
  - or `quiz.study.json`
  - or `quiz.json`
- Course Tools Study card now explains the real source:
  - `study_items.preview.json` when Quality gate is PASS
  - fallback to `quiz.json / quiz.study.json`
- Progress card copy now refers to Study-available questions, not only quiz artifacts.

## Validation

Evidence:

`D:\dev\tester-runs\v0787-study-status-and-copy-consistency\V0.7.87-STUDY-STATUS-COPY-CONSISTENCY-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0787-study-status-and-copy-consistency\V0.7.87-STUDY-STATUS-COPY-CONSISTENCY-SMOKE.json`

Validated markers:

- `VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SOURCE_INSPECT=PASS`
- `VOILA_V0_7_87_STUDY_STATUS_COPY_CONSISTENCY_SMOKE=PASS`
- `course_tools_status=200`
- `quick_tools_status=200`
- `study_status=200`
- `course_tools_study_copy_updated=True`
- `course_tools_progress_copy_updated=True`
- `progress_missing_copy_updated_in_source=True`
- `quick_tools_study_status_ok=True`
- `quick_tools_study_dash_visible=False`
- `study_preview_labels_visible=True`
- `study_logic_changed=False`
- `bkt_logic_changed=False`
- `progress_logic_changed=False`
- `generator_logic_changed=False`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

UI status/copy consistency only.

No Study learning logic change.
No BKT logic change.
No Progress logic change.
No generator logic change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_STUDY_STATUS_COPY_CONSISTENCY_PASS_NOT_PACKAGED
