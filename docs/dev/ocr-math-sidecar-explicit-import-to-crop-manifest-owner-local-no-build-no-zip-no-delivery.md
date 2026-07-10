# v0.7.46 OCR Math sidecar explicit import to Crop Editor manifest

Status: IMPLEMENTED / EXPLICIT OWNER-LOCAL IMPORT ONLY

Marker:
VOILA_V0_7_46_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_TO_CROP_MANIFEST_OWNER_LOCAL_CHECK=PASS

## Scope

This milestone adds an explicit owner-local importer from the OCR Math sidecar into the Crop Editor manifest.

Input:

- `figures_hybrid/ocr_math_visual_fallback_manifest.json`

Target, only when explicitly requested with `--apply`:

- `figures_hybrid/figures_manifest.hybrid.json`

Default mode is dry-run.

## Safety contract

The importer does not modify the Crop Editor manifest unless `--apply` is passed.

When `--apply` is used, the importer:

- creates `figures_manifest.hybrid.json.v0.7.46.bak` before writing
- imports each sidecar candidate at most once
- skips duplicates by `source_candidate_id`
- copies preview images into `figures_hybrid/crops/`
- marks imported items with `ocr_math_visual_fallback_imported_from_sidecar`
- marks crop rectangles as `default_full_page_pending_owner_crop`

## Validation

Validated by fixture:

- dry-run does not write manifest
- dry-run does not create backup
- dry-run does not copy preview
- explicit `--apply` imports one item
- explicit `--apply` creates backup
- explicit `--apply` copies preview
- second `--apply` imports zero items
- duplicate sidecar candidate is skipped

## Policy

Explicit owner-local import only.
No automatic import.
No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No build.
No ZIP.
No share.
No delivery.
No distribution.
