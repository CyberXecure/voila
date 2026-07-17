# v0.7.89 Formula visual evidence manifest

Status: PASS_FORMULA_VISUAL_EVIDENCE_MANIFEST

Marker:
VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_CHECK=PASS

Baseline:
v0.7.88 completed and merged to protected main at `0c090ff`.

## Purpose

This milestone creates the first owner-local visual evidence artifact for formulas/symbols.

It addresses the v0.7.88 blocker:

`REPORT_REALITY=BLOCKED_NO_VISUAL_EVIDENCE_ARTIFACTS_FOUND`

## Scope

Added:

- `scripts/dev/build-formula-visual-evidence-manifest.py`

Local generated artifacts, not committed:

- `data/output/03-pag-30-34-vectori-trigonometrie/formula_visual_evidence.manifest.json`
- `data/output/03-pag-30-34-vectori-trigonometrie/formula_visual_evidence/pages/*.png`
- `data/output/03-pag-30-34-vectori-trigonometrie/formula_visual_evidence/crops/*.png`

The script:

- uses local PyMuPDF / `fitz`
- renders page images
- finds candidate formula/symbol/text-line regions
- saves visual crops
- writes manifest entries with:
  - page
  - bbox
  - crop path
  - text
  - reasons
  - review status

## Validation

Evidence:

`D:\dev\tester-runs\v0789-formula-visual-evidence-manifest\V0.7.89-FORMULA-VISUAL-EVIDENCE-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0789-formula-visual-evidence-manifest\V0.7.89-FORMULA-VISUAL-EVIDENCE-MANIFEST-SMOKE.json`

Validated markers:

- `VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_SOURCE_INSPECT=PASS`
- `IMPLEMENTATION_READINESS=READY_FOR_LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST`
- `VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_BUILD=PASS`
- `VOILA_V0_7_89_FORMULA_VISUAL_EVIDENCE_MANIFEST_SMOKE=PASS`
- `page_count=5`
- `candidate_count=43`
- `page_image_count=5`
- `sample_crop_exists=True`
- `uses_pymupdf=True`
- `uses_llm=False`
- `uses_cloud=False`
- `ocr_rewrite_performed=False`
- `formula_ocr_performed=False`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

Owner-local formula visual evidence manifest only.

No OCR rewrite.
No full Formula OCR.
No Study learning logic change.
No BKT logic change.
No Progress logic change.
No generator logic change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_FORMULA_VISUAL_EVIDENCE_MANIFEST_PASS_NOT_PACKAGED

## Recommended next milestone

`v0.7.90-owner-local-formula-visual-evidence-viewer-no-build-no-zip-no-delivery`

Expected direction:

- owner-local viewer route for manifest
- display crop cards
- page, bbox, reason, OCR context
- link from OCR Math / OCR Review
- no OCR rewrite yet
