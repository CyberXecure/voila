# v0.7.90 Formula visual evidence viewer

Status: PASS_FORMULA_VISUAL_EVIDENCE_VIEWER

Marker:
VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_CHECK=PASS

Baseline:
v0.7.89 completed and merged to protected main at `3c67ae6`.

## Purpose

This milestone adds an owner-local read-only viewer for `formula_visual_evidence.manifest.json`.

It makes the v0.7.89 visual formula/symbol crop evidence inspectable in the browser.

## Scope

Changed:

- `services/api/web_app.py`

Added owner-local routes:

- `/owner/formula-visual-evidence/{course_id}/view`
- `/owner/formula-visual-evidence/{course_id}/asset?candidate_id=...`

The asset route is CodeQL-safe: it accepts only a strict candidate id, resolves the crop path from the owner-local manifest, and blocks direct user-provided filesystem paths.

The viewer displays:

- candidate crop image
- page
- bbox
- OCR text
- detection reason
- crop path
- review status

## Validation

Evidence:

`D:\dev\tester-runs\v0790-formula-visual-evidence-viewer\V0.7.90-FORMULA-VISUAL-EVIDENCE-VIEWER-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0790-formula-visual-evidence-viewer\V0.7.90-FORMULA-VISUAL-EVIDENCE-VIEWER-SMOKE.json`

Validated markers:

- `VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SOURCE_INSPECT=PASS`
- `manifest_exists=True`
- `candidate_count=43`
- `page_count=5`
- `sample_crop_exists=True`
- `VOILA_V0_7_90_FORMULA_VISUAL_EVIDENCE_VIEWER_SMOKE=PASS`
- `viewer_status=200`
- `asset_status=200`
- `safe_candidate_id_asset_route=True`
- `unsafe_rel_path_removed=True`
- `bad_asset_blocked=True`
- `candidate_count_visible=True`
- `page_image_count_visible=True`
- `crop_image_renderable=True`
- `text_ocr_visible=True`
- `reason_visible=True`
- `bbox_visible=True`
- `review_status_visible=True`
- `bool_false_labels_visible=True`
- `uses_llm=False`
- `uses_cloud=False`
- `ocr_rewrite_performed=False`
- `formula_ocr_performed=False`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

Owner-local read-only visual evidence viewer only.

No OCR rewrite.
No full Formula OCR.
No OCR Review decision write.
No Study learning logic change.
No BKT logic change.
No Progress logic change.
No generator logic change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_VIEWER_PASS_NOT_PACKAGED

## Recommended next milestone

`v0.7.91-owner-local-formula-visual-evidence-course-tools-link-no-build-no-zip-no-delivery`

Expected direction:

- add Course Tools card/link to Formula visual evidence viewer
- possibly add link from OCR Math report
- no OCR rewrite yet
