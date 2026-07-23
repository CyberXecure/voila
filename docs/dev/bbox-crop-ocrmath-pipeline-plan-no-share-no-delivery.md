# v0.8.65 BBox/Crop/OCR Math pipeline plan — no share/no delivery

## Purpose

This milestone defines the next canonical user-facing pipeline for Voila.

It is planning only.

No implementation is performed in this milestone.

## Starting point

v0.8.64 ended with:

`V0.8.64_AUDIT_VERDICT=BLOCKED_FOR_TESTER_SHARE`

The reason is product/architecture related, not just a UI bug.

The current flow still has:

- global OCR Math before bbox/crop;
- old shrink/preview/hybrid crop UI;
- LanguageTool present, but not proven as an automatic pipeline artifact;
- Review Document not yet proven as the single real workspace for a newly uploaded PDF.

## Product decision

The canonical user-facing flow must be:

`PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study`

## OCR Math rule

Global OCR Math before bbox/crop is deprecated for the user-facing flow.

OCR Math should run only after a bbox/crop exists.

OCR Math output is only a candidate.

The user must validate it manually before it can feed Study.

Allowed user decisions:

- accept
- edit
- ignore

## Visual/crop rule

The old shrink/preview/hybrid crop flow must be removed from user-facing navigation or clearly deprecated.

The new flow must use bbox as the source of truth.

The crop must be a real local artifact, not only a preview.

Planned canonical visual item shape:

```json
{
  "item_id": "visual-item-001",
  "kind": "formula_or_figure_or_table_or_diagram",
  "page": 3,
  "bbox": [120, 340, 680, 510],
  "bbox_units": "pdf_points_or_pixels_declared",
  "page_image_path": "formula_visual_evidence/pages/page-003.png",
  "crop_path": "formula_visual_evidence/crops/page-003-item-001.png",
  "ocr_math_candidate_text": "",
  "ocr_math_status": "not_run_or_pending_user_validation",
  "user_decision": null,
  "ready_for_study": false
}
```

## LanguageTool rule

LanguageTool may run on the OCR text after text extraction.

LanguageTool suggestions must also be candidates, not automatic truth.

The user must be able to review, accept, edit, or ignore text corrections before they affect clean Study.

## User-facing navigation target

Home should guide the user through one clear path:

1. Upload PDF
2. Pregătește documentul
3. Revizuiește documentul
4. Creează Study curat
5. Învață

Course Tools should not expose duplicate old crop/figure flows as primary actions.

Technical diagnostics may remain collapsed under `Diagnostic tehnic`.

## Explicitly deprecated from primary user flow

- `/owner/ocr-math-report/{course_id}/view` as a primary learning step
- global `ocr_math_report.json`
- global `ocr_math_report.md`
- `figures_hybrid`
- `figures.html`
- old `edit-crops` shrink controls
- preview-only crop as a substitute for real crop artifact

These may remain temporarily as owner-local technical diagnostics until replaced.

## Required implementation sequence after this plan

Recommended next milestones:

1. `v0.8.66-owner-local-hide-deprecated-visual-ocrmath-user-links-no-share-no-delivery`
2. `v0.8.67-owner-local-bbox-visual-item-contract-no-share-no-delivery`
3. `v0.8.68-owner-local-real-crop-artifact-from-bbox-no-share-no-delivery`
4. `v0.8.69-owner-local-ocrmath-on-crop-candidate-no-share-no-delivery`
5. `v0.8.70-owner-local-manual-validation-to-clean-study-gate-no-share-no-delivery`

## Policy

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No crop generation.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
