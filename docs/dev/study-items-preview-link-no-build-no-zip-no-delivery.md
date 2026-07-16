# v0.7.83 Study items preview link

Status: PASS_STUDY_ITEMS_PREVIEW_LINK

Marker:
VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_CHECK=PASS

Baseline:
v0.7.82 completed and merged to protected main at `6bc8071`.

## Purpose

This milestone adds an owner-local visible link from Course Tools to the Study items preview viewer.

The link helps the owner open the v0.7.82 read-only preview page without typing the route manually.

## Scope

Changed:

- `services/api/web_app.py`

Added Course Tools card:

- title: `Study Items Preview`
- route: `/owner/study-items-preview/{course_id}/view`
- availability: only when `study_items.preview.json` exists
- policy: preview only, read-only

## Validation

Source inspect evidence:

`D:\dev\tester-runs\v0783-study-items-preview-link\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-SOURCE-INSPECT.json`

Target inspect evidence:

`D:\dev\tester-runs\v0783-study-items-preview-link\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-TARGET-INSPECT.json`

Smoke evidence:

`D:\dev\tester-runs\v0783-study-items-preview-link\V0.7.83-STUDY-ITEMS-PREVIEW-LINK-SMOKE.json`

Validated markers:

- `VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SOURCE_INSPECT=PASS`
- `VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_TARGET_INSPECT=PASS`
- `VOILA_V0_7_83_STUDY_ITEMS_PREVIEW_LINK_SMOKE=PASS`
- `course_tools_status=200`
- `link_visible=True`
- `viewer_href_visible=True`
- `viewer_target_status=200`
- `preview_card_available=True`
- `study_integration_changed=False`
- `bkt_logic_changed=False`
- `progress_logic_changed=False`
- `generator_logic_changed=False`
- `preview_only=True`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

Owner-local visible link only.

No `/study` integration.
No BKT logic change.
No Study state change.
No Progress logic change.
No generator logic change.
No course generation integration.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_LINK_PASS_NOT_INTEGRATED
