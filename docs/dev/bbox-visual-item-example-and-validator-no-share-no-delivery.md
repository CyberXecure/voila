# v0.8.68 BBox visual item example and validator — no share/no delivery

## Purpose

This milestone adds a tracked local example and standalone validator for the canonical bbox visual item contract.

It does not generate crops.

It does not run OCR Math.

It does not change web routes.

It does not change Study or Progress.

## Added files

- `docs/dev/fixtures/bbox-visual-items/visual_items.bbox.example.json`
- `scripts/dev/validate-bbox-visual-items.py`
- `scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.py`
- `scripts/dev/check-bbox-visual-item-example-and-validator-no-share-no-delivery.ps1`

## Contract validated

The validator checks:

- required top-level fields;
- required item fields;
- allowed `kind` values;
- allowed `bbox_units` values;
- allowed `ocr_math_status` values;
- allowed `user_decision` values;
- positive page number;
- ordered four-integer bbox;
- unique `item_id`;
- Study gate rules.

## Study gate rules enforced

A visual item may be ready for Study only when:

- `ready_for_study` is `true`;
- `user_decision` is `accept` or `edit`;
- `crop_exists` is `true`;
- `crop_path` is non-empty;
- either OCR Math candidate text or user-corrected text is present;
- edited items have non-empty `user_corrected_text`.

Ignored and pending items must not be ready for Study.

## Policy

Example and validator only.

No server required.

No web route change.

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
