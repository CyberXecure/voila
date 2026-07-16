# v0.7.86 Study items preview status copy polish

Status: PASS_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH

Marker:
VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_CHECK=PASS

Baseline:
v0.7.85 completed and merged to protected main at `aff459d`.

## Purpose

This milestone fixes stale UI copy after v0.7.84 integrated `study_items.preview.json` into `/study`.

## Scope

Changed:

- `services/api/web_app.py`

Display-only changes:

- Replaces stale preview copy:
  - from `preview only · nu este integrat încă în Study`
  - to `integrat în Study când Quality gate este PASS`
- Replaces confusing `Study integration: False` badge with:
  - `Study integration: activă` when Quality gate is PASS
  - `Study integration: inactivă` otherwise
- Updates Course Tools copy so it no longer says the preview does not modify Study.

## Validation

Evidence:

`D:\dev\tester-runs\v0786-study-items-preview-status-copy-polish\V0.7.86-STUDY-ITEMS-PREVIEW-STATUS-COPY-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0786-study-items-preview-status-copy-polish\V0.7.86-STUDY-ITEMS-PREVIEW-STATUS-COPY-POLISH-SMOKE.json`

Validated markers:

- `VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_SOURCE_INSPECT=PASS`
- `VOILA_V0_7_86_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_SMOKE=PASS`
- `viewer_status=200`
- `course_tools_status=200`
- `status_copy_polished=True`
- `study_integration_badge_polished=True`
- `course_tools_copy_polished=True`
- `stale_preview_only_copy_visible=False`
- `stale_not_integrated_copy_visible=False`
- `study_logic_changed=False`
- `bkt_logic_changed=False`
- `progress_logic_changed=False`
- `generator_logic_changed=False`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

Display-only status/copy polish.

No Study logic change.
No BKT logic change.
No Progress logic change.
No generator logic change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_STATUS_COPY_POLISH_PASS_NOT_PACKAGED
