# v0.7.43 OCR Math visual fallback candidates to Figures/Crop sidecar

Status: IMPLEMENTED / DIAGNOSTIC SIDECAR ONLY

Marker:
VOILA_V0_7_43_OCR_MATH_VISUAL_FALLBACK_TO_FIGURES_CROP_SIDECAR_CHECK=PASS

## Scope

This milestone adds a local bridge from:

- `visual_fallback_candidates.json`

to:

- `figures_hybrid/ocr_math_visual_fallback_manifest.json`

The output is a sidecar manifest for future Figures/Crop integration.

## Safety contract

This milestone does not overwrite:

- `figures_hybrid/figures_manifest.hybrid.json`
- `figures_hybrid/figures_hybrid.html`

This milestone does not modify:

- OCR text
- Course
- Study
- Progress
- existing Figures gallery
- existing Crop Editor manifest

## Policy

No build.
No ZIP.
No share.
No delivery.
No distribution.

## Next allowed step

A later milestone may decide whether and how the sidecar candidates become visible in the Crop Editor UI.
