# v0.8.67 BBox visual item contract — no share/no delivery

## Purpose

This milestone defines the canonical local contract for visual learning items.

It is a contract milestone only.

No crop generation is implemented.

No OCR Math on crop is implemented.

No Study integration is implemented.

## Context

v0.8.65 defined the canonical target flow:

`PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study`

v0.8.66 hid deprecated visual/OCR Math links from primary user-facing navigation while preserving technical routes.

v0.8.67 now defines the stable data shape that later milestones must produce and consume.

## Canonical artifact name

Planned canonical artifact:

`formula_visual_evidence/visual_items.bbox.json`

This file is local-only and document-specific.

It belongs under:

`data/output/<course_id>/formula_visual_evidence/visual_items.bbox.json`

## Canonical item shape

```json
{
  "schema_version": "v0.8.67",
  "course_id": "example-course",
  "source_pdf": "example.pdf",
  "items": [
    {
      "item_id": "bbox-item-0001",
      "kind": "formula",
      "page": 3,
      "bbox": [120, 340, 680, 510],
      "bbox_units": "page_pixels",
      "page_image_path": "formula_visual_evidence/pages/page-003.png",
      "crop_path": "formula_visual_evidence/crops/page-003-item-0001.png",
      "crop_exists": false,
      "ocr_math_candidate_text": "",
      "ocr_math_status": "not_run",
      "user_decision": "pending",
      "user_corrected_text": "",
      "user_explanation": "",
      "ready_for_study": false,
      "created_by": "bbox_visual_item_contract",
      "review_notes": ""
    }
  ]
}
```

## Required top-level fields

- `schema_version`
- `course_id`
- `source_pdf`
- `items`

## Required item fields

- `item_id`
- `kind`
- `page`
- `bbox`
- `bbox_units`
- `page_image_path`
- `crop_path`
- `crop_exists`
- `ocr_math_candidate_text`
- `ocr_math_status`
- `user_decision`
- `user_corrected_text`
- `user_explanation`
- `ready_for_study`
- `created_by`
- `review_notes`

## Allowed `kind` values

- `formula`
- `figure`
- `diagram`
- `table`
- `symbol`
- `mixed`
- `unknown`

## Allowed `bbox_units` values

- `page_pixels`
- `pdf_points`

The producing milestone must declare which coordinate system it uses.

## Allowed `ocr_math_status` values

- `not_run`
- `candidate_generated`
- `failed`
- `not_applicable`
- `pending_user_validation`
- `validated_by_user`

## Allowed `user_decision` values

- `pending`
- `accept`
- `edit`
- `ignore`

## Study gate rule

A visual item may enter clean Study only when:

- `ready_for_study` is `true`;
- `user_decision` is `accept` or `edit`;
- `crop_exists` is `true`;
- `crop_path` is present;
- either `ocr_math_candidate_text` or `user_corrected_text` is present;
- if `user_decision` is `edit`, then `user_corrected_text` must be non-empty.

Items with `user_decision=ignore` must never feed Study.

Items with `user_decision=pending` must never feed Study.

## OCR Math rule

OCR Math is not run globally as the user-facing flow.

OCR Math may run only after a bbox/crop exists.

OCR Math output remains a candidate until the user validates it.

## LanguageTool relationship

LanguageTool suggestions belong to OCR text review.

They may reference page and text context.

They must not silently rewrite visual item OCR Math fields.

## User-facing behavior target

The user should see one coherent Review Document workspace.

The user should not see raw artifact names, bbox coordinates, schema IDs, or internal route names in the normal learning flow.

Technical details may remain available under owner-local diagnostics.

## Future implementation sequence

Recommended next milestones:

1. `v0.8.68-owner-local-bbox-visual-item-example-and-validator-no-share-no-delivery`
2. `v0.8.69-owner-local-real-crop-artifact-from-bbox-no-share-no-delivery`
3. `v0.8.70-owner-local-ocrmath-on-crop-candidate-no-share-no-delivery`
4. `v0.8.71-owner-local-manual-visual-validation-gate-no-share-no-delivery`
5. `v0.8.72-owner-local-clean-study-visual-item-ingestion-no-share-no-delivery`

## Policy

Contract only.

No web route change.

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No crop generation.

No OCR Math run.

No Study write.

No Progress write.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
