# Voila v0.7.41 — OCR Math visual fallback and figure candidate audit

Status: AUDIT ONLY
Policy: no build, no ZIP, no share, no delivery, no distribution.

## Decision

Do not force OCR Math to become a perfect formula OCR engine.

Voila should treat OCR Math as a selective diagnostic/router:

- readable OCR text stays text;
- uncertain math/formula/table/graph/symbol-heavy regions become visual fallback candidates;
- visual fallback candidates should flow into Figures / Crop Editor;
- Study should later reference the relevant visual crop instead of relying on broken OCR text.

## Product direction

OCR Math should not try to repair every formula with Tesseract.

Instead, the desired behavior is:

OCR text good enough -> keep as text
Math/formula/table/graph/symbol-heavy OCR uncertain -> create visual fallback candidate
Visual fallback candidate -> available as figure/crop candidate
Crop Editor -> user polishes the capture
Study -> references the polished visual crop

## Current status

### OCR Math report

The current OCR Math report is diagnostic-only.

It reads text candidates such as:

- pages.md
- course.cleaned.md
- course.md

It produces:

- ocr_math_report.json
- ocr_math_report.md

It counts risky math/mixed/text lines and reports suggestions.

It does not modify:

- OCR text;
- Course;
- Study;
- Progress;
- ZIP;
- delivery;
- distribution.

### Page image source

The Tesseract page OCR pipeline already renders full page images under:

ocr/page_images/page_XXXX.png

These page images are the safest source for visual fallback candidates.

### Figures / Crop direction

Figures and Crop Editor should become the downstream path for math visual fallback.

OCR Math should not directly crop, rewrite Study, or rewrite OCR text in this audit.

First it should create a clear diagnostic manifest contract.

## Proposed future contract

Future diagnostic manifest shape:

{
  "visual_fallback_candidates": [
    {
      "candidate_id": "math-p003-001",
      "page_number": 3,
      "source": "ocr_math_report",
      "reason": "math_or_symbol_dense_line",
      "line_number": 42,
      "risk_level": "high",
      "capture_source": "ocr/page_images/page_0003.png",
      "crop_status": "needs_crop",
      "figure_candidate": true,
      "study_reference_allowed": true
    }
  ]
}

## Recommended sequence

### v0.7.41

Document this audit and freeze the product decision.

No runtime behavior changes.

### v0.7.42

Generate diagnostic-only visual_fallback_candidates.json from OCR Math report and available page images.

No Course/Study rewrite.

### v0.7.43

Expose visual fallback candidates as figure/crop candidates.

No automatic crop polish.

### v0.7.44

Allow Study to reference already-cropped visual fallback figures.

Study should show text such as:

Consultă captura relevantă din pagina X.

## Non-goals

- No Formula OCR provider integration.
- No Mathpix / cloud / LLM dependency.
- No automatic LaTeX conversion.
- No forced Tesseract formula repair.
- No rewrite of OCR text.
- No rewrite of Study or Progress in this audit.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.

## Final marker

VOILA_V0_7_41_OCR_MATH_VISUAL_FALLBACK_AUDIT_CHECK=PASS
POLICY=no_build_no_zip_no_share_no_delivery_no_distribution
