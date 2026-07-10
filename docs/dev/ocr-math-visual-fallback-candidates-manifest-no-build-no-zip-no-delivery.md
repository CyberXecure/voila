# Voila v0.7.42 — OCR Math visual fallback candidates manifest

Status: IMPLEMENTATION PLAN / DIAGNOSTIC ONLY
Policy: no build, no ZIP, no share, no delivery, no distribution.

## Context

v0.7.41 fixed the product direction:

OCR Math should not be forced to become a perfect formula OCR engine.

Instead, OCR Math acts as a diagnostic/router:

- readable OCR text remains text;
- uncertain math/formula/table/graph/symbol-heavy OCR becomes a visual fallback candidate;
- visual fallback candidates later flow into Figures / Crop Editor;
- Study later references polished crops instead of relying on broken formula OCR.

## v0.7.42 Goal

Add a local diagnostic-only manifest generator:

Input:

- ocr_math_report.json
- pages.md or another source markdown with page headings
- ocr/page_images/page_XXXX.png

Output:

- visual_fallback_candidates.json

The generator maps risky OCR Math suggestions to page-level visual fallback candidates.

## Current repository evidence

OCR Math report already provides:

- ocr_math_report.json
- top_suggestions
- line_number
- source file name, usually pages.md
- rule_id
- severity
- reason
- original / replacement text

The Tesseract OCR page pipeline already produces page images under:

- ocr/page_images/page_XXXX.png

The markdown page structure already uses headings such as:

- ## Page 1
- ## Page 2

This makes page-level mapping possible without rewriting OCR, Course, Study, Progress, Figures, or Crop.

## Proposed generator

New file:

- services/api/ocr_math_visual_fallback_candidates.py

Behavior:

- read ocr_math_report.json from an output folder;
- read pages.md or the source markdown referenced by OCR Math suggestions;
- map each risky line_number to the current page using ## Page N headings;
- reference ocr/page_images/page_XXXX.png;
- write visual_fallback_candidates.json;
- report candidate count and count of candidates with existing page capture.

## Output contract

visual_fallback_candidates.json should contain:

{
  "marker": "VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST",
  "scope": "diagnostic manifest only; no OCR/Course/Study/Progress/Figures/Crop rewrite; no build, no ZIP, no delivery, no distribution",
  "pdf": "example.pdf",
  "output_folder": "path/to/output",
  "source_report": "ocr_math_report.json",
  "source_page_images": "ocr/page_images/page_XXXX.png",
  "candidate_count": 2,
  "candidate_count_with_existing_capture": 2,
  "visual_fallback_candidates": [
    {
      "candidate_id": "math-p001-001",
      "page_number": 1,
      "source": "ocr_math_report",
      "source_file": "pages.md",
      "line_number": 8,
      "rule_id": "arrow_limit",
      "severity": "high",
      "risk_level": "high",
      "reason": "arrow_limit: Possible limit arrow OCR issue",
      "original": "x -> xo",
      "replacement": "x → x0",
      "capture_source": "ocr/page_images/page_0001.png",
      "capture_exists": true,
      "crop_status": "needs_crop",
      "figure_candidate": true,
      "study_reference_allowed": true
    }
  ]
}

## Candidate rules

A visual fallback candidate should be created from OCR Math top suggestions.

Recommended defaults:

- maximum 80 candidates;
- high severity remains high risk;
- formula/limit/integral-like rules become high risk;
- unknown risk defaults to medium;
- each mapped page receives candidate IDs like math-p003-001;
- if no page can be mapped, use math-unknown-001;
- capture_source is null if page_number cannot be mapped;
- capture_exists is true only if the page image exists.

## Fixture validation

A fixture should create:

- temporary output folder;
- pages.md with ## Page 1 and ## Page 2;
- ocr/page_images/page_0001.png;
- ocr/page_images/page_0002.png;
- ocr_math_report.json with two top_suggestions.

Expected validation:

- python -m py_compile services/api/ocr_math_visual_fallback_candidates.py passes;
- generator returns OCR_MATH_VISUAL_FALLBACK_CANDIDATES=PASS;
- candidate_count = 2;
- candidate_count_with_existing_capture = 2;
- visual_fallback_candidates.json exists;
- first candidate maps to page 1;
- second candidate maps to page 2;
- first capture source is ocr/page_images/page_0001.png;
- crop_status is needs_crop;
- study_reference_allowed is true.

## Files expected in v0.7.42

- services/api/ocr_math_visual_fallback_candidates.py
- docs/dev/ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.md
- scripts/dev/check-ocr-math-visual-fallback-candidates-manifest-no-build-no-zip-no-delivery.ps1

## Non-goals

- No OCR text rewrite.
- No Course rewrite.
- No Study rewrite.
- No Progress rewrite.
- No Figures/Crop Editor integration yet.
- No automatic crop polish.
- No Formula OCR provider.
- No Mathpix.
- No cloud/API/LLM dependency.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.

## Final marker

VOILA_V0_7_42_OCR_MATH_VISUAL_FALLBACK_CANDIDATES_MANIFEST_CHECK=PASS
POLICY=no_build_no_zip_no_share_no_delivery_no_distribution
