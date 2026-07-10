# v0.7.47 OCR Math sidecar explicit import button in Crop UI

Status: IMPLEMENTED / EXPLICIT OWNER-LOCAL UI ACTION ONLY

Marker:
VOILA_V0_7_47_OCR_MATH_SIDECAR_EXPLICIT_IMPORT_BUTTON_CROP_UI_OWNER_LOCAL_CHECK=PASS

## Scope

This milestone adds an explicit owner-local import button in the Crop Editor UI.

The button imports OCR Math sidecar candidates from:

- `figures_hybrid/ocr_math_visual_fallback_manifest.json`

into:

- `figures_hybrid/figures_manifest.hybrid.json`

only after an explicit POST action.

## Safety contract

There is no auto-import.

GET rendering of the Crop Editor UI must not:

- modify the Crop Editor manifest
- create a backup
- copy preview files
- import sidecar candidates

The explicit import action:

- requires button click and browser confirmation
- uses the v0.7.46 importer with apply=True
- creates a backup
- skips duplicate `source_candidate_id`
- redirects back with import status

## Validation

Validated by fixture:

- button appears in HTML
- GET render does not auto-import
- POST `/ocr-math-sidecar-import` imports one candidate
- second POST imports zero candidates
- duplicate sidecar candidate is skipped
- backup is created
- preview is copied into `figures_hybrid/crops/`
- import result status is displayed in Crop Editor UI

## Policy

Explicit owner-local import only.
No auto-import.
No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No build.
No ZIP.
No share.
No delivery.
No distribution.
