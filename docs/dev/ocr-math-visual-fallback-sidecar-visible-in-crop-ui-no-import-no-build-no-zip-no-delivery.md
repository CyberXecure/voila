# v0.7.44 OCR Math visual fallback sidecar visible in Crop UI

Status: IMPLEMENTED / READ-ONLY UI ONLY

Marker:
VOILA_V0_7_44_OCR_MATH_VISUAL_FALLBACK_SIDECAR_VISIBLE_IN_CROP_UI_CHECK=PASS

## Scope

This milestone makes the v0.7.43 OCR Math visual fallback sidecar visible in the Crop Editor UI as a separate read-only section.

Input sidecar:

- `figures_hybrid/ocr_math_visual_fallback_manifest.json`

Existing Crop Editor manifest remains:

- `figures_hybrid/figures_manifest.hybrid.json`

## Safety contract

This milestone does not import sidecar candidates into the real Crop Editor manifest.

This milestone does not overwrite:

- `figures_hybrid/figures_manifest.hybrid.json`
- `figures_hybrid/figures_hybrid.html`

This milestone does not modify:

- OCR text
- Course
- Study
- Progress
- existing crop rectangles
- existing figure crops

## Policy

No import.
No build.
No ZIP.
No share.
No delivery.
No distribution.

## Next allowed step

A later milestone may add an explicit owner-local import action from sidecar candidates into the Crop Editor manifest.
